"""Live and backtest signals since a date, and daily price frames from the DB.

Used by the live breakout rule (dipzone.py) and the dataset builder."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

import db
from slot_gate import IST

MARKET_OPEN = (9, 15)


def _frame(conn, symbol: str, since: str) -> pd.DataFrame:
    rows = db.daily_prices_since(conn, symbol, since)
    df = pd.DataFrame(rows, columns=["date", "Open", "High", "Low", "Close"])
    df.index = pd.to_datetime(df.pop("date"))
    return df


def live_hit_date(detected_at: str) -> str:
    """The session a live trigger belongs to: before the open the scanner
    still shows the previous session's result."""
    t = datetime.fromisoformat(detected_at).astimezone(IST)
    return (t - timedelta(days=1) if (t.hour, t.minute) < MARKET_OPEN else t).date().isoformat()


def _signals(conn, start_day: str) -> list[tuple[str, str, str, str]]:
    """(hit_date, scanner, symbol, source), one per scanner/symbol/day."""
    seen: dict[tuple[str, str, str], str] = {}
    start = datetime.fromisoformat(start_day).replace(tzinfo=IST)
    for e in db.breakouts_since(conn, start.isoformat()):
        seen.setdefault((live_hit_date(e["detected_at"]), e["scanner_name"], e["symbol"]), "live")
    for scanner, symbol, day in conn.execute(
            "SELECT scanner_name, symbol, hit_date FROM backtest_hits WHERE hit_date >= ?", (start_day,)):
        seen.setdefault((day, scanner, symbol), "backtest export")
    return sorted((d, sc, sym, src) for (d, sc, sym), src in seen.items())
