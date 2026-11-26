"""Rework the buy and sell rules: every combination on the bot's own scanners.

Usage: python rule_lab.py [backtest_dir]      (default data/backtest)

Takes every hit of the scanners in data/backtest/*.csv (the files the bot
uses), applies the bot's filters (weekly ATR < 4%, 63/30 near the high), and
trades them with each BUY rule x each SELL rule. Every combination is run as
the bot runs: ₹10L, 15 slots shared by all scanners, one position per stock,
0.25% costs. A combination only counts as better if it beats the current rule
in BOTH halves (2019-22 and 2023-26) without a deeper worst fall.

BUY rules
  stop3  current: buy-stop at the signal candle's high for 3 sessions (5 weekly)
  stop1  buy-stop for the next session only
  open   buy at the next open after the signal candle (no trigger)
  pull   buy at the next open only if it opens no more than 2% above the close

SELL rules (all keep a hard stop and sell after 250 sessions at the latest)
  ema30   current: next open after a close below the 30-day EMA, 15% stop
  ema20   close below the 20-day EMA, 10% stop
  ema30t  ema30 with an 8% stop
  time    ema30, and sell after 15 sessions if not at least +3% by then
  half    sell half at +10%, the rest by ema30 (stop moves to cost after +10%)
  atr3    trailing: close below the highest close since entry minus 3 x ATR(14)
  trail20 trailing: close 20% below the highest close since entry
  t5      +5% target, 15% stop, 40 sessions (high win rate)

Writes reports/rule_lab.md and prints it.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone

ROOT = Path(__file__).resolve().parent.parent
BUYS = ["stop3", "stop1", "open", "pull"]
SELLS = ["ema30", "ema20", "ema30t", "time", "half", "atr3", "trail20", "t5"]
COST = bs.COST_PCT
HALVES = [("2019-01-01", "2023-01-01"), ("2023-01-01", "2100-01-01")]


def entry(rule: str, o, h, c, sp: int, trigger: float, window: int) -> tuple[int, float] | None:
    n = len(o)
    if rule in ("stop3", "stop1"):
        w = window if rule == "stop3" else 1
        for i in range(sp + 1, min(n, sp + 1 + w)):
            if h[i] > trigger:
                return i, max(float(o[i]), trigger)
        return None
    if sp + 1 >= n:
        return None
    if rule == "pull" and o[sp + 1] > c[sp] * 1.02:
        return None
    return sp + 1, float(o[sp + 1])


def exit_(rule: str, o, h, l, c, ema20, ema30, atr, e: int, ep: float) -> tuple[float, int] | None:
    """(return %, exit bar) or None while still open."""
    n = len(c)
    stop = ep * (1 - {"ema20": 0.10, "ema30t": 0.08}.get(rule, 0.15))
    last = min(n - 1, e + (40 if rule == "t5" else dipzone.RIDE_MAX_HOLD))
    hi_close, half_done, banked = ep, False, 0.0

    def done(px, i):
        r = px / ep - 1
        if half_done:
            r = (banked + r) / 2
        return r * 100 - COST, i

    for i in range(e, last + 1):
        if i > e and o[i] <= stop:
            return done(float(o[i]), i)
        if l[i] <= stop:
            return done(stop, i)
        if rule == "t5" and h[i] >= ep * 1.05:
            return done(max(float(o[i]), ep * 1.05) if i > e else ep * 1.05, i)
        if rule == "half" and not half_done and h[i] >= ep * 1.10:
            half_done, banked = True, 0.10 if (i == e or o[i] < ep * 1.10) else float(o[i]) / ep - 1
            stop = max(stop, ep)
        hi_close = max(hi_close, c[i])
        line = None
        if rule in ("ema30", "ema30t", "time", "half"):
            line = ema30[i]
        elif rule == "ema20":
            line = ema20[i]
        elif rule == "atr3" and not np.isnan(atr[i]):
            line = hi_close - 3 * atr[i]
        elif rule == "trail20":
            line = hi_close * 0.8
        sell = i > e and line is not None and not np.isnan(line) and c[i] < line
        if rule == "time" and i - e == 15 and c[i] < ep * 1.03:
            sell = True
        if sell:
            if i + 1 >= n:
                return None
            return done(float(o[i + 1]), i + 1)
    if last == e + (40 if rule == "t5" else dipzone.RIDE_MAX_HOLD):
        return done(float(c[last]), last)
    return None


def all_trades(hits: pd.DataFrame, prices: dict) -> pd.DataFrame:
    rows, cache = [], {}
    for _, hh in hits.iterrows():
        df = prices.get(hh["symbol"])
        sc = hh["scanner_name"]
        sig = bs.signal_bar(df, hh["hit_date"], bs.is_weekly(sc)) if df is not None else None
        if sig is None:
            continue
        sp = sig["end_pos"]
        if not dipzone.passes_filter(sc, dipzone.dist_52w_high(df, sp), dipzone.atr_pct(df, sp)):
            continue
        if hh["symbol"] not in cache:
            c = df["Close"]
            tr = pd.concat([df["High"] - df["Low"], (df["High"] - c.shift()).abs(), (df["Low"] - c.shift()).abs()], axis=1).max(axis=1)
            cache[hh["symbol"]] = (*(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                   c.ewm(span=20, adjust=False, min_periods=20).mean().to_numpy(),
                                   dipzone.exit_line(c), tr.rolling(14).mean().to_numpy())
        o, h, l, c, e20, e30, atr = cache[hh["symbol"]]
        for b in BUYS:
            en = entry(b, o, h, c, sp, sig["trigger"], bs.entry_window_for(sc))
            if en is None:
                continue
            e, ep = en
            for s in SELLS:
                x = exit_(s, o, h, l, c, e20, e30, atr, e, ep)
                if x is None:
                    continue
                rows.append({"buy": b, "sell": s, "scanner": sc, "symbol": hh["symbol"], "cap": hh["marketcap"],
                             "entry_date": df.index[e], "exit_date": df.index[x[1]], "ret": x[0],
                             "days": x[1] - e + 1})
    return pd.DataFrame(rows)


def _cagr(eq, a, b):
    x = eq[(eq.index >= pd.Timestamp(a)) & (eq.index < pd.Timestamp(b))]
    if len(x) < 2:
        return np.nan
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    return ((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100 if yrs > 0 else np.nan


def evaluate(t: pd.DataFrame) -> pd.DataFrame:
    start = t.groupby("scanner")["entry_date"].min().max()
    out = []
    for (b, s), g in t[t["entry_date"] >= start].groupby(["buy", "sell"]):
        eq = dipzone.portfolio(g)["equity"]
        out.append({"buy": b, "sell": s, "trades": len(g), "win": (g["ret"] > 0).mean() * 100, "avg": g["ret"].mean(),
                    "days": g["days"].mean(), "cagr": _cagr(eq, "2000-01-01", "2100-01-01"),
                    "h1": _cagr(eq, *HALVES[0]), "h2": _cagr(eq, *HALVES[1]),
                    "dd": (eq / eq.cummax() - 1).min() * 100,
                    "y2025": _cagr(eq, "2025-01-01", "2100-01-01")})
    return pd.DataFrame(out).sort_values("cagr", ascending=False)


def report(res: pd.DataFrame, n_hits: int) -> str:
    cur = res[(res["buy"] == "stop3") & (res["sell"] == "ema30")].iloc[0]
    res = res.assign(better=(res["h1"] > cur["h1"]) & (res["h2"] > cur["h2"]) & (res["dd"] >= cur["dd"] - 1))
    L = ["# Buy and sell rules reworked", "",
         f"{n_hits:,} hits of the bot's scanners (data/backtest), ₹10L, 15 slots shared, one position per stock, "
         "0.25% costs. 'Better' = beats the current rule (stop3 + ema30) in both 2019-22 and 2023-26 with a worst "
         "fall no more than 1 point deeper.", "",
         "| Buy | Sell | Trades | Won | Avg | Days | Per year | 2019-22 | 2023-26 | 2025-26 | Worst fall | Better? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res.iterrows():
        mark = "**current**" if (r["buy"], r["sell"]) == ("stop3", "ema30") else ("✓" if r["better"] else "")
        L.append(f"| {r['buy']} | {r['sell']} | {r['trades']} | {r['win']:.0f}% | {r['avg']:+.2f}% | {r['days']:.0f} | "
                 f"{r['cagr']:.1f}% | {r['h1']:.1f}% | {r['h2']:.1f}% | {r['y2025']:.1f}% | {r['dd']:.1f}% | {mark} |")
    best = res[res["better"]]
    L += ["", "Best combination that passes: " + (f"buy {best.iloc[0]['buy']}, sell {best.iloc[0]['sell']}"
                                                  if len(best) else "none: keep the current rule.")]
    hw = res[res["win"] >= 70].sort_values("cagr", ascending=False)
    if len(hw):
        r = hw.iloc[0]
        L.append(f"Best with a 70%+ win rate: buy {r['buy']}, sell {r['sell']}: {r['win']:.0f}% won, "
                 f"{r['cagr']:.1f}% a year, worst fall {r['dd']:.1f}%.")
    return "\n".join(L) + "\n"


def main() -> int:
    from hits import load_hits
    from market_data import fetch_daily
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "backtest"
    hits = load_hits(d)
    hits = hits[hits["source"] == "backtest"]   # lab = the exports only (live triggers carry other scanner names)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    print(f"{len(hits)} hits, fetching prices since {start}…")
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    t = all_trades(hits, prices)
    text = report(evaluate(t), len(hits))
    out = ROOT / "reports" / f"rule_lab_{d.name}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
