"""Fetch fundamentals (Yahoo) for every stock the scanners picked since the
live start date, refreshing anything older than 30 days. Run each scan."""

from __future__ import annotations

import db
import dipzone
import live_signals
import yahoo_fundamentals as yf_fund


def main() -> int:
    conn = db.connect()
    symbols = {sym for _, _, sym, _ in live_signals._signals(conn, dipzone.START)}
    n = yf_fund.refresh(conn, sorted(symbols))
    print(f"Fundamentals: {n} updated, {len(symbols)} scanner stocks covered")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
