"""Exit lab: try many sell rules on one scan (buy at the next open after the signal).

Usage: python exit_lab.py "<Chartink backtest export.csv>"

Each rule is run on the scan's trades as a ₹10L / 15-slot portfolio (0.25% costs)
and on the same stocks on random days. A rule counts as BETTER than the bot rule
(ema30) only if it earns more in BOTH 2019-22 and 2023-26 with a worst fall no
more than 1 point deeper. Writes reports/exits_<file>.md.

Rules (all have a hard stop and a max hold of 250 sessions unless stated):
  ema30        bot rule: next open after a close below the 30-day EMA, 15% stop
  ema30x2      as ema30 but needs 2 closes in a row below the EMA (fewer shake-outs)
  ema20        close below the 20-day EMA, 10% stop
  ema30s8      ema30 with an 8% stop
  ema30be      ema30; stop moves to the buy price once +8% is reached
  ema30time    ema30; also sell after 10 sessions if not at least +3%
  sig_low      sell on a close below the signal day's low, else ema30
  lock20       ema30 until +20%, then a 10% trailing stop from the highest close
  ema30to63    ema30 until +15%, then the 63-day EMA (let big winners run)
  half10       sell half at +10%, rest by ema30 (stop to cost after +10%)
  atr3         close below highest close - 3 x ATR(14), 15% stop
  ema63s10     close below the 63-day EMA, 10% stop
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
RULES = ["ema30", "ema30x2", "ema20", "ema30s8", "ema30be", "ema30time", "sig_low", "lock20",
         "ema30to63", "half10", "atr3", "ema63s10"]
HALVES = [("2019-01-01", "2023-01-01"), ("2023-01-01", "2100-01-01")]


def sell(rule, o, h, l, c, e20, e30, e63, atr, e, ep, siglow):
    n = len(c)
    stop = ep * {"ema20": 0.90, "ema30s8": 0.92, "ema63s10": 0.90}.get(rule, 0.85)
    last = min(n - 1, e + dipzone.RIDE_MAX_HOLD)
    hi_c, below, half_done, banked, stage2, lock = ep, 0, False, 0.0, False, None

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
        if rule == "half10" and not half_done and h[i] >= ep * 1.10:
            half_done, banked = True, (0.10 if (i == e or o[i] < ep * 1.10) else o[i] / ep - 1)
            stop = max(stop, ep)
        if rule == "ema30be" and h[i] >= ep * 1.08:
            stop = max(stop, ep)
        hi_c = max(hi_c, c[i])
        if rule == "lock20" and hi_c >= ep * 1.20:
            lock = hi_c * 0.90
        if rule == "ema30to63" and hi_c >= ep * 1.15:
            stage2 = True
        if i == e:
            continue
        out = False
        if rule in ("ema30", "ema30s8", "ema30be", "ema30time", "half10", "sig_low"):
            out = c[i] < e30[i]
        elif rule == "ema30x2":
            below = below + 1 if c[i] < e30[i] else 0
            out = below >= 2
        elif rule == "ema20":
            out = c[i] < e20[i]
        elif rule == "lock20":
            out = c[i] < lock if lock is not None else c[i] < e30[i]
        elif rule == "ema30to63":
            out = c[i] < (e63[i] if stage2 else e30[i])
        elif rule == "atr3":
            out = not np.isnan(atr[i]) and c[i] < hi_c - 3 * atr[i]
        elif rule == "ema63s10":
            out = c[i] < e63[i]
        if rule == "ema30time" and i - e == 10 and c[i] < ep * 1.03:
            out = True
        if rule == "sig_low" and c[i] < siglow:
            out = True
        if out:
            if i + 1 >= n:
                return None
            return done(float(o[i + 1]), i + 1)
    if last == e + dipzone.RIDE_MAX_HOLD:
        return done(float(c[last]), last)
    return None


def trades(hits: pd.DataFrame, prices: dict) -> pd.DataFrame:
    rows, cache = [], {}
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] + 1 >= len(df):
            continue
        sp = sig["end_pos"]
        if h["symbol"] not in cache:
            cl = df["Close"]
            tr = pd.concat([df["High"] - df["Low"], (df["High"] - cl.shift()).abs(), (df["Low"] - cl.shift()).abs()], axis=1).max(axis=1)
            cache[h["symbol"]] = (*(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                  cl.ewm(span=20, adjust=False, min_periods=20).mean().to_numpy(),
                                  dipzone.exit_line(cl),
                                  cl.ewm(span=63, adjust=False, min_periods=63).mean().to_numpy(),
                                  tr.rolling(14).mean().to_numpy())
        o, hi, lo, c, e20, e30, e63, atr = cache[h["symbol"]]
        e, ep = sp + 1, float(o[sp + 1])
        for r in RULES:
            x = sell(r, o, hi, lo, c, e20, e30, e63, atr, e, ep, float(lo[sp]))
            if x is None:
                continue
            rows.append({"rule": r, "symbol": h["symbol"], "scanner": "scan", "cap": h["marketcap"],
                         "entry_date": df.index[e], "exit_date": df.index[x[1]], "ret": x[0], "days": x[1] - e + 1})
    return pd.DataFrame(rows)


def _cagr(eq, a, b):
    x = eq[(eq.index >= pd.Timestamp(a)) & (eq.index < pd.Timestamp(b))]
    if len(x) < 2:
        return np.nan
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    return ((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100 if yrs > 0 else np.nan


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
    rt = pd.concat([trades(sq.random_hits(hits, prices, s), prices) for s in (1, 2)], ignore_index=True)
    res = []
    for r in RULES:
        g = t[t["rule"] == r]
        if g.empty:
            continue
        eq = dipzone.portfolio(g)["equity"]
        res.append({"rule": r, "trades": len(g), "win": (g["ret"] > 0).mean() * 100, "avg": g["ret"].mean(),
                    "rnd": rt[rt["rule"] == r]["ret"].mean(), "days": g["days"].mean(),
                    "cagr": _cagr(eq, "2000-01-01", "2100-01-01"), "h1": _cagr(eq, *HALVES[0]),
                    "h2": _cagr(eq, *HALVES[1]), "y25": _cagr(eq, "2025-01-01", "2100-01-01"),
                    "dd": (eq / eq.cummax() - 1).min() * 100})
    res = pd.DataFrame(res)
    base = res[res["rule"] == "ema30"].iloc[0]
    res["better"] = (res["h1"] > base["h1"]) & (res["h2"] > base["h2"]) & (res["dd"] >= base["dd"] - 1)
    res = res.sort_values("cagr", ascending=False)
    L = [f"# Exit lab: {path.stem}", "",
         f"{len(hits):,} signals. Bought at the next open, ₹10L, 15 slots, 0.25% costs. "
         "'Random' = average trade of the same rule on the same stocks on random days.", "",
         "| Sell rule | Trades | Won | Avg | Random | Days | Per year | 2019-22 | 2023-26 | 2025-26 | Worst fall | Better? |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in res.iterrows():
        mark = "**bot rule**" if r["rule"] == "ema30" else ("✓" if r["better"] else "")
        L.append(f"| {r['rule']} | {r['trades']} | {r['win']:.0f}% | {r['avg']:+.2f}% | {r['rnd']:+.2f}% | {r['days']:.0f} | "
                 f"{r['cagr']:.1f}% | {r['h1']:.1f}% | {r['h2']:.1f}% | {r['y25']:.1f}% | {r['dd']:.1f}% | {mark} |")
    ok = res[res["better"]]
    L += ["", "Better than the bot rule in both halves: " + (", ".join(ok["rule"]) if len(ok) else "none")]
    text = "\n".join(L) + "\n"
    out = ROOT / "reports" / f"exits_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
