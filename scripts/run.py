"""Orchestrator: scrape the dashboard, persist results, detect and notify breakouts."""

from __future__ import annotations

import os
import sys

import db
from notify import format_breakout_message, send_telegram_message
from scrape_dashboard import scrape_dashboard

DEFAULT_URL = "https://chartink.com/dashboard/45863"


def main() -> int:
    url = os.environ.get("CHARTINK_DASHBOARD_URL", DEFAULT_URL)
    debug = os.environ.get("CHARTINK_DEBUG_DUMP") == "1"

    scans = scrape_dashboard(url, debug=debug)
    if not scans:
        print("No tables found on the dashboard page. Set CHARTINK_DEBUG_DUMP=1 and re-run to inspect.")
        return 1

    conn = db.connect()
    run_id = db.create_run(conn)

    new_breakouts: list[tuple[str, str]] = []

    for scan in scans:
        print(f"Scanner '{scan.scanner_name}': {len(scan.rows)} rows")
        db.save_results(conn, run_id, scan.scanner_name, scan.rows)

        prev_id = db.previous_run_id(conn, scan.scanner_name, run_id)
        if prev_id is None:
            print(f"  first run for this scanner, seeding baseline ({len(scan.rows)} symbols)")
            continue

        prev_symbols = db.symbols_for_run(conn, scan.scanner_name, prev_id)
        curr_by_symbol = {row["_symbol"]: row for row in scan.rows}
        new_symbols = set(curr_by_symbol) - prev_symbols

        for symbol in sorted(new_symbols):
            db.record_breakout(conn, run_id, scan.scanner_name, symbol, curr_by_symbol[symbol])
            new_breakouts.append((scan.scanner_name, symbol))
            print(f"  breakout: {symbol}")

    conn.commit()
    conn.close()

    if new_breakouts:
        send_telegram_message(format_breakout_message(new_breakouts))
    else:
        print("No new breakouts this run.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
