"""Test a scan with a stop below the signal (trigger) day's low.

Usage: python low_stop_test.py "<Chartink backtest export.csv>"

Every hit is bought at the next open. Sell rules compared (0.25% costs each):

  ema30         your bot rule: next open after a close below the 30-day EMA, 15% stop
  low+ema30     stop at the signal day's low (sold the moment price trades below it),
                otherwise the 30-day EMA exit
  lowclose+ema  sold at the next open after a CLOSE below the signal day's low,
                otherwise the 30-day EMA exit
  low+t5        signal-day-low stop, +5% target, max 40 sessions
  low+t10       signal-day-low stop, +10% target, max 60 sessions
  low+be        signal-day-low stop, moved to cost once +5% is reached, then the 30-day EMA exit
  low only      signal-day-low stop, otherwise held 60 sessions

Each rule is also run on the same stocks on random days (x3) to check the scan
adds anything, and as a ₹10L / 15-slot portfolio. Writes reports/lowstop_<file>.md.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone
import rule_lab as rl
import scan_quality as sq

ROOT = Path(__file__).resolve().parent.parent
COST = bs.COST_PCT
RULES = ["ema30", "low+ema30", "lowclose+ema", "low+t5", "low+t10", "low+be", "low only"]
SPLIT = pd.Timestamp("2023-01-01")


def sell(rule, o, h, l, c, ema, e, ep, low):
    """(return %, exit bar) or None if still open."""
    n = len(c)
    stop = ep * 0.85 if rule == "ema30" else low
    if rule != "ema30" and ep <= low:          # opened at/below the signal low: out at once
        return -COST, e
    hold = {"low+t5": 40, "low+t10": 60, "low only": 60}.get(rule, dipzone.RIDE_MAX_HOLD)
    target = {"low+t5": 1.05, "low+t10": 1.10}.get(rule)
    last = min(n - 1, e + hold)
    for i in range(e, last + 1):
        if rule != "lowclose+ema":
            if i > e and o[i] <= stop:
                return (o[i] / ep - 1) * 100 - COST, i
            if l[i] <= stop:
                return (stop / ep - 1) * 100 - COST, i
        elif l[i] <= ep * 0.85:                # lowclose keeps a 15% emergency stop
            return (min(o[i], ep * 0.85) / ep - 1) * 100 - COST, i
        if target and h[i] >= ep * target:
            px = max(o[i], ep * target) if i > e else ep * target
            return (px / ep - 1) * 100 - COST, i
        if rule == "low+be" and h[i] >= ep * 1.05:
            stop = max(stop, ep)
        out = False
        if rule in ("ema30", "low+ema30", "lowclose+ema", "low+be") and i > e and not np.isnan(ema[i]) and c[i] < ema[i]:
            out = True
        if rule == "lowclose+ema" and c[i] < low:
            out = True
        if out:
            if i + 1 >= n:
                return None
            return (o[i + 1] / ep - 1) * 100 - COST, i + 1
    if last == e + hold:
        return (c[last] / ep - 1) * 100 - COST, last
    return None


def trades(hits: pd.DataFrame, prices: dict) -> pd.DataFrame:
    rows, cache = [], {}
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None:
            continue
        sp = sig["end_pos"]
        if sp + 1 >= len(df):
            continue
        if h["symbol"] not in cache:
            cache[h["symbol"]] = (*(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                  dipzone.exit_line(df["Close"]))
        o, hi, lo, c, ema = cache[h["symbol"]]
        e, ep = sp + 1, float(o[sp + 1])
        for r in RULES:
            x = sell(r, o, hi, lo, c, ema, e, ep, float(lo[sp]))
            if x is None:
                continue
            rows.append({"rule": r, "symbol": h["symbol"], "scanner": "scan", "cap": h["marketcap"],
                         "entry_date": df.index[e], "exit_date": df.index[x[1]], "ret": x[0], "days": x[1] - e + 1,
                         "risk": (ep / lo[sp] - 1) * 100})
    return pd.DataFrame(rows)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    path = Path(sys.argv[1])
    hits = sq.load(path)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    t = trades(hits, prices)
    rnd = pd.concat([trades(sq.random_hits(hits, prices, s), prices) for s in (1, 2, 3)], ignore_index=True)
    risk = t[t["rule"] == "low only"]["risk"]
    L = [f"# Stop below the signal day's low: {path.stem}", "",
         f"{len(hits):,} hits. Bought at the next open. Distance from the buy price down to the signal day's low: "
         f"median {risk.median():.1f}%, 90% of trades under {risk.quantile(0.9):.1f}%.", "",
         "| Sell rule | Trades | Won | Avg | Avg win / loss | Days | 2019-22 avg | 2023-26 avg | Random days avg | ₹10L, 15 slots: per year | Worst fall |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in RULES:
        g, gr = t[t["rule"] == r], rnd[rnd["rule"] == r]
        if g.empty:
            continue
        w, ls = g[g["ret"] > 0]["ret"], g[g["ret"] <= 0]["ret"]
        pf = dipzone.portfolio(g)
        eq = pf["equity"]
        yrs = (eq.index[-1] - eq.index[0]).days / 365.25
        cagr = ((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1) * 100
        dd = (eq / eq.cummax() - 1).min() * 100
        L.append(f"| {r} | {len(g)} | {(g['ret'] > 0).mean() * 100:.0f}% | {g['ret'].mean():+.2f}% | "
                 f"{w.mean():+.1f}% / {ls.mean():+.1f}% | {g['days'].mean():.0f} | "
                 f"{g[g['entry_date'] < SPLIT]['ret'].mean():+.2f}% | {g[g['entry_date'] >= SPLIT]['ret'].mean():+.2f}% | "
                 f"{gr['ret'].mean():+.2f}% | {cagr:.1f}% | {dd:.1f}% |")
    L += ["", "A rule is worth using when its average beats the random-days average clearly, in both periods.",
          "", "## By year (signal-day-low stop + 30-day EMA exit)", "", "| Year | Trades | Won | Avg |", "|---|---|---|---|"]
    g = t[t["rule"] == "low+ema30"]
    for y, gy in g.groupby(g["entry_date"].dt.year):
        L.append(f"| {y} | {len(gy)} | {(gy['ret'] > 0).mean() * 100:.0f}% | {gy['ret'].mean():+.2f}% |")
    text = "\n".join(L) + "\n"
    out = ROOT / "reports" / f"lowstop_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
