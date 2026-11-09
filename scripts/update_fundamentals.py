"""Fetch fundamentals for every stock the scanners picked since the live start
date, refreshing anything older than 30 days: the Screener company page first
(screener_company.py, private cache), Yahoo as the fallback. Run each scan."""

from __future__ import annotations

import db
import dipzone
import live_signals
import yahoo_fundamentals as yf_fund


def main() -> int:
    conn = db.connect()
    symbols = {sym for _, _, sym, _ in live_signals._signals(conn, dipzone.START)}
    try:
        import screener_company
        m = screener_company.refresh(sorted(symbols))
        print(f"Screener pages: {m} updated, {sum(screener_company.cached(s) is not None for s in symbols)}/{len(symbols)} cached")
        import market
        watch = market.watch_symbols(conn)
        print(f"Screener announcements: {screener_company.refresh_events(watch)} of {len(watch)} watched stocks re-read")
    except Exception as e:  # Yahoo still covers them
        print(f"Screener pages failed ({e.__class__.__name__}); Yahoo only")
    n = yf_fund.refresh(conn, sorted(symbols))
    print(f"Yahoo fundamentals: {n} updated, {len(symbols)} scanner stocks covered")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
