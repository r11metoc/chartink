"""Orchestrator: scrape the dashboard, persist results, detect and notify breakouts."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone

import db
from notify import (
    _col,
    _num,
    format_breakout_message,
    format_digest_message,
    format_scan_message,
    format_sector_focus_message,
    send_telegram_message,
)
import paper
import track_record
from export_dashboard import sector_momentum_view, track_for
from scrape_dashboard import scrape_dashboard
from slot_gate import IST, current_slot

DEFAULT_URL = "https://chartink.com/dashboard/45863"


def main() -> int:
    url = os.environ.get("CHARTINK_DASHBOARD_URL", DEFAULT_URL)
    debug = os.environ.get("CHARTINK_DEBUG_DUMP") == "1"
    send_snapshot = os.environ.get("CHARTINK_SEND_SNAPSHOT") == "1"
    send_digest = os.environ.get("CHARTINK_SEND_DIGEST") == "1"
    digest_days = int(os.environ.get("CHARTINK_DIGEST_DAYS") or "30")
    gate_slot = os.environ.get("CHARTINK_SLOT") or None
    # A manual scan that sends the messages inside a slot window fills that
    # slot too, so a late scheduled run doesn't send the same messages again.
    slot = gate_slot or (current_slot(datetime.now(IST)) if send_snapshot or send_digest else None)

    if gate_slot:
        # Two queued runs can pass the gate for the same slot; only the first scans.
        conn = db.connect()
        done = db.slot_done(conn, gate_slot)
        conn.close()
        if done:
            print(f"Slot {gate_slot} was already scanned, skipping.")
            return 0

    scans = scrape_dashboard(url, debug=debug)
    if not scans:
        print("No tables found on the dashboard page. Set CHARTINK_DEBUG_DUMP=1 and re-run to inspect.")
        return 1

    conn = db.connect()
    run_id = db.create_run(conn)

    new_breakouts: list[tuple[str, str, dict]] = []
    rec = track_record.TrackRecord()
    today = datetime.now(IST).date().isoformat()

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
            db.record_breakout(conn, run_id, scan.scanner_name, symbol, row, kind=kind)
            row["_track"] = track_for(conn, rec, scan.scanner_name, symbol, today, _num(_col(row, "mcap")))
            new_breakouts.append((scan.scanner_name, kind, row))
            print(f"  {kind}: {symbol}")

    trigger_lookup = {}
    if send_snapshot:
        for scan in scans:
            for row in scan.rows:
                symbol = row["_symbol"]
                trigger_lookup[(scan.scanner_name, symbol)] = db.trigger_row(conn, scan.scanner_name, symbol)

    if slot:
        db.mark_slot_done(conn, slot, run_id)
    conn.commit()
    conn.close()

    if new_breakouts:
        send_telegram_message(format_breakout_message(new_breakouts))
    else:
        print("No new breakouts this run.")

    if send_snapshot:
        send_telegram_message(format_scan_message(scans, trigger_lookup))

    if send_digest:
        since = (datetime.now(timezone.utc) - timedelta(days=digest_days)).isoformat()
        digest_conn = db.connect()
        entries = db.breakouts_since(digest_conn, since)
        on_scan = {s.scanner_name: db.symbols_in_latest_run(digest_conn, s.scanner_name) for s in scans}
        for entry in entries:
            entry["_current_row"] = db.latest_row(digest_conn, entry["scanner_name"], entry["symbol"])
            entry["_on_scan"] = entry["symbol"] in on_scan.get(entry["scanner_name"], set())
            if not entry["_on_scan"]:
                # Off the scanner, the last scan price is stale; use the latest daily close.
                bars = db.daily_prices_since(digest_conn, entry["symbol"], entry["detected_at"][:10])
                if bars:
                    entry["_current_row"] = {"Price": f"{bars[-1][4]:.2f}"}

        today = datetime.now(timezone.utc).date()
        weekly_since = (today - timedelta(days=7)).isoformat()
        monthly_since = (today - timedelta(days=30)).isoformat()
        sector_focus = {}
        for scanner_name in db.distinct_backtest_scanners(digest_conn):
            sector_focus[scanner_name] = {
                "weekly": db.sector_counts_since(digest_conn, scanner_name, weekly_since),
                "monthly": db.sector_counts_since(digest_conn, scanner_name, monthly_since),
            }

        momentum = sector_momentum_view(digest_conn, datetime.now(IST).date())
        book = {"start": paper.PAPER_START, "stake": paper.STAKE,
                "summary": paper.summarize(paper.paper_trades(digest_conn))}
        digest_conn.close()
        send_telegram_message(format_sector_focus_message(sector_focus))
        send_telegram_message(format_digest_message(entries, digest_days, momentum, book))

    return 0


if __name__ == "__main__":
    sys.exit(main())
