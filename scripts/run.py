"""Orchestrator: scrape the dashboard, persist results, detect and notify breakouts."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import db
from notify import (
    format_breakout_message,
    format_buy_hold_message,
    format_digest_message,
    format_sector_focus_message,
    format_snapshot_message,
    send_telegram_message,
)
from scrape_dashboard import scrape_dashboard

DEFAULT_URL = "https://chartink.com/dashboard/45863"


def _industry_of(row: dict) -> str | None:
    for k, v in row.items():
        if "industry" in k.lower() and v:
            return v
    return None


def main() -> int:
    url = os.environ.get("CHARTINK_DASHBOARD_URL", DEFAULT_URL)
    debug = os.environ.get("CHARTINK_DEBUG_DUMP") == "1"
    send_snapshot = os.environ.get("CHARTINK_SEND_SNAPSHOT") == "1"
    send_digest = os.environ.get("CHARTINK_SEND_DIGEST") == "1"
    digest_days = int(os.environ.get("CHARTINK_DIGEST_DAYS") or "7")

    scans = scrape_dashboard(url, debug=debug)
    if not scans:
        print("No tables found on the dashboard page. Set CHARTINK_DEBUG_DUMP=1 and re-run to inspect.")
        return 1

    conn = db.connect()
    run_id = db.create_run(conn)

    new_breakouts: list[tuple[str, str, dict]] = []

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
            row = curr_by_symbol[symbol]
            kind = "retest" if db.has_appeared_before(conn, scan.scanner_name, symbol, run_id) else "fresh"

            row["_backtest_hits"] = db.backtest_history(conn, scan.scanner_name, symbol)
            industry = _industry_of(row)
            if industry:
                row["_sector_share"] = db.backtest_sector_share(conn, scan.scanner_name, industry)

            db.record_breakout(conn, run_id, scan.scanner_name, symbol, row, kind=kind)
            new_breakouts.append((scan.scanner_name, kind, row))
            print(f"  {kind}: {symbol}")

    trigger_lookup = {}
    if send_snapshot:
        for scan in scans:
            for row in scan.rows:
                symbol = row["_symbol"]
                trigger_lookup[(scan.scanner_name, symbol)] = db.trigger_row(conn, scan.scanner_name, symbol)

    conn.commit()
    conn.close()

    if new_breakouts:
        send_telegram_message(format_breakout_message(new_breakouts))
    else:
        print("No new breakouts this run.")

    if send_snapshot:
        send_telegram_message(format_snapshot_message(scans))
        send_telegram_message(format_buy_hold_message(scans, trigger_lookup))

    if send_digest:
        since = (datetime.now(timezone.utc) - timedelta(days=digest_days)).isoformat()
        digest_conn = db.connect()
        entries = db.breakouts_since(digest_conn, since)
        for entry in entries:
            entry["_current_row"] = db.latest_row(digest_conn, entry["scanner_name"], entry["symbol"])

        today = datetime.now(timezone.utc).date()
        weekly_since = (today - timedelta(days=7)).isoformat()
        monthly_since = (today - timedelta(days=30)).isoformat()
        sector_focus = {}
        for scanner_name in db.distinct_backtest_scanners(digest_conn):
            sector_focus[scanner_name] = {
                "weekly": db.sector_counts_since(digest_conn, scanner_name, weekly_since),
                "monthly": db.sector_counts_since(digest_conn, scanner_name, monthly_since),
            }

        outcome_params = db.latest_outcome_params(digest_conn)
        recent_outcomes = []
        if outcome_params:
            horizon_days, threshold_pct = outcome_params
            outcomes_since_date = (today - timedelta(days=digest_days)).isoformat()
            recent_outcomes = db.outcomes_with_context(digest_conn, horizon_days, threshold_pct, outcomes_since_date)

        digest_conn.close()
        send_telegram_message(format_sector_focus_message(sector_focus))
        send_telegram_message(format_digest_message(entries, digest_days, recent_outcomes))

    return 0


if __name__ == "__main__":
    sys.exit(main())
