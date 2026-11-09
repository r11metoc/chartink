"""How long should a buy-stop stay open? Backtest of the live rule with longer
entry windows (daily scanners 3 / 6 / 10 sessions, weekly 5 / 10 / 15).

Everything else is the live rule: buy when the price trades above the trigger
(filled at the trigger, or the open on a gap-up), 12% stop (15% weekly), sell
after a close below the 50-day average, filters as live, 15 slots with the
mid > large > small priority. Writes reports/entry_window_test.md.

Run on GitHub Actions (needs Yahoo): Scanner signal model -> mode=window_test.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

import breakout_sim as bs
import dipzone as dz
from market_data import fetch_daily
from stock_outcomes import load_hits

REPORT = Path(__file__).resolve().parent.parent / "reports" / "entry_window_test.md"
WINDOWS = [(3, 5), (6, 10), (10, 15)]  # (daily, weekly) sessions; first = live


def trades_for(hits, prices, daily: int, weekly: int) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        weekly_sc = bs.is_weekly(h["scanner_name"])
        sig = bs.signal_bar(df, h["hit_date"], weekly_sc) if df is not None else None
        if sig is None or not dz.passes_filter(h["scanner_name"], dz.dist_52w_high(df, sig["end_pos"]),
                                                dz.atr_pct(df, sig["end_pos"])):
            continue
        sp, trig = sig["end_pos"], sig["trigger"]
        hi, op = df["High"].to_numpy(dtype=float), df["Open"].to_numpy(dtype=float)
        win = weekly if weekly_sc else daily
        b = next((i for i in range(sp + 1, min(len(df), sp + 1 + win)) if hi[i] > trig), None)
        if b is None:
            continue
        px = max(op[b], trig)
        x = dz.ride(df, b, h["scanner_name"], "ma50", ep=px)
        if x:
            rows.append({"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                         "hit_date": pd.Timestamp(h["hit_date"]), "entry_date": df.index[b], "entry": px,
                         "day": b - sp, **x})
    return pd.DataFrame(rows)


def stats(t: pd.DataFrame, start, end=None) -> dict:
    t = t[(t["entry_date"] >= start) & ((t["entry_date"] < end) if end is not None else True)]
    pf = dz.portfolio(t)
    eq = pf["equity"]
    r = t["ret"]
    return {"trades": len(t), "win": (r > 0).mean() * 100, "avg": r.mean(), "taken": len(pf["taken"]),
            "cagr": dz._cagr(pf["capital"], eq.iloc[-1], eq.index[0], eq.index[-1]),
            "dd": (eq / eq.cummax() - 1).min() * 100, "final": eq.iloc[-1]}


def main() -> int:
    hits = load_hits()
    hits = hits[hits["source"] == "backtest"] if "source" in hits else hits
    start = (hits["hit_date"].min() - timedelta(days=420)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    res = {w: trades_for(hits, prices, *w) for w in WINDOWS}
    live = res[WINDOWS[0]]
    begin = live.groupby("scanner")["entry_date"].min().max()
    L = ["# Entry window test", "",
         "How long a buy-stop stays open after the signal. Live rule otherwise; 15 slots, ₹10L, "
         f"from {begin.date()} (all three scanners live). Trades still open are left out.", ""]
    periods = [("All years", begin, None), ("2019-22", begin, pd.Timestamp("2023-01-01")),
               ("2023-26", pd.Timestamp("2023-01-01"), None)]
    for name, a, b in periods:
        L += [f"## {name}", "", "| Window (daily / weekly) | Signals bought | Win | Avg trade | Trades taken (15 slots) | Yearly return | Worst fall | ₹10L became |",
              "|---|---|---|---|---|---|---|---|"]
        for w in WINDOWS:
            s = stats(res[w], a, b)
            L.append(f"| {w[0]} / {w[1]} sessions{' (live)' if w == WINDOWS[0] else ''} | {s['trades']} | {s['win']:.0f}% | "
                     f"{s['avg']:+.1f}% | {s['taken']} | {s['cagr']:.1f}% | {s['dd']:.1f}% | ₹{s['final'] / 1e5:.1f}L |")
        L.append("")
    L += ["## The extra buys on their own", "",
          "Trades a longer window adds (bought after the live window closed):", "",
          "| Window | Extra buys | Win | Avg trade |", "|---|---|---|---|"]
    for w in WINDOWS[1:]:
        t = res[w]
        lim = t["scanner"].map(lambda s: WINDOWS[0][1] if bs.is_weekly(s) else WINDOWS[0][0])
        late = t[(t["day"] > lim) & (t["entry_date"] >= begin)]
        if len(late):
            L.append(f"| {w[0]} / {w[1]} | {len(late)} | {(late['ret'] > 0).mean() * 100:.0f}% | {late['ret'].mean():+.1f}% |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
