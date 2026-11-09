"""Market pulse and upcoming results, for the Today page (context only).

Market pulse: Nifty 50 and Nifty 500 against their 50- and 200-day averages,
India VIX, the share of the bot's tracked stocks above their own 50-day
average, and the sectors gaining or losing scanner picks. The backtest found
that a Nifty trend filter did NOT improve the rule, so this never changes a
buy or sell; it's there to read the market.

Upcoming results: BSE's forthcoming-results calendar (one request a day,
api.bseindia.com, the same call bseindia.com's own page makes), matched to the
stocks you hold or have a buy-stop on by BSE symbol, BSE code or the BSE code
read from the stock's Screener page.

Run on GitHub Actions each scan: python market.py (refreshes the calendar).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import db

INDEXES = {"^NSEI": "Nifty 50", "^CRSLDX": "Nifty 500"}
VIX = "^INDIAVIX"
CAL_URL = "https://api.bseindia.com/BseIndiaAPI/api/Corpforthresults/w?scripcode=&FromDate=&ToDate="
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Referer": "https://www.bseindia.com/", "Accept": "application/json"}
EVENT_DAYS = 7


def _ensure(conn) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS results_calendar (code TEXT, short_name TEXT, name TEXT, "
                 "meeting_date TEXT, fetched_at TEXT)")


def refresh_calendar(conn, get=None) -> int:
    """Replace the stored calendar with BSE's current one (at most once every 12 hours)."""
    _ensure(conn)
    last = conn.execute("SELECT MAX(fetched_at) FROM results_calendar").fetchone()[0]
    now = datetime.now(timezone.utc)
    if last and now - datetime.fromisoformat(last) < timedelta(hours=12):
        return 0
    if get is None:
        import requests
        get = lambda url: requests.get(url, headers=HEADERS, timeout=30)  # noqa: E731
    r = get(CAL_URL)
    r.raise_for_status()
    rows = []
    for x in r.json():
        try:
            d = datetime.strptime(x["meeting_date"], "%d %b %Y").date().isoformat()
        except (KeyError, ValueError):
            continue
        rows.append((str(x.get("scrip_Code", "")).strip(), str(x.get("short_name", "")).strip().upper(),
                     x.get("Long_Name", ""), d, now.isoformat()))
    if rows:
        conn.execute("DELETE FROM results_calendar")
        conn.executemany("INSERT INTO results_calendar VALUES (?, ?, ?, ?, ?)", rows)
        conn.commit()
    return len(rows)


def upcoming_results(conn, symbols: list[str], days: int = EVENT_DAYS, today: date | None = None) -> dict:
    """symbol -> results/board-meeting date within `days` (inclusive of today)."""
    _ensure(conn)
    today = today or datetime.now(timezone(timedelta(hours=5, minutes=30))).date()
    until = (today + timedelta(days=days)).isoformat()
    cal = conn.execute("SELECT code, short_name, meeting_date FROM results_calendar "
                       "WHERE meeting_date >= ? AND meeting_date <= ?", (today.isoformat(), until)).fetchall()
    by_name = {s: d for _, s, d in cal}
    by_code = {c: d for c, _, d in cal}
    try:
        import screener_company
    except Exception:  # pragma: no cover
        screener_company = None
    out = {}
    for sym in symbols:
        d = by_name.get(sym) or by_code.get(sym)
        if not d and screener_company is not None:
            row = screener_company.cached(sym) or {}
            d = by_code.get(str(row.get("BSE Code", "")).strip())
        if d:
            out[sym] = d
    return out


def _closes(conn, symbol: str, days: int = 420) -> list[float]:
    since = (date.today() - timedelta(days=days)).isoformat()
    return [b[4] for b in db.daily_prices_since(conn, symbol, since)]


def _vs(closes: list[float], n: int) -> float | None:
    if len(closes) < n:
        return None
    return round((closes[-1] / (sum(closes[-n:]) / n) - 1) * 100, 1)


def pulse(conn, sector_momentum: dict | None = None) -> dict:
    idx = []
    for sym, name in INDEXES.items():
        c = _closes(conn, sym)
        if len(c) < 2:
            continue
        idx.append({"name": name, "close": round(c[-1], 1), "day": round((c[-1] / c[-2] - 1) * 100, 2),
                    "month": round((c[-1] / c[-22] - 1) * 100, 1) if len(c) > 22 else None,
                    "vs50": _vs(c, 50), "vs200": _vs(c, 200)})
    v = _closes(conn, VIX, 30)
    vix = {"level": round(v[-1], 1), "day": round(v[-1] - v[-2], 1) if len(v) > 1 else None} if v else None

    # Breadth: the bot's tracked stocks with fresh prices, above their own 50-day average.
    recent = (date.today() - timedelta(days=5)).isoformat()
    syms = [s for (s,) in conn.execute("SELECT DISTINCT symbol FROM daily_prices WHERE date >= ? AND symbol NOT LIKE '^%'",
                                       (recent,))]
    above = total = 0
    for s in syms:
        c = _closes(conn, s, 110)
        if len(c) >= 50:
            total += 1
            above += c[-1] > sum(c[-50:]) / 50
    breadth = {"above": above, "total": total, "pct": round(100 * above / total) if total else None}

    trend = None
    if idx and idx[0]["vs50"] is not None and idx[0]["vs200"] is None:
        trend = "Above 50-day average" if idx[0]["vs50"] > 0 else "Below 50-day average"
    if idx and idx[0]["vs50"] is not None and idx[0]["vs200"] is not None:
        a50, a200 = idx[0]["vs50"] > 0, idx[0]["vs200"] > 0
        trend = ("Uptrend" if a50 and a200 else "Pullback in an uptrend" if a200 else
                 "Recovering" if a50 else "Downtrend")
    mood = None
    if vix:
        mood = "calm" if vix["level"] < 13 else "normal" if vix["level"] < 18 else "nervous" if vix["level"] < 25 else "fearful"

    up = down = []
    if sector_momentum and sector_momentum.get("rows"):
        rows = [r for r in sector_momentum["rows"] if r["sector"].lower() != "unclassified"]
        up = [r["sector"] for r in sorted(rows, key=lambda r: r["cur"] - r["prev"], reverse=True) if r["cur"] > r["prev"]][:3]
        down = [r["sector"] for r in sorted(rows, key=lambda r: r["cur"] - r["prev"]) if r["cur"] < r["prev"]][:3]
    return {"indexes": idx, "vix": vix, "breadth": breadth, "trend": trend, "mood": mood,
            "sectors_up": up, "sectors_down": down}


def main() -> int:
    conn = db.connect()
    try:
        n = refresh_calendar(conn)
        print(f"Results calendar: {n} entries" if n else "Results calendar: fresh, not refetched")
    except Exception as e:  # never cost the scan
        print(f"Results calendar fetch failed ({e.__class__.__name__}); Today shows no result dates")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
