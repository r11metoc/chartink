"""Which extra conditions would improve a scan? Split its trades by facts on the signal day.

Usage: python feature_split.py "<Chartink backtest export.csv>"

Every hit is traded with your rule (buy at the next open, sell at the next open
after a close below the 30-day EMA, 15% stop, 0.25% costs). The trades are
then split by about a dozen facts known on the signal day. A condition worth
adding to the scan shows a clearly better average trade AND holds up in both
2019-22 and 2023-26 with enough trades. Writes reports/features_<file>.md.
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
SPLIT = pd.Timestamp("2023-01-01")


def _rsi(c: pd.Series, n: int = 14) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def indicators(df: pd.DataFrame) -> pd.DataFrame:
    c, v = df["Close"], df["Volume"].astype(float)
    e = lambda n: c.ewm(span=n, adjust=False, min_periods=n).mean()  # noqa: E731
    sma20, sd20 = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    out = pd.DataFrame(index=df.index)
    out["ema30"], out["ema50"], out["ema63"], out["ema200"] = e(30), e(50), e(63), e(200)
    out["ema200_up"] = out["ema200"] > out["ema200"].shift(20)
    out["rsi"] = _rsi(c)
    out["vol_x"] = v / v.rolling(20).mean()
    out["turnover_cr"] = (c * v).rolling(20).mean() / 1e7
    out["bbw"] = 4 * sd20 / sma20 * 100
    out["day_pct"] = (c / c.shift(1) - 1) * 100
    out["ret_60"] = (c / c.shift(60) - 1) * 100
    out["hi52"] = df["High"].rolling(252, min_periods=120).max()
    return out


def bucket(x: float, edges: list[float], labels: list[str]) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    for e, lab in zip(edges, labels):
        if x < e:
            return lab
    return labels[-1]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    path = Path(sys.argv[1])
    hits = sq.load(path)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    idx = fetch_daily(["^NSEI"], start).get("^NSEI")
    nif = None
    if idx is not None:
        nc = idx["Close"]
        nif = pd.DataFrame({"above200": nc > nc.ewm(span=200, adjust=False).mean(),
                            "ret20": (nc / nc.shift(20) - 1) * 100})
    ind, rows = {}, []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] < 210:
            continue
        sp = sig["end_pos"]
        if h["symbol"] not in ind:
            c = df["Close"]
            ind[h["symbol"]] = (indicators(df), *(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                c.ewm(span=20, adjust=False, min_periods=20).mean().to_numpy(), dipzone.exit_line(c))
        f, o, hi, lo, c, e20, e30 = ind[h["symbol"]]
        en = rl.entry("open", o, hi, c, sp, 0.0, 1)
        if en is None:
            continue
        x = rl.exit_("ema30", o, hi, lo, c, e20, e30, np.full(len(c), np.nan), *en)
        if x is None:
            continue
        r = f.iloc[sp]
        day = df.index[sp]
        nr = nif.loc[:day].iloc[-1] if nif is not None and (nif.index <= day).any() else None
        rows.append({
            "date": day, "ret": x[0],
            "Close vs 200-day EMA": "above" if c[sp] > r["ema200"] else "below",
            "200-day EMA rising (vs 20 days ago)": "yes" if r["ema200_up"] else "no",
            "50-day EMA vs 200-day EMA": "50 above 200" if r["ema50"] > r["ema200"] else "50 below 200",
            "30-day EMA vs 63-day EMA": "30 above 63" if r["ema30"] > r["ema63"] else "30 below 63",
            "Below 52-week high": bucket((c[sp] / r["hi52"] - 1) * 100, [-30, -20, -10, -5],
                                         ["30%+ below", "20-30% below", "10-20% below", "5-10% below", "within 5%"]),
            "Daily RSI(14)": bucket(r["rsi"], [55, 65, 75], ["under 55", "55-65", "65-75", "over 75"]),
            "Volume vs 20-day average": bucket(r["vol_x"], [1, 1.5, 2.5], ["under 1x", "1-1.5x", "1.5-2.5x", "over 2.5x"]),
            "Avg daily turnover": bucket(r["turnover_cr"], [2, 10, 50], ["under 2 Cr", "2-10 Cr", "10-50 Cr", "over 50 Cr"]),
            "Bollinger width (squeeze)": bucket(r["bbw"], [8, 12, 18], ["under 8%", "8-12%", "12-18%", "over 18%"]),
            "Day's gain": bucket(r["day_pct"], [2, 4, 7], ["under 2%", "2-4%", "4-7%", "over 7%"]),
            "Last 3 months": bucket(r["ret_60"], [-10, 0, 10, 25], ["down 10%+", "down 0-10%", "up 0-10%", "up 10-25%", "up 25%+"]),
            "Market: Nifty vs its 200-day EMA": "n/a" if nr is None else ("above" if nr["above200"] else "below"),
            "Market: Nifty last month": "n/a" if nr is None else ("up" if nr["ret20"] > 0 else "down"),
            "Market cap": h["marketcap"] or "blank",
        })
    t = pd.DataFrame(rows)
    allavg = t["ret"].mean()
    L = [f"# Which extra conditions would help: {path.stem}", "",
         f"{len(t):,} closed trades (buy next open, sell below the 30-day EMA, 15% stop, 0.25% costs). "
         f"All trades: {(t['ret'] > 0).mean() * 100:.0f}% won, {allavg:+.2f}% average. "
         "Each row: trades · won · average, then the average in 2019-22 and 2023-26. "
         "★ = average at least 1 point better than all trades in BOTH halves, with 100+ trades.", ""]
    for col in [c for c in t.columns if c not in ("date", "ret")]:
        L += [f"## {col}", "", "| Value | Trades | Won | Avg | 2019-22 | 2023-26 | |", "|---|---|---|---|---|---|---|"]
        a1, a2 = t[t["date"] < SPLIT]["ret"].mean(), t[t["date"] >= SPLIT]["ret"].mean()
        for val, g in sorted(t.groupby(col), key=lambda kv: str(kv[0])):
            g1, g2 = g[g["date"] < SPLIT]["ret"], g[g["date"] >= SPLIT]["ret"]
            star = "★" if len(g) >= 100 and len(g1) and len(g2) and g1.mean() >= a1 + 1 and g2.mean() >= a2 + 1 else ""
            L.append(f"| {val} | {len(g)} | {(g['ret'] > 0).mean() * 100:.0f}% | {g['ret'].mean():+.2f}% | "
                     f"{g1.mean() if len(g1) else float('nan'):+.2f}% | {g2.mean() if len(g2) else float('nan'):+.2f}% | {star} |")
        L.append("")
    text = "\n".join(L)
    out = ROOT / "reports" / f"features_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
