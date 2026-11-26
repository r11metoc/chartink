"""Does a scan's signal lead to big moves LATER? Tests patient exits.

Usage: python patient_test.py "<Chartink backtest export.csv>"

Part 1 - what happens after each signal (bought at the next open), compared
with the same stocks on random days (x3): return after 20, 60 and 120
sessions, the best gain reached within 120 sessions, and how often a +20% /
+50% run came within 120 sessions.

Part 2 - sell rules that give the trade time (all 0.25% costs, ₹10L / 15 slots):
  ema30        bot rule: close below the 30-day EMA, 15% stop
  ema63        close below the 63-day EMA, 15% stop
  ema30 late   30-day EMA exit only from session 20 on, 15% stop
  trail20      close 20% below the highest close since buying
  trail25      close 25% below the highest close since buying
  hold60       hold 60 sessions, 20% stop
  hold120      hold 120 sessions, 25% stop
  bstop+ema63  buy only if price later trades above the signal day's high (within 10 sessions), then ema63
Writes reports/patient_<file>.md.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone
import scan_quality as sq

ROOT = Path(__file__).resolve().parent.parent
COST = bs.COST_PCT
SPLIT = pd.Timestamp("2023-01-01")
RULES = ["ema30", "ema63", "ema30 late", "trail20", "trail25", "hold60", "hold120", "bstop+ema63"]


def sell(rule, o, h, l, c, e30, e63, e, ep):
    n = len(c)
    stop = ep * {"hold60": 0.80, "hold120": 0.75, "trail20": 0.0, "trail25": 0.0}.get(rule, 0.85)
    hold = {"hold60": 60, "hold120": 120}.get(rule, dipzone.RIDE_MAX_HOLD)
    last, hi = min(n - 1, e + hold), ep
    for i in range(e, last + 1):
        if stop > 0:
            if i > e and o[i] <= stop:
                return (o[i] / ep - 1) * 100 - COST, i
            if l[i] <= stop:
                return (stop / ep - 1) * 100 - COST, i
        hi = max(hi, c[i])
        line = {"ema30": e30[i], "ema30 late": e30[i] if i - e >= 20 else np.nan, "ema63": e63[i],
                "bstop+ema63": e63[i], "trail20": hi * 0.80, "trail25": hi * 0.75}.get(rule, np.nan)
        if i > e and not np.isnan(line) and c[i] < line:
            if i + 1 >= n:
                return None
            return (o[i + 1] / ep - 1) * 100 - COST, i + 1
    if last == e + hold:
        return (c[last] / ep - 1) * 100 - COST, last
    return None


def run(hits: pd.DataFrame, prices: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    trades, fwd, cache = [], [], {}
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] + 1 >= len(df):
            continue
        sp = sig["end_pos"]
        if h["symbol"] not in cache:
            cl = df["Close"]
            cache[h["symbol"]] = (*(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                  dipzone.exit_line(cl), cl.ewm(span=63, adjust=False, min_periods=63).mean().to_numpy())
        o, hi, lo, c, e30, e63 = cache[h["symbol"]]
        e, ep = sp + 1, float(o[sp + 1])
        if e + 120 < len(c):
            seg = hi[e:e + 121]
            fwd.append({"date": df.index[e], **{f"r{k}": (c[e + k] / ep - 1) * 100 for k in (20, 60, 120)},
                        "best": (seg.max() / ep - 1) * 100})
        for r in RULES:
            ee, pp = e, ep
            if r == "bstop+ema63":
                trig = float(hi[sp])
                ee = next((i for i in range(sp + 1, min(len(c), sp + 11)) if hi[i] > trig), None)
                if ee is None:
                    continue
                pp = max(float(o[ee]), trig)
            x = sell(r, o, hi, lo, c, e30, e63, ee, pp)
            if x is None:
                continue
            trades.append({"rule": r, "symbol": h["symbol"], "scanner": "scan", "cap": h["marketcap"],
                           "entry_date": df.index[ee], "exit_date": df.index[x[1]], "ret": x[0], "days": x[1] - ee + 1})
    return pd.DataFrame(trades), pd.DataFrame(fwd)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    path = Path(sys.argv[1])
    hits = sq.load(path)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    t, f = run(hits, prices)
    rr = [run(sq.random_hits(hits, prices, s), prices) for s in (1, 2, 3)]
    rt = pd.concat([x[0] for x in rr], ignore_index=True)
    rf = pd.concat([x[1] for x in rr], ignore_index=True)
    L = [f"# Patient exits: {path.stem}", "", f"{len(hits):,} hits, {hits['symbol'].nunique()} stocks.", "",
         "## 1. What happens after the signal (bought at the next open)", "",
         "| | Signals | After 20 sessions | After 60 | After 120 | Best gain within 120 (median) | Reached +20% | Reached +50% |",
         "|---|---|---|---|---|---|---|---|"]
    for name, x in (("This scan", f), ("This scan 2019-22", f[f["date"] < SPLIT]), ("This scan 2023-26", f[f["date"] >= SPLIT]),
                    ("Same stocks, random days", rf)):
        L.append(f"| {name} | {len(x)} | {x['r20'].mean():+.1f}% | {x['r60'].mean():+.1f}% | {x['r120'].mean():+.1f}% | "
                 f"{x['best'].median():+.1f}% | {(x['best'] >= 20).mean() * 100:.0f}% | {(x['best'] >= 50).mean() * 100:.0f}% |")
    L += ["", "Averages; 'after N' = the close N sessions after buying. If the scan adds nothing, its numbers look like the random row.", "",
          "## 2. Sell rules that give the trade time", "",
          "| Sell rule | Trades | Won | Avg | Avg win / loss | Days | 2019-22 avg | 2023-26 avg | Random days avg | ₹10L, 15 slots: per year | Worst fall |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in RULES:
        g, gr = t[t["rule"] == r], rt[rt["rule"] == r]
        if g.empty:
            continue
        w, ls = g[g["ret"] > 0]["ret"], g[g["ret"] <= 0]["ret"]
        eq = dipzone.portfolio(g)["equity"]
        yrs = (eq.index[-1] - eq.index[0]).days / 365.25
        cagr = ((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1) * 100
        L.append(f"| {r} | {len(g)} | {(g['ret'] > 0).mean() * 100:.0f}% | {g['ret'].mean():+.2f}% | "
                 f"{w.mean():+.1f}% / {ls.mean():+.1f}% | {g['days'].mean():.0f} | "
                 f"{g[g['entry_date'] < SPLIT]['ret'].mean():+.2f}% | {g[g['entry_date'] >= SPLIT]['ret'].mean():+.2f}% | "
                 f"{gr['ret'].mean():+.2f}% | {cagr:.1f}% | {(eq / eq.cummax() - 1).min() * 100:.1f}% |")
    best = t.groupby("rule")["ret"].mean().idxmax()
    g = t[t["rule"] == best]
    L += ["", f"## By year ({best})", "", "| Year | Trades | Won | Avg |", "|---|---|---|---|"]
    for y, gy in g.groupby(g["entry_date"].dt.year):
        L.append(f"| {y} | {len(gy)} | {(gy['ret'] > 0).mean() * 100:.0f}% | {gy['ret'].mean():+.2f}% |")
    top = g.sort_values("ret", ascending=False)
    share = top.head(max(1, len(top) // 20))["ret"].sum() / max(g["ret"].sum(), 1e-9) * 100
    L += ["", f"Best 5% of trades = {share:.0f}% of the total profit (over 100% means the rest lose money together)."]
    text = "\n".join(L) + "\n"
    out = ROOT / "reports" / f"patient_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
