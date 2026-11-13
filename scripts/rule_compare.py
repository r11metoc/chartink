"""Backtest of the 13 Nov 2026 rule change, one change at a time.

Old rule: buy-stop 3 sessions (5 weekly), exit on a close below the 50-day
simple average, 12% stop (15% weekly), Wkly_upswing only under 4% daily ATR.
New rule: buy-stop 10 sessions (20 weekly), exit on a close below the 30-day
EMA, 15% stop for all, no volatility filter. Both: 63_30 within 10% of the
52-week high, sell after 250 sessions at most, 15 slots, mid caps first.
Writes reports/rule_compare.md. Run on GitHub (Yahoo): signal_model mode=rule_compare.
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

REPORT = Path(__file__).resolve().parent.parent / "reports" / "rule_compare.md"
OLD = {"win": (3, 5), "exit": "sma50", "stop": (12.0, 15.0), "atr": True}
NEW = {"win": (10, 20), "exit": "ema30", "stop": (15.0, 15.0), "atr": False}
VARIANTS = {
    "Old rule (until 13 Nov)": OLD,
    "Old + 30-day EMA exit": {**OLD, "exit": "ema30"},
    "Old + 15% stop for all": {**OLD, "stop": (15.0, 15.0)},
    "Old + 10/20-session buy-stop": {**OLD, "win": (10, 20)},
    "Old + no volatility filter": {**OLD, "atr": False},
    "New rule (all four changes)": NEW,
    "EMA exit + 15% stop": {**OLD, "exit": "ema30", "stop": (15.0, 15.0)},
    "EMA exit + 15% stop + 10/20 buy-stop": {**OLD, "exit": "ema30", "stop": (15.0, 15.0), "win": (10, 20)},
    "EMA exit + 15% stop, no vol. filter": {**OLD, "exit": "ema30", "stop": (15.0, 15.0), "atr": False},
}


def _line(c: pd.Series, kind: str) -> np.ndarray:
    if kind == "ema30":
        return c.ewm(span=30, adjust=False, min_periods=30).mean().to_numpy()
    return c.rolling(50, min_periods=50).mean().to_numpy()


def trades(hits, prices, v) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        wk = bs.is_weekly(h["scanner_name"])
        sig = bs.signal_bar(df, h["hit_date"], wk) if df is not None else None
        if sig is None:
            continue
        sp, trig = sig["end_pos"], sig["trigger"]
        dist = dz.dist_52w_high(df, sp)
        if h["scanner_name"] == "63_30_daily" and dist is not None and dist < -10:
            continue
        if v["atr"] and wk:
            a = dz.atr_pct(df, sp)
            if a is not None and a >= 4.0:
                continue
        o, hi, lo, c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
        win = v["win"][1] if wk else v["win"][0]
        b = next((i for i in range(sp + 1, min(len(df), sp + 1 + win)) if hi[i] > trig), None)
        if b is None:
            continue
        ep = max(o[b], trig)
        stop = ep * (1 - (v["stop"][1] if wk else v["stop"][0]) / 100)
        ma = _line(df["Close"], v["exit"])
        n, last, x = len(c), min(len(c) - 1, b + 250), None
        for i in range(b, last + 1):
            if i > b and o[i] <= stop:
                x = (o[i], i, "stop"); break
            if lo[i] <= stop:
                x = (stop, i, "stop"); break
            if i > b and not np.isnan(ma[i]) and c[i] < ma[i]:
                x = (o[i + 1], i + 1, "trend") if i + 1 < n else None
                break
        else:
            if b + 250 <= n - 1:
                x = (c[last], last, "time")
        if x is None:
            continue  # still open
        rows.append({"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                     "entry_date": df.index[b], "exit_date": df.index[x[1]], "why": x[2],
                     "days": x[1] - b + 1, "ret": round((x[0] / ep - 1) * 100 - bs.COST_PCT, 2)})
    return pd.DataFrame(rows)


def stats(t: pd.DataFrame, a, b=None) -> dict:
    t = t[(t["entry_date"] >= a) & ((t["entry_date"] < b) if b is not None else True)]
    pf = dz.portfolio(t)
    eq = pf["equity"]
    r = t["ret"]
    return {"n": len(t), "win": (r > 0).mean() * 100, "avg": r.mean(), "aw": r[r > 0].mean(), "al": r[r <= 0].mean(),
            "days": t["days"].mean(), "cagr": dz._cagr(pf["capital"], eq.iloc[-1], eq.index[0], eq.index[-1]),
            "dd": (eq / eq.cummax() - 1).min() * 100, "final": eq.iloc[-1]}


def main() -> int:
    hits = load_hits()
    hits = hits[hits["source"] == "backtest"] if "source" in hits else hits
    start = (hits["hit_date"].min() - timedelta(days=420)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    res = {k: trades(hits, prices, v) for k, v in VARIANTS.items()}
    begin = res["Old rule (until 13 Nov)"].groupby("scanner")["entry_date"].min().max()
    L = ["# Rule change backtest (13 Nov 2026)", "",
         "Lines 2-5 change one thing from the old rule, line 6 has all four, the last three are combinations. ₹10L, 15 slots, mid caps first, "
         f"after 0.25% costs, from {begin.date()}. Trades still open are left out.", ""]
    for name, a, b in [("All years", begin, None), ("2019-22", begin, pd.Timestamp("2023-01-01")),
                       ("2023-26", pd.Timestamp("2023-01-01"), None)]:
        L += [f"## {name}", "", "| Rule | Trades | Win | Avg | Avg win / loss | Days held | Per year | Worst fall | ₹10L became |",
              "|---|---|---|---|---|---|---|---|---|"]
        for k, t in res.items():
            s = stats(t, a, b)
            L.append(f"| {k} | {s['n']} | {s['win']:.0f}% | {s['avg']:+.1f}% | {s['aw']:+.1f}% / {s['al']:.1f}% | "
                     f"{s['days']:.0f} | {s['cagr']:.1f}% | {s['dd']:.1f}% | ₹{s['final'] / 1e5:.1f}L |")
        L.append("")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
