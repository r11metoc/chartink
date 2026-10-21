"""Import Chartink's own backtest CSV exports into the database.

Each CSV (one per scanner) has columns: Date, Symbol, Marketcapname, Sector.
Rows the CSV no longer has are removed, so the database always matches it.
This is historical "when did this scanner used to trigger on this symbol"
data, with no price or return information - it's used for descriptive
context only (has this scanner flagged this symbol before, and how often
does it hit a given sector), not for predicting returns.

Usage: python import_backtest.py [backtest_dir]
Expects files named <scanner_name>.csv in that directory (default: ../data/backtest).
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

import db

DEFAULT_DIR = Path(__file__).resolve().parent.parent / "data" / "backtest"


def _parse_date(raw: str) -> str:
    # Chartink exports as DD-MM-YYYY; store as ISO for sane sorting/filtering.
    return datetime.strptime(raw, "%d-%m-%Y").date().isoformat()


def import_file(conn, scanner_name: str, path: Path) -> int:
    """Make the database match the CSV: add new rows and drop rows the CSV no
    longer has (so replacing a scanner's export replaces its history)."""
    inserted, keep = 0, set()
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hit_date = _parse_date(row["Date"])
            symbol = row["Symbol"].strip().upper()
            marketcap = row.get("Marketcapname", "").strip()
            sector = row.get("Sector", "").strip()
            keep.add((hit_date, symbol))
            if db.import_backtest_hit(conn, scanner_name, hit_date, symbol, marketcap, sector):
                inserted += 1
    stale = [(d, s) for d, s in conn.execute(
        "SELECT hit_date, symbol FROM backtest_hits WHERE scanner_name = ?", (scanner_name,)) if (d, s) not in keep]
    conn.executemany("DELETE FROM backtest_hits WHERE scanner_name = ? AND hit_date = ? AND symbol = ?",
                     [(scanner_name, d, s) for d, s in stale])
    if stale:
        print(f"{scanner_name}: removed {len(stale)} rows that are no longer in {path.name}")
    return inserted


def main() -> int:
    backtest_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    csv_files = sorted(backtest_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {backtest_dir}")
        return 1

    conn = db.connect()
    for path in csv_files:
        scanner_name = path.stem
        inserted = import_file(conn, scanner_name, path)
        conn.commit()
        print(f"{scanner_name}: {inserted} new rows imported from {path.name}")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
