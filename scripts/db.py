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

CREATE TABLE IF NOT EXISTS backtest_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scanner_name TEXT NOT NULL,
    hit_date TEXT NOT NULL,
    symbol TEXT NOT NULL,
    trigger_close REAL NOT NULL,
    future_close REAL NOT NULL,
    pct_return REAL NOT NULL,
    label INTEGER NOT NULL,
    horizon_days INTEGER NOT NULL,
    success_threshold_pct REAL NOT NULL,
    computed_at TEXT NOT NULL,
    UNIQUE(scanner_name, hit_date, symbol, horizon_days, success_threshold_pct)
);
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


def _load_row(row_json: str) -> dict:
    # Rows from the earliest runs were saved with headers like
    # "Price\nSort table by Price in ascending order"; keep just the label so
    # they compare against current rows.
    return {k.split("\n", 1)[0]: v for k, v in json.loads(row_json).items()}


def latest_breakout_row(conn: sqlite3.Connection, scanner_name: str, symbol: str) -> dict | None:
    cur = conn.execute(
        "SELECT row_json FROM breakouts WHERE scanner_name = ? AND symbol = ? "
        "ORDER BY detected_at DESC LIMIT 1",
        (scanner_name, symbol),
    )
    row = cur.fetchone()
    return _load_row(row[0]) if row else None


def first_seen_row(conn: sqlite3.Connection, scanner_name: str, symbol: str) -> dict | None:
    cur = conn.execute(
        "SELECT row_json FROM results WHERE scanner_name = ? AND symbol = ? "
        "ORDER BY run_id ASC LIMIT 1",
        (scanner_name, symbol),
    )
    row = cur.fetchone()
    return _load_row(row[0]) if row else None


def trigger_row(conn: sqlite3.Connection, scanner_name: str, symbol: str) -> dict | None:
    """Best-known 'trigger price' row for a currently-active symbol: the
    most recent breakout event if one was ever recorded for it (correctly
    captures a retest's re-entry price), otherwise the earliest known
    results row for this scanner+symbol (covers symbols that have been on
    the scan since before formal breakout tracking started, e.g. a
    baseline-seeding run)."""
    row = latest_breakout_row(conn, scanner_name, symbol)
    if row is not None:
        return row
    return first_seen_row(conn, scanner_name, symbol)


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
    return _load_row(row[0]) if row else None


def symbols_in_latest_run(conn: sqlite3.Connection, scanner_name: str) -> set[str]:
    cur = conn.execute(
        "SELECT symbol FROM results WHERE scanner_name = ? AND run_id = (SELECT MAX(id) FROM runs)",
        (scanner_name,),
    )
    return {r[0] for r in cur.fetchall()}


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


def distinct_backtest_symbols(conn: sqlite3.Connection) -> list[str]:
    cur = conn.execute("SELECT DISTINCT symbol FROM backtest_hits ORDER BY symbol")
    return [r[0] for r in cur.fetchall()]


def all_backtest_hits(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """All (scanner_name, hit_date, symbol) rows - used to compute outcomes."""
    cur = conn.execute("SELECT scanner_name, hit_date, symbol FROM backtest_hits")
    return cur.fetchall()


def earliest_backtest_date(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT MIN(hit_date) FROM backtest_hits").fetchone()
    return row[0] if row else None


def save_backtest_outcome(
    conn: sqlite3.Connection, scanner_name: str, hit_date: str, symbol: str,
    trigger_close: float, future_close: float, pct_return: float, label: int,
    horizon_days: int, success_threshold_pct: float,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO backtest_outcomes "
        "(scanner_name, hit_date, symbol, trigger_close, future_close, pct_return, label, "
        " horizon_days, success_threshold_pct, computed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scanner_name, hit_date, symbol, trigger_close, future_close, pct_return, label,
         horizon_days, success_threshold_pct, now),
    )


def outcomes_with_context(conn: sqlite3.Connection, horizon_days: int, success_threshold_pct: float) -> list[dict]:
    """Join backtest_outcomes with backtest_hits (sector/marketcap) for a
    given labeling rule, in chronological order - the training/reporting dataset."""
    cur = conn.execute(
        "SELECT o.scanner_name, o.hit_date, o.symbol, o.trigger_close, o.future_close, "
        "       o.pct_return, o.label, h.marketcap, h.sector "
        "FROM backtest_outcomes o "
        "JOIN backtest_hits h ON h.scanner_name = o.scanner_name "
        "                    AND h.hit_date = o.hit_date AND h.symbol = o.symbol "
        "WHERE o.horizon_days = ? AND o.success_threshold_pct = ? "
        "ORDER BY o.hit_date",
        (horizon_days, success_threshold_pct),
    )
    cols = ["scanner_name", "hit_date", "symbol", "trigger_close", "future_close", "pct_return", "label", "marketcap", "sector"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def breakouts_since(conn: sqlite3.Connection, since_iso: str) -> list[dict]:
    cur = conn.execute(
        "SELECT scanner_name, symbol, kind, detected_at, row_json FROM breakouts "
        "WHERE detected_at >= ? ORDER BY detected_at DESC",
        (since_iso,),
    )
    out = []
    for scanner_name, symbol, kind, detected_at, row_json in cur.fetchall():
        entry = _load_row(row_json)
        entry.update(scanner_name=scanner_name, symbol=symbol, kind=kind, detected_at=detected_at)
        out.append(entry)
    return out
