"""Fetch historical NSE prices for every symbol in backtest_hits and label
each historical trigger as a real breakout or a fake trigger, based on
whether price actually rose enough afterward.

The raw Chartink backtest export has no price/return data at all - this is
what makes it usable for anything beyond frequency-counting. Runs only on
GitHub Actions (or anywhere with real internet access); this sandbox's
network policy blocks Yahoo Finance, same as it blocks chartink.com.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

import db

SUCCESS_THRESHOLD_PCT = 3.0
HORIZON_DAYS = 5
BATCH_SIZE = 50


def _to_yahoo_ticker(symbol: str) -> str:
    # NSE symbols map to Yahoo as SYMBOL.NS. A handful of symbols contain
    # characters Yahoo's ticker scheme doesn't use this way (e.g. '&', '-'
    # for demerger-share suffixes) and simply won't resolve - those get
    # skipped below rather than guessed at.
    return f"{symbol}.NS"


def _fetch_batch(symbols: list[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    tickers = [_to_yahoo_ticker(s) for s in symbols]
    try:
        data = yf.download(
            tickers=tickers, start=start, end=end, interval="1d",
            group_by="ticker", threads=True, progress=False, auto_adjust=False,
        )
    except Exception as e:
        print(f"  batch fetch failed ({e}), skipping {len(symbols)} symbols")
        return {}

    out = {}
    for symbol, ticker in zip(symbols, tickers):
        try:
            df = data[ticker] if len(tickers) > 1 else data
        except (KeyError, TypeError):
            continue
        df = df.dropna(subset=["Close"])
        if df.empty:
            continue
        df.index = pd.to_datetime(df.index).tz_localize(None)
        out[symbol] = df
    return out


def _compute_outcome(df: pd.DataFrame, hit_date: datetime):
    future_dates = df.index[df.index >= hit_date]
    if len(future_dates) == 0:
        return None
    trigger_pos = df.index.get_loc(future_dates[0])
    future_pos = trigger_pos + HORIZON_DAYS
    if future_pos >= len(df):
        return None  # not enough trading days have passed yet
    trigger_close = float(df.iloc[trigger_pos]["Close"])
    future_close = float(df.iloc[future_pos]["Close"])
    if trigger_close <= 0:
        return None
    pct_return = (future_close - trigger_close) / trigger_close * 100
    label = 1 if pct_return >= SUCCESS_THRESHOLD_PCT else 0
    return trigger_close, future_close, pct_return, label


def main() -> int:
    conn = db.connect()
    symbols = db.distinct_backtest_symbols(conn)
    hits = db.all_backtest_hits(conn)
    by_symbol: dict[str, list[tuple[str, str]]] = {}
    for scanner_name, hit_date, symbol in hits:
        by_symbol.setdefault(symbol, []).append((scanner_name, hit_date))

    earliest = db.earliest_backtest_date(conn)
    start = (datetime.fromisoformat(earliest) - timedelta(days=5)).date().isoformat()
    end = (datetime.now() + timedelta(days=1)).date().isoformat()

    print(f"{len(symbols)} unique symbols, {len(hits)} historical hits, range {start}..{end}")

    fetched_symbols = 0
    skipped_symbols = 0
    computed = 0
    insufficient_data = 0

    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        price_data = _fetch_batch(batch, start, end)
        for symbol in batch:
            df = price_data.get(symbol)
            if df is None:
                skipped_symbols += 1
                continue
            fetched_symbols += 1
            for scanner_name, hit_date in by_symbol[symbol]:
                outcome = _compute_outcome(df, datetime.fromisoformat(hit_date))
                if outcome is None:
                    insufficient_data += 1
                    continue
                trigger_close, future_close, pct_return, label = outcome
                db.save_backtest_outcome(
                    conn, scanner_name, hit_date, symbol,
                    trigger_close, future_close, pct_return, label,
                    HORIZON_DAYS, SUCCESS_THRESHOLD_PCT,
                )
                computed += 1
        conn.commit()
        print(f"  ...{min(i + BATCH_SIZE, len(symbols))}/{len(symbols)} symbols "
              f"(fetched {fetched_symbols}, skipped {skipped_symbols}, outcomes {computed})")
        time.sleep(1)  # be polite to Yahoo's API between batches

    conn.close()
    print(f"\nDone. Fetched {fetched_symbols} symbols ({skipped_symbols} skipped/unresolvable), "
          f"{computed} outcomes computed, {insufficient_data} hits too recent to score yet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
