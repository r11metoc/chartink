"""Fetch daily prices from Yahoo Finance for every stock the dashboard tracks.

Tracked = triggered on any scanner in the last TRACK_DAYS, everything on a
scanner in the latest scan, and backtest picks from the last BACKTEST_DAYS.
Scan prices alone go stale once a stock drops off its scanner; these daily
bars keep its performance current.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import db
from market_data import fetch_daily

TRACK_DAYS = 120
# Backtest picks feed the sector view's "average move since pick" (last 4 weeks).
BACKTEST_DAYS = 35


def tracked_symbols(conn) -> tuple[list[str], str]:
    since = (datetime.now(timezone.utc) - timedelta(days=TRACK_DAYS)).isoformat()
    bt_since = (date.today() - timedelta(days=BACKTEST_DAYS)).isoformat()
    symbols = {s for (s,) in conn.execute("SELECT DISTINCT symbol FROM breakouts WHERE detected_at >= ?", (since,))}
    symbols |= {s for (s,) in conn.execute(
        "SELECT DISTINCT symbol FROM results WHERE run_id = (SELECT MAX(id) FROM runs)")}
    symbols |= {s for (s,) in conn.execute("SELECT DISTINCT symbol FROM backtest_hits WHERE hit_date >= ?", (bt_since,))}
    first = conn.execute("SELECT MIN(detected_at) FROM breakouts WHERE detected_at >= ?", (since,)).fetchone()[0]
    start = min(date.fromisoformat(first[:10]) if first else date.today(), date.fromisoformat(bt_since)) - timedelta(days=7)
    return sorted(symbols), start.isoformat()


def main() -> int:
    conn = db.connect()
    symbols, start = tracked_symbols(conn)
    if not symbols:
        print("No tracked symbols.")
        return 0
    print(f"Fetching daily prices for {len(symbols)} symbols since {start}")
    end = (date.today() + timedelta(days=1)).isoformat()  # yfinance's end is exclusive
    for symbol, df in fetch_daily(symbols, start, end).items():
        bars = [(d.date().isoformat(), float(r.Open), float(r.High), float(r.Low), float(r.Close))
                for d, r in df.iterrows()]
        db.save_daily_prices(conn, symbol, bars)
    conn.commit()
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
