"""Wkly_upswing: buy at once, or wait (and how long) for the price to cross the trigger?

Weekly signals under the live exit (sell at the next open after a close below
the 30-day EMA, 15% stop, at most 250 sessions), with different entries:
  - next open: buy at the first open after the signal week, no trigger;
  - buy-stop at the trigger (the signal week's high) valid 5 (live), 10 or 20 sessions;
each with and without the 4% daily-ATR filter. Shown for the weekly trades on
their own, and for the whole ₹10L / 15-slot portfolio with the daily scanners
on the live rule. Writes reports/weekly_test.md. Run on GitHub (Yahoo):
signal_model mode=weekly_test.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone as dz
from market_data import fetch_daily
from stock_outcomes import load_hits

REPORT = Path(__file__).resolve().parent.parent / "reports" / "weekly_test.md"
ENTRIES = [("Buy-stop 5 sessions (live)", "stop", 5), ("Buy-stop 10 sessions", "stop", 10),
           ("Buy-stop 20 sessions", "stop", 20), ("Buy at next open (no trigger)", "open", 0)]


def ride(df, b, ep) -> tuple | None:
    o, lo, c = (df[k].to_numpy(dtype=float) for k in ("Open", "Low", "Close"))
    ma = dz.exit_line(df["Close"])
    stop = ep * (1 - dz.STOP_PCT / 100)
    n, last = len(c), min(len(c) - 1, b + 250)
    for i in range(b, last + 1):
        if i > b and o[i] <= stop:
            return o[i], i
        if lo[i] <= stop:
            return stop, i
        if i > b and not np.isnan(ma[i]) and c[i] < ma[i]:
            return (o[i + 1], i + 1) if i + 1 < n else None
    return (c[last], last) if b + 250 <= n - 1 else None


def trades(hits, prices, kind, window, atr_filter, scanner) -> pd.DataFrame:
    rows = []
    for _, h in hits[hits["scanner_name"] == scanner].iterrows():
        df = prices.get(h["symbol"])
        wk = bs.is_weekly(scanner)
        sig = bs.signal_bar(df, h["hit_date"], wk) if df is not None else None
        if sig is None:
            continue
        sp, trig = sig["end_pos"], sig["trigger"]
        dist = dz.dist_52w_high(df, sp)
        if scanner == "63_30_daily" and dist is not None and dist < -10:
            continue
        if atr_filter and wk:
            a = dz.atr_pct(df, sp)
            if a is not None and a >= 4.0:
                continue
        o, hi = df["Open"].to_numpy(dtype=float), df["High"].to_numpy(dtype=float)
        if kind == "open":
            b = sp + 1 if sp + 1 < len(df) else None
            ep = o[b] if b is not None else None
        else:
            b = next((i for i in range(sp + 1, min(len(df), sp + 1 + window)) if hi[i] > trig), None)
            ep = max(o[b], trig) if b is not None else None
        if b is None:
            continue
        x = ride(df, b, ep)
        if x is None:
            continue
        rows.append({"scanner": scanner, "symbol": h["symbol"], "cap": h["marketcap"],
                     "entry_date": df.index[b], "exit_date": df.index[x[1]], "days": x[1] - b + 1,
                     "ret": round((x[0] / ep - 1) * 100 - bs.COST_PCT, 2)})
    return pd.DataFrame(rows)


def main() -> int:
    hits = load_hits()
    hits = hits[hits["source"] == "backtest"] if "source" in hits else hits
    start = (hits["hit_date"].min() - timedelta(days=420)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    daily = pd.concat([trades(hits, prices, "stop", 3, True, s) for s in ("63_30_daily", "Bullish_Scanner")])
    n_sig = int((hits["scanner_name"] == "Wkly_upswing").sum())
    L = ["# Wkly_upswing: buy at once or wait for the trigger?", "",
         f"{n_sig} weekly signals in the backtest exports. Live exit for all (30-day EMA, 15% stop, 250 sessions), "
         "after 0.25% costs. Trades still open are left out.", ""]
    begin = daily.groupby("scanner")["entry_date"].min().max()
    for atr in (True, False):
        L += [f"## {'With' if atr else 'Without'} the 4% volatility filter", "",
              "| Entry | Weekly trades | Win | Avg | Avg win / loss | Days | 2019-22 avg | 2023-26 avg | Portfolio per year | Worst fall |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for name, kind, win in ENTRIES:
            w = trades(hits, prices, kind, win, atr, "Wkly_upswing")
            r = w["ret"]
            a1 = w[w["entry_date"] < "2023-01-01"]["ret"].mean()
            a2 = w[w["entry_date"] >= "2023-01-01"]["ret"].mean()
            pf = dz.portfolio(pd.concat([daily, w])[lambda t: t["entry_date"] >= begin])
            eq = pf["equity"]
            L.append(f"| {name} | {len(w)} | {(r > 0).mean() * 100:.0f}% | {r.mean():+.2f}% | "
                     f"{r[r > 0].mean():+.1f}% / {r[r <= 0].mean():.1f}% | {w['days'].mean():.0f} | {a1:+.2f}% | {a2:+.2f}% | "
                     f"{dz._cagr(pf['capital'], eq.iloc[-1], eq.index[0], eq.index[-1]):.1f}% | {(eq / eq.cummax() - 1).min() * 100:.1f}% |")
        L.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
