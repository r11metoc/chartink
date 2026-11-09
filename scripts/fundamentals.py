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
from datetime import datetime
from pathlib import Path

import main_screen
import valuepick_score as vp

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "fundamentals" / "latest.csv"
_export: dict | None = None
_yahoo: dict = {}


UPLOADS = FILE.parent / "uploads"


def _files(path: Path) -> list[Path]:
    """Only the newest export: a new upload replaces the old list completely
    (the app also deletes the older upload files). Falls back to latest.csv."""
    if path != FILE:
        return [path] if path.exists() else []
    ups = sorted(UPLOADS.glob("*.csv")) if UPLOADS.exists() else []
    return ups[-1:] or ([FILE] if FILE.exists() else [])


def export_rows(path: Path = FILE) -> dict:
    """NSE/BSE code -> raw Screener row from the newest export, plus '_asof'. {} without a file."""
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


def _auto_row(symbol: str) -> tuple[dict | None, str]:
    """Automatic source: the stock's Screener company page (cached, private),
    else Yahoo."""
    import screener_company
    row = screener_company.cached(symbol)
    return (row, "Screener page") if row else (_yahoo_row(symbol), "Yahoo")


def check(symbol: str, path: Path = FILE) -> dict | None:
    """Fundamental check for one stock, or None without data."""
    sym = str(symbol).strip().upper()
    scr = export_rows(path).get(sym)
    auto, asrc = _auto_row(sym) if path == FILE else (None, "")
    if not scr and not auto:
        return None
    # The uploaded export's numbers where it has them, the automatic source for the rest.
    row = {**(auto or {}), **{k: v for k, v in (scr or {}).items() if str(v or "").strip()}}
    src = f"Screener export + {asrc}" if scr and auto else "Screener export" if scr else asrc
    bank = "bank" in str(row.get("Industry", "")).lower()
    if bank:
        # Banks: operating margin and debt/equity don't apply (deposits are their raw
        # material) and ROE is the return measure, not ROCE.
        row = {**row, "OPM": "", "Debt to equity": "", "Debtor days": "", "Debtor Days Ch": "",
               "Return on capital employed": row.get("Return on equity", "")}
    screen = main_screen.evaluate(row)
    if bank:  # say ROE where ROE was checked
        screen["fails"] = [("ROE" + f[4:]) if f.startswith("ROCE ") else f for f in screen["fails"]]
        screen["fail_labels"] = ["ROE" if x == "ROCE" else x for x in screen["fail_labels"]]
    vrow = row
    if "bank" in str(row.get("Industry", "")).lower():
        # Banks: widely held (no promoter) and loans are not trade receivables.
        vrow = {**row, "Promoter holding": "", "Debtor days": "", "Debtor Days Ch": ""}
    v = vp.score_row(vrow)
    asof = None
    if "Screener page" in src:
        import screener_company
        asof = screener_company.fetched_at(sym)
    return {"source": src, "private": "Screener page" in src, "bank": bank, "asof": asof, "screen": screen,
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
