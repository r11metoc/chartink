"""Fundamental scan: every stock in your uploaded Screener exports, ranked.

A separate module from the Chartink technical scan. It uses only the latest
Screener export uploaded from the app (data/fundamentals/uploads/; each upload
replaces the previous list) and scores each stock with your Valuepick
logic (valuepick_score.py) plus your main screen (main_screen.py). Shown under
More -> Fundamentals, best Valuepick score first.

Columns missing from an export simply aren't checked. P/E is worked out from
market cap / profit after tax when the export has no P/E column.
"""

from __future__ import annotations

import main_screen
import valuepick_score as vp
from fundamentals import FILE, export_rows


def _stocks(path=FILE) -> list[dict]:
    rows = export_rows(path)
    seen, out = set(), []
    for key, r in rows.items():
        if key == "_asof" or id(r) in seen or not str(r.get("Name") or "").strip():
            continue
        seen.add(id(r))
        out.append(r)
    return out


def score(row: dict) -> dict:
    vrow = row
    if "bank" in str(row.get("Industry", "")).lower():
        vrow = {**row, "Promoter holding": "", "Debtor days": "", "Debtor Days Ch": ""}
    v = vp.score_row(vrow)
    srow = row if str(row.get("Price to Earning") or "").strip() or v["pe"] is None else {**row, "Price to Earning": v["pe"]}
    s = main_screen.evaluate(srow)
    return {"name": v["name"], "code": v["code"], "industry": v["industry"],
            "score": v["score"], "verdict": v["verdict"], "flags": v["flags"], "entry": v["entry"],
            "coverage": v["coverage"], "pe": v["pe"], "peg": v["peg"], "roce": v["roce"],
            "promoter": v["promoter"], "mcap": v["mcap"], "from_high": v["from_high_pct"],
            "screen": {"passed": s["passed"], "checked": s["checked"], "total": s["total"],
                       "fails": s["fails"], "unknown": s["unknown"], "ok": s["ok"]}}


def view(path=FILE) -> dict | None:
    stocks = [score(r) for r in _stocks(path)]
    if not stocks:
        return None
    stocks.sort(key=lambda x: (x["score"] is None, -(x["score"] or 0)))
    for k, x in enumerate(stocks, 1):
        x["rank"] = k
    return {"asof": export_rows(path).get("_asof"), "stocks": stocks}
