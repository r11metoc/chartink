"""Signal candle, trigger and point-in-time features for scanner signals.

- **Signal bar**: the candle that made the scanner fire. For the daily
  scanners that's the hit date's daily candle. For the weekly scanner
  Chartink dates each hit by the *first trading day of the week*, but the
  condition is evaluated on the completed weekly candle, so the signal is
  only known after that week's last session (using the Monday would peek at
  the rest of the week).
- **Trigger**: the high of the signal bar. The buy-stop stays open for the
  next 3 sessions (5 after a weekly signal); filled at the trigger, or at
  the open on a gap-up.
- **Features** (for the ML ranker): only bars up to and including the
  signal bar.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DAILY_ENTRY_WINDOW = 3   # sessions a buy-stop stays open after a daily signal
WEEKLY_ENTRY_WINDOW = 5  # after a weekly signal
COST_PCT = 0.25            # round-trip brokerage + taxes + slippage, in %

WEEKLY_SCANNERS = {"Wkly_upswing"}


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


def find_entry(opens: np.ndarray, highs: np.ndarray, trigger: float, window: int) -> tuple[int, float] | None:
    """First bar (0-based within the forward path) whose high crosses the
    trigger, and the fill price."""
    for i in range(min(window, len(highs))):
        if highs[i] > trigger:
            return i, max(float(opens[i]), trigger)
    return None


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
    # Zero-volume or zero-price bars in old data give inf; the model imputes NaN.
    return f.replace([np.inf, -np.inf], np.nan)


FEATURE_COLUMNS = [
    "ret_1d", "ret_5d", "ret_20d", "ret_60d",
    "dist_sma20", "dist_sma50", "dist_sma200",
    "rsi14", "atr_pct", "vol_ratio", "dist_52w_high", "log_turnover", "up_days_10",
    "bar_range_pct", "close_pos_in_bar", "trigger_gap_pct", "bar_risk_pct",
    "nifty_ret_20d", "nifty_dist_sma50",
]


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
