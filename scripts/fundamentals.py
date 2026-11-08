"""Fundamental check for scanner stocks (Valuepick score, information only).

Drop a Screener.in export at data/fundamentals/latest.csv (any screen with
some of the columns in valuepick_score.COLS; one row per stock). Every scan
then tags each buy-stop alert and holding with its Valuepick score (0-100),
verdict (Shortlist / Maybe / Skip / Reject) and red flags. It never changes a
buy or sell: the price rule decides, this adds confidence or caution.

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


def check(symbol: str, path: Path = FILE) -> dict | None:
    """Compact fundamental check for one stock, or None if it isn't in the export."""
    r = scores(path).get(str(symbol).strip().upper())
    if not r:
        return None
    return {"score": r["score"], "verdict": r["verdict"], "flags": r["flags"],
            "pe": r["pe"], "roce": r["roce"], "promoter": r["promoter"]}


def label(f: dict | None) -> str:
    """Short text for alerts: 'Fundamentals 72 Shortlist' (+ flags)."""
    if not f:
        return ""
    t = f"Fundamentals {f['score']:.0f} {f['verdict']}"
    return t + (f" ({f['flags']})" if f.get("flags") else "")
