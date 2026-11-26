"""Remove weekly AND monthly look-ahead from a Chartink backtest export.

Usage: python honest_filter2.py <in.csv> <out.csv>

For Bullish_Scanner_x (17 Nov 2026) whose conditions include
  Monthly RSI(14) > 65, Weekly RSI(14) > 65,
  Monthly Close >= 1 month ago Max(63, Monthly High) * 0.85.
Chartink's backtest judges these with the WHOLE week's / month's close,
including days after the signal. Live, only the period so far is known.
Keeps the hits that pass all three on the signal day itself (current week /
month counted up to that day). Prints how many each condition removed.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import scan_quality as sq


def _rsi_last(closes: pd.Series, n: int = 14) -> float:
    d = closes.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    return float(r.iloc[-1])


def period_rsi(df: pd.DataFrame, pos: int, freq: str) -> float:
    """RSI(14) of weekly/monthly closes, the current period closing at bar `pos`."""
    day = df.index[pos]
    c = df["Close"].iloc[:pos + 1]
    per = c.resample(freq).last().dropna()
    done = per[per.index < day]          # period labels are period ends: the current one is >= day
    return _rsi_last(pd.concat([done, pd.Series([float(c.iloc[-1])], index=[day])]))


def monthly_high_ok(df: pd.DataFrame, pos: int) -> bool:
    day = df.index[pos]
    h = df["High"].iloc[:pos + 1].resample("ME").max().dropna()
    prev = h[h.index < day].tail(63)     # completed months only
    return len(prev) > 0 and float(df["Close"].iloc[pos]) >= prev.max() * 0.85


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    raw = pd.read_csv(src, encoding="utf-8-sig")
    hits = sq.load(src)
    start = (hits["hit_date"].min() - timedelta(days=365 * 7)).date().isoformat()   # 63 months of highs
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    keep, why = [], {"no prices": 0, "monthly RSI": 0, "weekly RSI": 0, "monthly high": 0}
    for i, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] < 60:
            why["no prices"] += 1
            continue
        p = sig["end_pos"]
        if not period_rsi(df, p, "ME") > 65:
            why["monthly RSI"] += 1
        elif not period_rsi(df, p, "W-FRI") > 65:
            why["weekly RSI"] += 1
        elif not monthly_high_ok(df, p):
            why["monthly high"] += 1
        else:
            keep.append(i)
    raw.loc[keep].to_csv(dst, index=False, encoding="utf-8")
    print(f"{len(hits)} hits: kept {len(keep)} that pass live on the signal day. Removed: "
          + ", ".join(f"{k} {v}" for k, v in why.items()) + f". Saved {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
