"""Fundamentals for scanner stocks from Yahoo Finance, in Screener's column names.

Every stock the Chartink scanners pick gets its fundamentals fetched (yfinance:
.info plus the annual income statement, balance sheet and cash flow) and
cached in chartink.db for REFRESH_DAYS. fundamentals.py scores them with the
Valuepick logic (valuepick_score.py), so the technical signal comes with a
fundamental check without any manual export.

Yahoo has no promoter holding as such: "heldPercentInsiders" (insiders and
promoters) stands in for it. Figures are in Rs crore like Screener's.

Run on GitHub Actions (needs Yahoo): python update_fundamentals.py
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone

import pandas as pd

import db
from market_data import to_yahoo_ticker

REFRESH_DAYS = 30
CR = 1e7  # rupees per crore


def _ensure(conn) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS fundamentals (symbol TEXT PRIMARY KEY, fetched_at TEXT NOT NULL, data TEXT NOT NULL)")


def _f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _row(df: pd.DataFrame | None, *names: str) -> list[float | None]:
    """Annual values of the first matching line, newest first."""
    if df is None or getattr(df, "empty", True):
        return []
    for n in names:
        if n in df.index:
            return [_f(v) for v in df.loc[n].tolist()]
    return []


def _growth(new, old) -> float | None:
    return round((new / old - 1) * 100, 1) if new is not None and old and old > 0 else None


def _cagr(vals: list, years: int = 3) -> float | None:
    if len(vals) <= years or vals[0] is None or vals[years] is None or vals[0] <= 0 or vals[years] <= 0:
        return None
    return round(((vals[0] / vals[years]) ** (1 / years) - 1) * 100, 1)


def to_screener(symbol: str, info: dict, inc=None, bal=None, cf=None, qinc=None) -> dict:
    """One Screener-style row (column names as in valuepick_score.COLS)."""
    rev = _row(inc, "Total Revenue", "Operating Revenue")
    ni = _row(inc, "Net Income", "Net Income Common Stockholders")
    ebit = _row(inc, "EBIT", "Operating Income")
    assets = _row(bal, "Total Assets")
    cur_liab = _row(bal, "Current Liabilities")
    debt = _row(bal, "Total Debt")
    recv = _row(bal, "Accounts Receivable", "Receivables")
    cfo = _row(cf, "Operating Cash Flow", "Cash Flow From Continuing Operating Activities")
    qni = _row(qinc, "Net Income", "Net Income Common Stockholders")  # quarterly, newest first
    opm = _f(info.get("operatingMargins"))
    if opm is None and ebit and rev and ebit[0] is not None and rev[0]:
        opm = ebit[0] / rev[0]

    roce = None
    if ebit and assets and cur_liab and ebit[0] is not None and assets[0] and cur_liab[0] is not None:
        ce = assets[0] - cur_liab[0]
        roce = round(ebit[0] / ce * 100, 1) if ce > 0 else None
    dd = [round(r / s * 365, 1) if (r is not None and s) else None for r, s in zip(recv, rev)]
    de = _f(info.get("debtToEquity"))
    out = {
        "Name": info.get("longName") or info.get("shortName") or symbol,
        "NSE Code": symbol,
        "Industry": info.get("industry") or "",
        "Current Price": _f(info.get("currentPrice")) or _f(info.get("regularMarketPrice")),
        "Market Capitalization": round(_f(info.get("marketCap")) / CR, 1) if _f(info.get("marketCap")) else None,
        "Price to Earning": _f(info.get("trailingPE")),
        "Return on capital employed": roce,
        "Return on equity": round(_f(info.get("returnOnEquity")) * 100, 1) if _f(info.get("returnOnEquity")) is not None else None,
        "Debt to equity": round(de / 100, 2) if de is not None else None,  # Yahoo gives it in %
        "Promoter holding": round(_f(info.get("heldPercentInsiders")) * 100, 1) if _f(info.get("heldPercentInsiders")) is not None else None,
        "Sales growth 3Years": _cagr(rev),
        "Profit growth 3Years": _cagr(ni),
        "Sales growth": _growth(rev[0], rev[1]) if len(rev) > 1 else None,
        "Profit growth": _growth(ni[0], ni[1]) if len(ni) > 1 else None,
        "Profit after tax": round(ni[0] / CR, 1) if ni and ni[0] is not None else None,
        "CFO": round(cfo[0] / CR, 1) if cfo and cfo[0] is not None else None,
        "Debt": round(debt[0] / CR, 1) if debt and debt[0] is not None else None,
        "Debt Change": round((debt[0] - debt[1]) / CR, 1) if len(debt) > 1 and None not in debt[:2] else None,
        "Debtor days": dd[0] if dd else None,
        "Debtor Days Ch": round(dd[0] - dd[1], 1) if len(dd) > 1 and None not in dd[:2] else None,
        "High price": _f(info.get("fiftyTwoWeekHigh")),
        "OPM": round(opm * 100, 1) if opm is not None else None,
        "YOY Quarterly profit growth": _growth(qni[0], qni[4]) if len(qni) > 4 else None,
        "Pledged percentage": None,  # not available from Yahoo
    }
    return {k: ("" if v is None else v) for k, v in out.items()}


def fetch(symbol: str) -> dict | None:
    import yfinance as yf
    t = yf.Ticker(to_yahoo_ticker(symbol))
    info = t.info or {}
    if not info.get("marketCap") and not info.get("longName"):
        return None

    def safe(attr):
        try:
            return getattr(t, attr)
        except Exception:
            return None
    return to_screener(symbol, info, safe("income_stmt"), safe("balance_sheet"), safe("cashflow"),
                       safe("quarterly_income_stmt"))


def cached(conn, symbol: str) -> dict | None:
    _ensure(conn)
    r = conn.execute("SELECT data FROM fundamentals WHERE symbol = ?", (symbol,)).fetchone()
    return json.loads(r[0]) if r else None


def refresh(conn, symbols: list[str], days: int = REFRESH_DAYS) -> int:
    """Fetch symbols with no data or data older than `days`. Returns how many were updated."""
    _ensure(conn)
    now = datetime.now(timezone.utc)
    done = 0
    for sym in sorted(set(symbols)):
        r = conn.execute("SELECT fetched_at, data FROM fundamentals WHERE symbol = ?", (sym,)).fetchone()
        # refetch when stale, or cached before OPM / quarterly growth were collected
        if r and (now - datetime.fromisoformat(r[0])).days < days and "OPM" in json.loads(r[1]):
            continue
        try:
            row = fetch(sym)
        except Exception as e:  # one bad symbol must not stop the rest
            print(f"  {sym}: fundamentals fetch failed ({e.__class__.__name__})")
            continue
        if row:
            conn.execute("INSERT OR REPLACE INTO fundamentals (symbol, fetched_at, data) VALUES (?, ?, ?)",
                         (sym, now.isoformat(), json.dumps(row)))
            done += 1
    conn.commit()
    return done
