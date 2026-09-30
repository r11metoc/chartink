"""Daily NSE OHLCV from Yahoo Finance.

Needs real internet access (GitHub Actions has it; the Claude sandbox this
repo is developed in does not).
"""

from __future__ import annotations

import time

import pandas as pd

NIFTY_TICKER = "^NSEI"
BATCH_SIZE = 50


def to_yahoo_ticker(symbol: str) -> str:
    return symbol if symbol.startswith("^") else f"{symbol}.NS"


def fetch_daily(symbols: list[str], start: str, end: str | None = None) -> dict[str, pd.DataFrame]:
    """symbol -> DataFrame[Open, High, Low, Close, Volume] indexed by date.
    Symbols Yahoo can't resolve are simply missing from the result."""
    import yfinance as yf

    out: dict[str, pd.DataFrame] = {}
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        tickers = [to_yahoo_ticker(s) for s in batch]
        try:
            data = yf.download(tickers=tickers, start=start, end=end, interval="1d",
                               group_by="ticker", threads=True, progress=False,
                               auto_adjust=False)
        except Exception as e:  # network hiccup: skip the batch, keep going
            print(f"  batch fetch failed ({e}), skipping {len(batch)} symbols")
            continue
        for symbol, ticker in zip(batch, tickers):
            try:
                df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            except KeyError:
                continue
            df = df[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Open", "High", "Low", "Close"])
            df = df[(df["High"] > 0) & (df["Low"] > 0)]
            if df.empty:
                continue
            df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
            out[symbol] = df.sort_index()
        print(f"  ...{min(i + BATCH_SIZE, len(symbols))}/{len(symbols)} symbols fetched ({len(out)} resolved)")
        if i + BATCH_SIZE < len(symbols):
            time.sleep(1)
    return out
