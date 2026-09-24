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
CREATE INDEX IF NOT EXISTS idx_breakouts_detected_at ON breakouts(detected_at);

CREATE TABLE IF NOT EXISTS backtest_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanner_name TEXT NOT NULL,
    hit_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    marketcap TEXT NOT NULL,
    sector TEXT NOT NULL,
    UNIQUE(scanner_name, hit_date, symbol)
);
CREATE INDEX IF NOT EXISTS idx_backtest_scanner_symbol ON backtest_hits(scanner_name, symbol);
"""


def _migrate(conn: sqlite3.Connection) -> None:
    """Add columns to tables created before this field existed."""
    cols = {row[1] for row in conn.execute("PRAGMA table_info(breakouts)")}
    if "kind" not in cols:
        # 'fresh' = symbol never seen before on this scanner; 'retest' = it
        # was seen before, dropped out for at least one run, and is back -
        # i.e. the scan condition re-triggered at the same technical level.
        conn.execute("ALTER TABLE breakouts ADD COLUMN kind TEXT NOT NULL DEFAULT 'fresh'")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    _migrate(conn)
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


def has_appeared_before(conn: sqlite3.Connection, scanner_name: str, symbol: str, before_run_id: int) -> bool:
    """True if this symbol was ever in this scanner's results in an earlier run
    (used to tell a genuinely-first-time breakout apart from a retest)."""
    cur = conn.execute(
        "SELECT 1 FROM results WHERE scanner_name = ? AND symbol = ? AND run_id < ? LIMIT 1",
        (scanner_name, symbol, before_run_id),
    )
    return cur.fetchone() is not None


def record_breakout(conn: sqlite3.Connection, run_id: int, scanner_name: str, symbol: str, row: dict, kind: str = "fresh") -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO breakouts (run_id, scanner_name, symbol, detected_at, row_json, kind) VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, scanner_name, symbol, now, json.dumps(row, ensure_ascii=False), kind),
    )


def latest_row(conn: sqlite3.Connection, scanner_name: str, symbol: str) -> dict | None:
    """Most recently scraped row for this symbol on this scanner - used as
    'current price' for comparing against a stored breakout's trigger price.
    Only as fresh as the last time this symbol actually appeared in the scan;
    if it has since dropped out entirely, this is stale, not live."""
    cur = conn.execute(
        "SELECT row_json FROM results WHERE scanner_name = ? AND symbol = ? "
        "ORDER BY run_id DESC LIMIT 1",
        (scanner_name, symbol),
    )
    row = cur.fetchone()
    return json.loads(row[0]) if row else None


def import_backtest_hit(conn: sqlite3.Connection, scanner_name: str, hit_date: str, symbol: str, marketcap: str, sector: str) -> bool:
    """Returns True if a new row was inserted (False if it already existed)."""
    cur = conn.execute(
        "INSERT OR IGNORE INTO backtest_hits (scanner_name, hit_date, symbol, marketcap, sector) "
        "VALUES (?, ?, ?, ?, ?)",
        (scanner_name, hit_date, symbol, marketcap, sector),
    )
    return cur.rowcount > 0


def backtest_history(conn: sqlite3.Connection, scanner_name: str, symbol: str) -> list[str]:
    """All historical backtest dates this exact symbol triggered on this scanner."""
    cur = conn.execute(
        "SELECT hit_date FROM backtest_hits WHERE scanner_name = ? AND symbol = ? ORDER BY hit_date",
        (scanner_name, symbol),
    )
    return [r[0] for r in cur.fetchall()]


def backtest_sector_share(conn: sqlite3.Connection, scanner_name: str, sector: str) -> tuple[int, int] | None:
    """(hits for this sector, total hits) for this scanner, matching sector
    case-insensitively and loosely (either string contains the other) since
    live scan 'Industry' labels don't exactly match backtest 'Sector' labels."""
    total = conn.execute(
        "SELECT COUNT(*) FROM backtest_hits WHERE scanner_name = ?", (scanner_name,)
    ).fetchone()[0]
    if total == 0 or not sector:
        return None
    sector_low = sector.lower()
    cur = conn.execute("SELECT sector FROM backtest_hits WHERE scanner_name = ?", (scanner_name,))
    matches = sum(
        1 for (s,) in cur.fetchall()
        if s and (s.lower() in sector_low or sector_low in s.lower())
    )
    return (matches, total)


def distinct_backtest_scanners(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute("SELECT DISTINCT scanner_name FROM backtest_hits ORDER BY scanner_name")
    return [r[0] for r in cur.fetchall()]


def sector_counts_since(conn: sqlite3.Connection, scanner_name: str, since_date: str, limit: int = 5) -> list[tuple[str, int]]:
    """Top sectors by backtest hit count for this scanner since since_date (ISO date)."""
    cur = conn.execute(
        "SELECT sector, COUNT(*) AS n FROM backtest_hits "
        "WHERE scanner_name = ? AND hit_date >= ? GROUP BY sector ORDER BY n DESC LIMIT ?",
        (scanner_name, since_date, limit),
    )
    return [(r[0], r[1]) for r in cur.fetchall()]


def breakouts_since(conn: sqlite3.Connection, since_iso: str) -> list[dict]:
    cur = conn.execute(
        "SELECT scanner_name, symbol, kind, detected_at, row_json FROM breakouts "
        "WHERE detected_at >= ? ORDER BY detected_at DESC",
        (since_iso,),
    )
    out = []
    for scanner_name, symbol, kind, detected_at, row_json in cur.fetchall():
        entry = json.loads(row_json)
        entry.update(scanner_name=scanner_name, symbol=symbol, kind=kind, detected_at=detected_at)
        out.append(entry)
    return out
