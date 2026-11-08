"""Fundamental check for scanner stocks (Valuepick score, information only).

Every stock the Chartink scanners pick has its fundamentals fetched from
Yahoo Finance (yahoo_fundamentals.py, cached in chartink.db) and scored with
the Valuepick logic (valuepick_score.py): score 0-100, verdict (Shortlist /
Maybe / Skip / Reject) and red flags, shown on every buy-stop alert and
holding. A Screener.in export at data/fundamentals/latest.csv, if present,
takes priority for the stocks it covers (it has ROCE and promoter holding
straight from Screener). It never changes a buy or sell: the price rule
decides, this adds confidence or caution.

There is no point-in-time history of fundamentals, so this cannot be
backtested; judge it on live results.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import valuepick_score as vp

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "fundamentals" / "latest.csv"
_cache: dict | None = None


def scores(path: Path = FILE) -> dict:
    """NSE/BSE code -> Valuepick result, plus '_asof' (file date). {} without a file."""
    global _cache
    if _cache is not None and path == FILE:
        return _cache
    out: dict = {}
    if path.exists():
        try:
            for r in vp.score_file(str(path)):
                if r.get("code"):
                    out[str(r["code"]).strip().upper()] = r
            out["_asof"] = datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
        except Exception as e:  # a bad export must never stop the scan
            print(f"Fundamentals file unreadable ({e}); skipping the fundamental check")
            out = {}
    if path == FILE:
        _cache = out
    return out


_yahoo: dict = {}


def _from_yahoo(symbol: str) -> dict | None:
    if symbol not in _yahoo:
        import db
        import yahoo_fundamentals
        conn = db.connect()
        try:
            row = yahoo_fundamentals.cached(conn, symbol)
        finally:
            conn.close()
        if row and "bank" in str(row.get("Industry", "")).lower():
            # Banks: widely held (no promoter) and loans are not trade receivables,
            # so promoter holding and debtor days would give false rejects/flags.
            row = {**row, "Promoter holding": "", "Debtor days": "", "Debtor Days Ch": ""}
        r = vp.score_row(row) if row else None
        _yahoo[symbol] = r if r and r.get("score") is not None else None
    return _yahoo[symbol]


def check(symbol: str, path: Path = FILE) -> dict | None:
    """Compact fundamental check for one stock: the Screener export if it has
    the stock, else the Yahoo data fetched for it; None if neither."""
    sym = str(symbol).strip().upper()
    r = scores(path).get(sym)
    src = "Screener"
    if not r and path == FILE:
        r, src = _from_yahoo(sym), "Yahoo"
    if not r:
        return None
    return {"score": r["score"], "verdict": r["verdict"], "flags": r["flags"], "source": src,
            "pe": r["pe"], "roce": r["roce"], "promoter": r["promoter"]}


def label(f: dict | None) -> str:
    """Short text for alerts: 'Fundamentals 72 Shortlist' (+ flags)."""
    if not f:
        return ""
    t = f"Fundamentals {f['score']:.0f} {f['verdict']}"
    return t + (f" ({f['flags']})" if f.get("flags") else "")
