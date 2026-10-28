"""Market-cap tier of a stock: the latest tier in the Chartink backtest
exports, else from its market cap in crore (used for the mid-cap-first
slot priority)."""

from __future__ import annotations

LARGECAP_CR, MIDCAP_CR = 100_000, 30_000


def tier_of(conn, symbol: str, mcap_cr: float | None = None) -> str | None:
    row = conn.execute(
        "SELECT marketcap FROM backtest_hits WHERE symbol = ? AND marketcap != '' ORDER BY hit_date DESC LIMIT 1",
        (symbol,)).fetchone()
    if row:
        return row[0]
    if mcap_cr is None:
        return None
    return "Largecap" if mcap_cr >= LARGECAP_CR else "Midcap" if mcap_cr >= MIDCAP_CR else "Smallcap"
