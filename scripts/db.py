"""SQLite storage for scan runs and breakout detection.

Schema:
  runs(id, run_at)                                  -- one row per scrape
  results(id, run_id, scanner_name, symbol, row_json) -- every symbol seen in a run
  breakouts(id, run_id, scanner_name, symbol, detected_at, row_json)
                                                      -- symbols new to a scanner vs its previous run
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chartink.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    scanner_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    row_json TEXT NOT NULL,
    UNIQUE(run_id, scanner_name, symbol)
);
CREATE INDEX IF NOT EXISTS idx_results_scanner_run ON results(scanner_name, run_id);

CREATE TABLE IF NOT EXISTS breakouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    scanner_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    row_json TEXT NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn


def create_run(conn: sqlite3.Connection) -> int:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO runs (run_at) VALUES (?)", (now,))
    return cur.lastrowid


def save_results(conn: sqlite3.Connection, run_id: int, scanner_name: str, rows: list[dict]) -> None:
    for row in rows:
        symbol = row.get("_symbol", "").strip()
        if not symbol:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO results (run_id, scanner_name, symbol, row_json) VALUES (?, ?, ?, ?)",
            (run_id, scanner_name, symbol, json.dumps(row, ensure_ascii=False)),
        )


def previous_run_id(conn: sqlite3.Connection, scanner_name: str, before_run_id: int) -> int | None:
    cur = conn.execute(
        "SELECT DISTINCT run_id FROM results WHERE scanner_name = ? AND run_id < ? "
        "ORDER BY run_id DESC LIMIT 1",
        (scanner_name, before_run_id),
    )
    row = cur.fetchone()
    return row[0] if row else None


def symbols_for_run(conn: sqlite3.Connection, scanner_name: str, run_id: int) -> set[str]:
    cur = conn.execute(
        "SELECT symbol FROM results WHERE scanner_name = ? AND run_id = ?",
        (scanner_name, run_id),
    )
    return {r[0] for r in cur.fetchall()}


def record_breakout(conn: sqlite3.Connection, run_id: int, scanner_name: str, symbol: str, row: dict) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO breakouts (run_id, scanner_name, symbol, detected_at, row_json) VALUES (?, ?, ?, ?, ?)",
        (run_id, scanner_name, symbol, now, json.dumps(row, ensure_ascii=False)),
    )
