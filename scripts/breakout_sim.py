"""Trade simulation and point-in-time features for scanner signals.

The trading rule being evaluated ("buy when it crosses above the trigger
price"):

- **Signal bar**: the candle that made the scanner fire. For the daily
  scanners that's the hit date's daily candle. For the weekly scanner
  Chartink dates each hit by the *first trading day of the week*, but the
  condition is evaluated on the completed weekly candle, so the signal is
  only known after that week's last session. Treating the Monday date as
  the entry day would peek at the rest of the week (the old 5-day report
  showed an impossible +11.7% average for Wkly_upswing because of this).
- **Trigger price**: the high of the signal bar.
- **Entry**: a stop-buy at the trigger during the next `entry_window`
  sessions. Filled at the trigger, or at the open if the stock gaps above
  it. No cross within the window -> no trade.
- **Exit**: stop at the signal bar's low (risk capped at `max_risk_pct`),
  target at `target_r` times the risk, otherwise out at the close after
  `max_hold` sessions. When a bar touches both stop and target the stop is
  assumed to come first, and a stop touched on the entry day counts, so
  results lean pessimistic rather than optimistic. With `trail_pct` the
  stop also ratchets up to that % below the highest close since entry.

Everything here is pure pandas/numpy so it can be tested without network.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

DAILY_ENTRY_WINDOW = 3
WEEKLY_ENTRY_WINDOW = 5
FORWARD_DAYS = 70          # sessions stored after the signal bar (12 weeks after a late entry)
COST_PCT = 0.25            # round-trip brokerage + taxes + slippage, in %

WEEKLY_SCANNERS = {"Wkly_upswing"}


@dataclass(frozen=True)
class ExitRule:
    max_risk_pct: float = 8.0   # stop never further than this below entry
    min_risk_pct: float = 2.0   # ...nor closer than this (avoids noise stops)
    target_r: float = 2.0       # target = entry + target_r * risk; 0 disables
    max_hold: int = 20          # sessions after entry, then exit at close
    trail_pct: float = 0.0      # >0: after each close, raise the stop to this % below the highest close


DEFAULT_RULE = ExitRule()


def is_weekly(scanner_name: str) -> bool:
    return scanner_name in WEEKLY_SCANNERS


def entry_window_for(scanner_name: str) -> int:
    return WEEKLY_ENTRY_WINDOW if is_weekly(scanner_name) else DAILY_ENTRY_WINDOW


def signal_bar(df: pd.DataFrame, hit_date: pd.Timestamp, weekly: bool,
               require_complete: bool = True) -> dict | None:
    """Locate the signal bar for a hit. Returns positions and levels, or
    None if the price data doesn't cover the hit date.

    `end_pos` is the index of the last daily bar inside the signal bar, i.e.
    the first moment the signal was knowable. With `require_complete` a
    weekly bar only counts once a later session exists (the week closed);
    live prediction passes False to use the week-to-date bar."""
    idx = df.index
    if weekly:
        week_start = hit_date - pd.Timedelta(days=hit_date.weekday())
        week_end = week_start + pd.Timedelta(days=6)
        mask = (idx >= week_start) & (idx <= week_end)
        positions = np.flatnonzero(mask)
        if len(positions) == 0:
            return None
        start_pos, end_pos = int(positions[0]), int(positions[-1])
        if require_complete and end_pos + 1 >= len(df) and idx[end_pos].weekday() < 4:
            return None  # week still in progress
    else:
        if hit_date not in idx:
            return None
        start_pos = end_pos = int(idx.get_loc(hit_date))

    bar = df.iloc[start_pos:end_pos + 1]
    return {
        "start_pos": start_pos,
        "end_pos": end_pos,
        "signal_date": idx[end_pos],
        "trigger": float(bar["High"].max()),
        "bar_low": float(bar["Low"].min()),
        "bar_close": float(bar["Close"].iloc[-1]),
    }


def stop_and_target(entry: float, bar_low: float, rule: ExitRule = DEFAULT_RULE) -> tuple[float, float]:
    risk_pct = (entry - bar_low) / entry * 100
    risk_pct = min(max(risk_pct, rule.min_risk_pct), rule.max_risk_pct)
    stop = entry * (1 - risk_pct / 100)
    target = entry * (1 + rule.target_r * risk_pct / 100) if rule.target_r > 0 else float("inf")
    return stop, target


def find_entry(opens: np.ndarray, highs: np.ndarray, trigger: float, window: int) -> tuple[int, float] | None:
    """First bar (0-based within the forward path) whose high crosses the
    trigger, and the fill price."""
    for i in range(min(window, len(highs))):
        if highs[i] > trigger:
            return i, max(float(opens[i]), trigger)
    return None


def simulate_trade(path: pd.DataFrame, trigger: float, bar_low: float, window: int,
                   rule: ExitRule = DEFAULT_RULE) -> dict:
    """Run the entry/exit rule over the bars *after* the signal bar.

    Returns a dict with `status` 'triggered', 'not_triggered' or 'pending'
    (window not over yet / trade still open), plus trade fields."""
    o, h, l, c = (path[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    entry = find_entry(o, h, trigger, window)
    if entry is None:
        return {"status": "pending" if len(path) < window else "not_triggered"}

    e_i, e_px = entry
    stop, target = stop_and_target(e_px, bar_low, rule)
    initial_stop = stop
    exit_i, exit_px, reason = None, None, None
    last = e_i + rule.max_hold
    for i in range(e_i, min(last + 1, len(path))):
        if i > e_i and o[i] <= stop:
            exit_i, exit_px, reason = i, o[i], "stop_gap"
        elif l[i] <= stop:
            exit_i, exit_px, reason = i, stop, "stop"
        elif i > e_i and o[i] >= target:
            exit_i, exit_px, reason = i, o[i], "target_gap"
        elif h[i] >= target:
            exit_i, exit_px, reason = i, target, "target"
        elif i == last:
            exit_i, exit_px, reason = i, c[i], "time"
        if exit_i is not None:
            break
        if rule.trail_pct > 0:  # takes effect from the next session
            stop = max(stop, c[e_i:i + 1].max() * (1 - rule.trail_pct / 100))

    out = {
        "status": "triggered",
        "entry_offset": e_i,
        "entry_price": e_px,
        "stop": initial_stop,
        "final_stop": stop,
        "target": target,
        "gap_entry": bool(o[e_i] > trigger),
    }
    if exit_i is None:  # still open: mark to the latest close
        out.update(status="pending", exit_offset=len(path) - 1, exit_price=c[-1], exit_reason="open")
    else:
        out.update(exit_offset=exit_i, exit_price=float(exit_px), exit_reason=reason)
    risk = e_px - initial_stop
    out["ret_pct"] = (out["exit_price"] / e_px - 1) * 100 - COST_PCT
    out["r_multiple"] = (out["exit_price"] - e_px) / risk if risk > 0 else 0.0
    out["hold_days"] = out["exit_offset"] - e_i
    return out


# ---------------------------------------------------------------------------
# Features. Every value uses only bars up to and including the signal bar.
# ---------------------------------------------------------------------------

def _rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100)


def indicator_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Per-bar indicators for one symbol's daily OHLCV."""
    c, h, l, v = df["Close"], df["High"], df["Low"], df["Volume"].fillna(0)
    prev_c = c.shift(1)
    tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
    f = pd.DataFrame(index=df.index)
    for n in (1, 5, 20, 60):
        f[f"ret_{n}d"] = (c / c.shift(n) - 1) * 100
    for n in (20, 50, 200):
        f[f"dist_sma{n}"] = (c / c.rolling(n, min_periods=int(n * 0.8)).mean() - 1) * 100
    f["rsi14"] = _rsi(c)
    f["atr_pct"] = tr.rolling(14).mean() / c * 100
    f["vol_ratio"] = v / v.rolling(20).mean().shift(1)
    f["dist_52w_high"] = (c / h.rolling(252, min_periods=120).max() - 1) * 100
    f["log_turnover"] = np.log10((c * v).rolling(20).mean().clip(lower=1))
    f["up_days_10"] = (c > prev_c).rolling(10).sum()
    return f


