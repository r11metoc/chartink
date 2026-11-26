"""Can Bullish_Scanner's trades be made better by the bot's own rules?

Usage: python bullish_improve.py [lab_dir]     (default local/L1_base)

Uses the lab folder's three scanners (Bullish with the weekly-RSI look-ahead
removed, 63_30 x4, Wkly_upswing), buys at the next open, and sells two ways:
the live rule (close below the 30-day EMA, 15% stop) and +5% target / 15% stop.
Each variant changes ONLY what the bot does with Bullish_Scanner signals:

  base           as today
  no_weak        skip Bullish signals in Bank, Media, Textiles
  pullback_1st   Bullish signals 5-10% below the 52-week high get free slots first
  rsi75          only Bullish signals with daily RSI(14) above 75
  no_weak+pb     no_weak and pullback_1st together
  no_weak+rsi75  no_weak and rsi75 together
  pullback_only  only Bullish signals 5-10% below the 52-week high

'Better' = beats base in BOTH 2019-22 and 2023-26, worst fall no more than 1
point deeper. Writes reports/bullish_improve.md and prints it.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import condition_check as cc
import dipzone
import rule_lab as rl

ROOT = Path(__file__).resolve().parent.parent
WEAK = {"bank", "media", "textiles"}
BULL = "Bullish_Scanner"


def add_features(t: pd.DataFrame, hits: pd.DataFrame, prices: dict) -> pd.DataFrame:
    sec = hits[hits["scanner_name"] == BULL].drop_duplicates("symbol", keep="last").set_index("symbol")["sector"]
    dist, rsi = [], []
    rsi_cache = {}
    for sym, ed in zip(t["symbol"], t["entry_date"]):
        df = prices[sym]
        sp = int(df.index.get_loc(ed)) - 1          # signal bar = the session before the next-open buy
        dist.append(dipzone.dist_52w_high(df, sp))
        if sym not in rsi_cache:
            rsi_cache[sym] = cc._rsi(df["Close"]).to_numpy()
        rsi.append(float(rsi_cache[sym][sp]))
    return t.assign(sector=t["symbol"].map(sec).fillna("").str.lower(),
                    dist=pd.to_numeric(pd.Series(dist, index=t.index), errors="coerce"), rsi=rsi)


def variant(t: pd.DataFrame, name: str) -> pd.DataFrame:
    b = t["scanner"] == BULL
    weak = b & t["sector"].isin(WEAK)
    band = b & t["dist"].between(-10, -5)
    if name in ("no_weak", "no_weak+pb", "no_weak+rsi75"):
        t = t[~weak]
        b, band = t["scanner"] == BULL, (t["scanner"] == BULL) & t["dist"].between(-10, -5)
    if name in ("rsi75", "no_weak+rsi75"):
        t = t[~((t["scanner"] == BULL) & (t["rsi"] <= 75))]
    if name == "pullback_only":
        t = t[~(b & ~band)]
    if name in ("pullback_1st", "no_weak+pb"):
        band = (t["scanner"] == BULL) & t["dist"].between(-10, -5)
        capp = t["cap"].map(dipzone.CAP_PRIORITY).fillna(3)
        t = t.assign(ml=band.astype(float) * 10 + (3 - capp))   # band first, then the usual cap order
    return t


def stats(g: pd.DataFrame, start) -> dict:
    g = g[g["entry_date"] >= start]
    eq = dipzone.portfolio(g)["equity"]
    bb = g[g["scanner"] == BULL]
    return {"bull_trades": len(bb), "bull_win": (bb["ret"] > 0).mean() * 100, "bull_avg": bb["ret"].mean(),
            "all_win": (g["ret"] > 0).mean() * 100,
            "cagr": rl._cagr(eq, "2000-01-01", "2100-01-01"), "h1": rl._cagr(eq, *rl.HALVES[0]),
            "h2": rl._cagr(eq, *rl.HALVES[1]), "y2025": rl._cagr(eq, "2025-01-01", "2100-01-01"),
            "dd": (eq / eq.cummax() - 1).min() * 100}


def main() -> int:
    from hits import load_hits
    from market_data import fetch_daily
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "local" / "L1_base"
    hits = load_hits(d)
    hits = hits[hits["source"] == "backtest"]
    start_px = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    print(f"{len(hits)} hits, fetching prices since {start_px}…")
    prices = fetch_daily(sorted(hits["symbol"].unique()), start_px)
    rl.BUYS, rl.SELLS = ["open"], ["ema30", "t5"]
    t = add_features(rl.all_trades(hits, prices), hits, prices)
    start = t.groupby("scanner")["entry_date"].min().max()
    names = ["base", "no_weak", "pullback_1st", "rsi75", "no_weak+pb", "no_weak+rsi75", "pullback_only"]
    L = ["# Improving Bullish_Scanner inside the bot", "",
         f"Lab: {d.name}. ₹10L, 15 slots shared by the three scanners, buy at the next open, 0.25% costs. "
         "Only Bullish signals are changed; 'Bullish won / avg' are its own trades, the rest is the whole bot.", ""]
    for sell, label in (("ema30", "Sell below the 30-day EMA (live rule)"), ("t5", "+5% target, 15% stop")):
        g = t[t["sell"] == sell]
        rows = {n: stats(variant(g, n), start) for n in names}
        base = rows["base"]
        L += [f"## {label}", "",
              "| Variant | Bullish trades | Bullish won | Bullish avg | Bot won | Per year | 2019-22 | 2023-26 | 2025-26 | Worst fall | Better? |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for n, r in rows.items():
            better = n != "base" and r["h1"] > base["h1"] and r["h2"] > base["h2"] and r["dd"] >= base["dd"] - 1
            L.append(f"| {n} | {r['bull_trades']} | {r['bull_win']:.0f}% | {r['bull_avg']:+.2f}% | {r['all_win']:.0f}% | "
                     f"{r['cagr']:.1f}% | {r['h1']:.1f}% | {r['h2']:.1f}% | {r['y2025']:.1f}% | {r['dd']:.1f}% | "
                     f"{'base' if n == 'base' else ('✓' if better else '')} |")
        L.append("")
    text = "\n".join(L)
    out = ROOT / "reports" / "bullish_improve.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
