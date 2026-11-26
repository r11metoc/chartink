"""Remove the look-ahead of a 'Monthly Close >= f x 1 month ago Max(63, Monthly High)' condition.

Usage: python honest_monthly_high.py <in.csv> <out.csv> [factor=0.8]

Chartink's backtest uses the month's final close, which can come weeks after
the signal. Live, the 'monthly close' on the signal day is that day's close.
Keeps only the hits whose signal-day close was already >= factor x the highest
monthly high of the 63 completed months before the signal month.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

import breakout_sim as bs
import scan_quality as sq


def ok(df: pd.DataFrame, pos: int, factor: float) -> bool:
    day = df.index[pos]
    h = df["High"].iloc[:pos + 1].resample("ME").max().dropna()
    prev = h[h.index < day].tail(63)          # completed months only
    return len(prev) > 0 and float(df["Close"].iloc[pos]) >= prev.max() * factor


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    factor = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8
    raw = pd.read_csv(src, encoding="utf-8-sig")
    hits = sq.load(src)
    start = (hits["hit_date"].min() - timedelta(days=365 * 6)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    keep, fail, nop = [], 0, 0
    for i, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None:
            nop += 1
            continue
        if ok(df, sig["end_pos"], factor):
            keep.append(i)
        else:
            fail += 1
    raw.loc[keep].to_csv(dst, index=False, encoding="utf-8")
    print(f"{len(hits)} hits: kept {len(keep)}, removed {fail} (monthly-high look-ahead), {nop} without prices. Saved {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
