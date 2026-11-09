"""Data checks shown on the Today page ("Data check").

Each scan re-checks the numbers the website shows, with code independent of
dipzone.py where it matters:
  - the latest scan is recent and found stocks on the scanners;
  - every held stock has prices up to the latest trading day;
  - every paper trade's buy and sell price lies inside that day's range, and
    each holding's return equals last close / buy - 1 - costs;
  - fundamentals: how many scanner stocks have Screener-page figures, and how
    old the oldest is.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

import db

COST_PCT = 0.25


def checks(conn, states: list[dict], last_scan_iso: str, scanners: list[dict]) -> dict:
    out: list[dict] = []

    def add(ok: bool, text: str):
        out.append({"ok": bool(ok), "text": text})

    age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(last_scan_iso)).total_seconds() / 3600
    n_on = sum(len(s["rows"]) for s in scanners)
    add(age_h < 80 and n_on > 0, f"Latest scan {age_h:.0f} h ago, {n_on} stocks on the scanners")

    trades = [s for s in states if "entry_date" in s]
    held = [s for s in trades if s.get("status") == "holding"]
    last = {s["symbol"]: str(s.get("last_date"))[:10] for s in held}
    newest = max(last.values()) if last else None
    stale = sorted(k for k, v in last.items() if v != newest)
    add(not stale, f"Prices up to {newest} for all {len(held)} holdings" if not stale
        else f"Prices behind for {', '.join(stale)} (others up to {newest})")

    bad = []
    for s in trades:
        bars = {d: (o, h, l, c) for d, o, h, l, c in db.daily_prices_since(conn, s["symbol"], str(s["entry_date"])[:10])}
        e = bars.get(str(s["entry_date"])[:10])
        if not e or not (e[2] - 0.01 <= s["entry"] <= e[1] + 0.01):
            bad.append(f"{s['symbol']} buy")
        if s.get("exit_date") is not None:
            x = bars.get(str(s["exit_date"])[:10])
            if not x or not (x[2] - 0.01 <= s["exit"] <= x[1] + 0.01):
                bad.append(f"{s['symbol']} sell")
        elif s.get("status") == "holding" and s.get("last_close"):
            ret = (s["last_close"] / s["entry"] - 1) * 100 - COST_PCT
            if abs(ret - s["ret"]) > 0.05:
                bad.append(f"{s['symbol']} return")
    add(not bad, f"All {len(trades)} paper trades match the daily prices" if not bad
        else "Price mismatch: " + ", ".join(bad))

    try:
        import screener_company
        syms = sorted({s["symbol"] for s in states})
        have = [screener_company.fetched_at(x) for x in syms]
        got = [h for h in have if h]
        if got:
            oldest = (datetime.now(timezone.utc).date() - pd.Timestamp(min(got)).date()).days
            add(len(got) >= 0.8 * len(syms) and oldest <= 45,
                f"Fundamentals from Screener for {len(got)}/{len(syms)} scanner stocks, oldest {oldest} days")
        else:
            add(False, "No Screener fundamentals yet (Yahoo used)")
    except Exception as e:  # never break the dashboard over a check
        add(False, f"Fundamentals check failed ({e.__class__.__name__})")
    return {"ok": all(c["ok"] for c in out), "checks": out}
