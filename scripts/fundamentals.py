"""Fundamental check for scanner stocks (information only).

For every stock the Chartink scanners pick:
  1. your main screen (main_screen.py): pass / fail on each of its 11
     conditions, with the reasons it fails;
  2. the Valuepick score (valuepick_score.py): 0-100, verdict and red flags.

Data: Yahoo Finance, fetched automatically each scan (yahoo_fundamentals.py,
cached 30 days in chartink.db). A Screener.in export at
data/fundamentals/latest.csv, if present, takes priority for the stocks it
covers (Screener has pledge, promoter holding and ROCE directly).
It never changes a buy or sell; it cannot be backtested (no point-in-time
fundamentals).
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path

import main_screen
import valuepick_score as vp

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "fundamentals" / "latest.csv"
_export: dict | None = None
_yahoo: dict = {}


UPLOADS = FILE.parent / "uploads"
MAX_AGE_DAYS = 180


def _files(path: Path) -> list[Path]:
    """Exports oldest first: latest.csv, then the app's uploads by name (= time),
    skipping uploads older than MAX_AGE_DAYS."""
    if path != FILE:
        return [path] if path.exists() else []
    cutoff = (datetime.now() - timedelta(days=MAX_AGE_DAYS)).strftime("%Y-%m-%d")
    ups = sorted(p for p in UPLOADS.glob("*.csv") if p.name[:10] >= cutoff) if UPLOADS.exists() else []
    return ([FILE] if FILE.exists() else []) + ups


def export_rows(path: Path = FILE) -> dict:
    """NSE/BSE code -> raw Screener row (newest export wins), plus '_asof'. {} without a file."""
    global _export
    if _export is not None and path == FILE:
        return _export
    out: dict = {}
    files = _files(path)
    for f in files:
        try:
            with open(f, newline="", encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh):
                    for key in ("NSE Code", "BSE Code"):
                        code = str(r.get(key) or "").strip().upper()
                        if code:
                            out[code] = r
        except Exception as e:  # a bad export must never stop the scan
            print(f"Fundamentals file {f.name} unreadable ({e}); skipped")
    if out and files:
        last = files[-1]
        out["_asof"] = (last.name[:10] if last.parent == UPLOADS
                        else datetime.fromtimestamp(last.stat().st_mtime).date().isoformat())
    if path == FILE:
        _export = out
    return out


def scores(path: Path = FILE) -> dict:
    """Kept for the dashboard: only '_asof' of the export is used."""
    return {"_asof": export_rows(path).get("_asof")}


def _yahoo_row(symbol: str) -> dict | None:
    if symbol not in _yahoo:
        import db
        import yahoo_fundamentals
        conn = db.connect()
        try:
            _yahoo[symbol] = yahoo_fundamentals.cached(conn, symbol)
        finally:
            conn.close()
    return _yahoo[symbol]


def check(symbol: str, path: Path = FILE) -> dict | None:
    """Fundamental check for one stock, or None without data."""
    sym = str(symbol).strip().upper()
    scr = export_rows(path).get(sym)
    yh = _yahoo_row(sym) if path == FILE else None
    if not scr and not yh:
        return None
    # Screener's numbers where the export has them, Yahoo's for the columns it lacks.
    row = {**(yh or {}), **{k: v for k, v in (scr or {}).items() if str(v or "").strip()}}
    src = "Screener + Yahoo" if scr and yh else "Screener" if scr else "Yahoo"
    screen = main_screen.evaluate(row)
    vrow = row
    if "bank" in str(row.get("Industry", "")).lower():
        # Banks: widely held (no promoter) and loans are not trade receivables.
        vrow = {**row, "Promoter holding": "", "Debtor days": "", "Debtor Days Ch": ""}
    v = vp.score_row(vrow)
    return {"source": src, "screen": screen,
            "score": v.get("score"), "verdict": v.get("verdict"), "flags": v.get("flags"),
            "pe": v.get("pe"), "roce": v.get("roce"), "promoter": v.get("promoter")}


def label(f: dict | None) -> str:
    """Short text for alerts: your screen first, then the Valuepick score."""
    if not f:
        return ""
    parts = [main_screen.label(f["screen"])]
    if f.get("score") is not None:
        parts.append(f"Valuepick {f['score']:.0f} {f['verdict']}" + (f" ({f['flags']})" if f.get("flags") else ""))
    return " · ".join(p for p in parts if p)
