"""Remove look-ahead from a Chartink backtest that uses a Weekly RSI condition.

Usage: python honest_filter.py <in.csv> <out.csv> [threshold=65]

Chartink's backtest judges "Weekly RSI(14) > 65" with the WHOLE week's close,
including days after the signal. Live, on the signal day, only the week so far
is known. This keeps only the hits whose weekly RSI(14) was already above the
threshold on the signal day itself (this week counted up to that day), so the
result shows what the scan would really have given live. Rows are written in
the original export format.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

import breakout_sim as bs
import condition_check as cc
import dipzone
import scan_quality as sq


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    thr = float(sys.argv[3]) if len(sys.argv) > 3 else 65.0
    raw = pd.read_csv(src, encoding="utf-8-sig")
    hits = sq.load(src)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    keep, no_px, fail = [], 0, 0
    for i, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] < 60:
            no_px += 1
            continue
        p = sig["end_pos"]
        honest, _full = cc.weekly_rsi(df.iloc[:min(len(df), p + 6)], p)
        if honest > thr:
            keep.append(i)
        else:
            fail += 1
    raw.loc[keep].to_csv(dst, index=False, encoding="utf-8")
    print(f"{len(hits)} hits: kept {len(keep)}, removed {fail} (weekly RSI not above {thr:g} on the signal day), "
          f"{no_px} without prices. Saved {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