FEATURE_COLUMNS = [
    "ret_1d", "ret_5d", "ret_20d", "ret_60d",
    "dist_sma20", "dist_sma50", "dist_sma200",
    "rsi14", "atr_pct", "vol_ratio", "dist_52w_high", "log_turnover", "up_days_10",
    "bar_range_pct", "close_pos_in_bar", "trigger_gap_pct", "bar_risk_pct",
    "nifty_ret_20d", "nifty_dist_sma50",
    "prior_hits_same_scanner_180d", "other_scanner_hits_10d",
]
CATEGORICAL_COLUMNS = ["scanner_name", "marketcap", "sector"]


def bar_features(sig: dict) -> dict:
    trig, low, close = sig["trigger"], sig["bar_low"], sig["bar_close"]
    rng = trig - low
    return {
        "bar_range_pct": rng / close * 100,
        "close_pos_in_bar": (close - low) / rng if rng > 0 else 1.0,
        "trigger_gap_pct": (trig / close - 1) * 100,
        "bar_risk_pct": (trig - low) / trig * 100,
    }


def market_features(nifty: pd.DataFrame | None, date: pd.Timestamp) -> dict:
    if nifty is None or nifty.empty:
        return {"nifty_ret_20d": np.nan, "nifty_dist_sma50": np.nan}
    c = nifty["Close"]
    upto = c[c.index <= date]
    if len(upto) < 50:
        return {"nifty_ret_20d": np.nan, "nifty_dist_sma50": np.nan}
    return {
        "nifty_ret_20d": (upto.iloc[-1] / upto.iloc[-21] - 1) * 100,
        "nifty_dist_sma50": (upto.iloc[-1] / upto.iloc[-50:].mean() - 1) * 100,
    }


def history_features(hits: pd.DataFrame) -> pd.DataFrame:
    """Repeat/confluence counts per hit, using only hits already knowable at
    each hit's own signal date. `hits` needs scanner_name, symbol,
    signal_date columns; returns the two count columns aligned to its index."""
    out = pd.DataFrame(index=hits.index, columns=["prior_hits_same_scanner_180d", "other_scanner_hits_10d"],
                       dtype=float)
    for symbol, grp in hits.groupby("symbol"):
        for i, row in grp.iterrows():
            d = row["signal_date"]
            earlier = grp[(grp["signal_date"] <= d) & (grp.index != i)]
            same = earlier[(earlier["scanner_name"] == row["scanner_name"])
                           & (earlier["signal_date"] > d - pd.Timedelta(days=180))
                           & (earlier["signal_date"] < d)]
            other = earlier[(earlier["scanner_name"] != row["scanner_name"])
                            & (earlier["signal_date"] > d - pd.Timedelta(days=10))]
            out.loc[i] = [len(same), len(other)]
    return out
