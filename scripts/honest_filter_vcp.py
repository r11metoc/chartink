"""Remove weekly/monthly look-ahead from a VCP-& TIGHTNESS backtest export.

Usage: python honest_filter_vcp.py <in.csv> <out.csv>

Re-checks, on the signal day itself (current week / month counted only up to
that day), the scan's conditions that use weekly or monthly candles:
  Close >= 0.80 x Weekly Max(52, Weekly High)
  Close >= 1.3 x Weekly Min(52, Weekly Low)
  Weekly RSI(14) > 55
  Monthly EMA(10) >= 1 month ago Monthly EMA(10) >= 2 months ago Monthly EMA(10)
Chartink's backtest uses the whole week / month (days after the signal).
Keeps only hits that pass all of them live. Prints what each removed.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import scan_quality as sq


def _rsi_last(x: pd.Series, n: int = 14) -> float:
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return float((100 - 100 / (1 + up / dn.replace(0, np.nan))).iloc[-1])


def periods(df: pd.DataFrame, pos: int, freq: str) -> pd.DataFrame:
    """OHLC of completed periods before the signal day + the current one up to it."""
    day = df.index[pos]
    d = df.iloc[:pos + 1]
    agg = d.resample(freq).agg({"High": "max", "Low": "min", "Close": "last"}).dropna()
    return agg  # labels are period ends; the last row is the current, partial period


def check(df: pd.DataFrame, pos: int) -> str | None:
    c = float(df["Close"].iloc[pos])
    w = periods(df, pos, "W-FRI").tail(52)
    if not c >= 0.80 * w["High"].max():
        return "52-week high"
    if not c >= 1.3 * w["Low"].min():
        return "52-week low"
    if not _rsi_last(periods(df, pos, "W-FRI")["Close"]) > 55:
        return "weekly RSI"
    m = periods(df, pos, "ME")["Close"].ewm(span=10, adjust=False).mean()
    if len(m) < 3 or not (m.iloc[-1] >= m.iloc[-2] >= m.iloc[-3]):
        return "monthly EMA"
    return None


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    raw = pd.read_csv(src, encoding="utf-8-sig")
    hits = sq.load(src)
    start = (hits["hit_date"].min() - timedelta(days=365 * 3)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    keep, why = [], {"no prices": 0, "52-week high": 0, "52-week low": 0, "weekly RSI": 0, "monthly EMA": 0}
    for i, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] < 260:
            why["no prices"] += 1
            continue
        r = check(df, sig["end_pos"])
        if r is None:
            keep.append(i)
        else:
            why[r] += 1
    raw.loc[keep].to_csv(dst, index=False, encoding="utf-8")
    print(f"{len(hits)} hits: kept {len(keep)} that pass live on the signal day. Removed: "
          + ", ".join(f"{k} {v}" for k, v in why.items()) + f". Saved {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
