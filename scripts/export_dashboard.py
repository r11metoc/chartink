"""Write site/data.json for the web dashboard (site/index.html).

Three views:
  scanners   every stock on each scanner in the latest scan, BUY/HOLD vs trigger
  breakouts  every trigger in the last WINDOW_DAYS with its move since then,
             using daily prices (refresh_prices.py) when available, else the
             last scan price
  sectors    backtest picks per sector, last 7 and 30 days
  sector_momentum
             all scanners combined: distinct stocks picked per sector in the
             last 2 weeks vs the 2 before, scanners agreeing, average move
             since pick, and weekly counts for a sparkline
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import db
from notify import _col, _num, _price
from slot_gate import IST, SLOTS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "data.json"
WINDOW_DAYS = 90
MOMENTUM_DAYS = 14
WEEKS = 8
UNCLASSIFIED = "Unclassified"


def _ist(iso: str) -> datetime:
    return datetime.fromisoformat(iso).astimezone(IST)


def _pct(a: float | None, b: float | None) -> float | None:
    return round((b - a) / a * 100, 2) if a and b is not None else None


def trigger_info(conn, scanner: str, symbol: str) -> tuple[dict | None, str | None]:
    """(trigger row, when) - latest breakout, else the first time it was seen."""
    r = conn.execute(
        "SELECT row_json, detected_at FROM breakouts WHERE scanner_name = ? AND symbol = ? "
        "ORDER BY detected_at DESC LIMIT 1", (scanner, symbol)).fetchone()
    if r is None:
        r = conn.execute(
            "SELECT res.row_json, runs.run_at FROM results res JOIN runs ON runs.id = res.run_id "
            "WHERE res.scanner_name = ? AND res.symbol = ? ORDER BY res.run_id LIMIT 1",
            (scanner, symbol)).fetchone()
    return (db._load_row(r[0]), r[1]) if r else (None, None)


def scanners_view(conn, latest_run: int) -> list[dict]:
    names = set(db.distinct_backtest_scanners(conn))
    names |= {n for (n,) in conn.execute("SELECT DISTINCT scanner_name FROM results WHERE run_id = ?", (latest_run,))}
    out = []
    for name in sorted(names):
        rows = []
        for symbol, row_json in conn.execute(
                "SELECT symbol, row_json FROM results WHERE run_id = ? AND scanner_name = ?", (latest_run, name)):
            row = db._load_row(row_json)
            trigger, when = trigger_info(conn, name, symbol)
            now, trig = _price(row), _price(trigger)
            chg = _pct(trig, now)
            rows.append({
                "symbol": symbol,
                "industry": _col(row, "industry"),
                "now": now,
                "day_chg": _num(_col(row, "%")),
                "trigger": trig,
                "trigger_date": _ist(when).date().isoformat() if when else None,
                "chg": chg,
                "status": "BUY" if chg is not None and chg > 0 else "HOLD",
            })
        rows.sort(key=lambda r: r["chg"] if r["chg"] is not None else -1e9, reverse=True)
        out.append({"name": name, "rows": rows})
    return out


def breakouts_view(conn, latest_run: int) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()
    on_scan = {(n, s) for n, s in conn.execute(
        "SELECT scanner_name, symbol FROM results WHERE run_id = ?", (latest_run,))}
    out = []
    for e in db.breakouts_since(conn, since):
        name, symbol = e["scanner_name"], e["symbol"]
        trig = _price(e)
        when = _ist(e["detected_at"])
        bars = db.daily_prices_since(conn, symbol, when.date().isoformat())
        # Best/worst count from the next session: the trigger day's high or low
        # may have come before the stock triggered.
        after = [b for b in bars if b[0] > when.date().isoformat()]
        if bars:
            now, now_date = round(bars[-1][4], 2), bars[-1][0]
            best = max(b[2] for b in after) if after else None
            worst = min(b[3] for b in after) if after else None
            days = len(after)
        else:
            current = db.latest_row(conn, name, symbol)
            now, now_date = _price(current), None
            best = worst = None
            days = None
        chg = _pct(trig, now)
        out.append({
            "scanner": name,
            "symbol": symbol,
            "kind": e["kind"],
            "date": when.date().isoformat(),
            "time": when.strftime("%H:%M"),
            "trigger": trig,
            "now": now,
            "now_date": now_date,
            "chg": chg,
            "best_chg": _pct(trig, best),
            "worst_chg": _pct(trig, worst),
            "days": days,
            "on_scan": (name, symbol) in on_scan,
            "status": "BUY" if chg is not None and chg > 0 else "HOLD",
        })
    return out


def stats_view(breakouts: list[dict]) -> list[dict]:
    by_scanner: dict[str, list[dict]] = {}
    for b in breakouts:
        if b["chg"] is not None:
            by_scanner.setdefault(b["scanner"], []).append(b)
    out = []
    for name, rows in sorted(by_scanner.items()):
        bests = [r["best_chg"] for r in rows if r["best_chg"] is not None]
        out.append({
            "scanner": name,
            "count": len(rows),
            "above": sum(1 for r in rows if r["chg"] > 0),
            "avg_chg": round(sum(r["chg"] for r in rows) / len(rows), 2),
            "avg_best": round(sum(bests) / len(bests), 2) if bests else None,
        })
    return out


def sectors_view(conn) -> dict:
    today = date.today()
    out = {}
    for name in db.distinct_backtest_scanners(conn):
        weekly = dict(db.sector_counts_since(conn, name, (today - timedelta(days=7)).isoformat()))
        monthly = dict(db.sector_counts_since(conn, name, (today - timedelta(days=30)).isoformat()))
        sectors = sorted(set(weekly) | set(monthly), key=lambda s: (-monthly.get(s, 0), -weekly.get(s, 0), s))[:5]
        out[name] = [[s, weekly.get(s, 0), monthly.get(s, 0)] for s in sectors]
    return out


def sector_momentum_view(conn, today: date) -> dict:
    """Picks = Chartink backtest hits plus the bot's own live triggers, each
    stock counted once per sector per window however many scanners or days
    picked it. Live triggers take their sector from the backtest data."""
    start = today - timedelta(days=7 * WEEKS - 1)
    sector_of = dict(conn.execute("SELECT symbol, sector FROM backtest_hits ORDER BY hit_date"))
    picks = [(d, sc, sym, sec or UNCLASSIFIED, None) for sc, sym, sec, d in conn.execute(
        "SELECT scanner_name, symbol, sector, hit_date FROM backtest_hits WHERE hit_date >= ?", (start.isoformat(),))]
    since = datetime.combine(start, datetime.min.time(), IST).isoformat()
    for e in db.breakouts_since(conn, since):
        picks.append((_ist(e["detected_at"]).date().isoformat(), e["scanner_name"], e["symbol"],
                      sector_of.get(e["symbol"], UNCLASSIFIED), _price(e)))

    cur_from = (today - timedelta(days=MOMENTUM_DAYS - 1)).isoformat()
    prev_from = (today - timedelta(days=2 * MOMENTUM_DAYS - 1)).isoformat()
    week_starts = [(today - timedelta(days=7 * (WEEKS - i) - 1)).isoformat() for i in range(WEEKS)]

    def move_since(symbol: str, day: str, ref: float | None) -> float | None:
        bars = db.daily_prices_since(conn, symbol, day)
        if not bars:
            return None
        if ref is None and bars[0][0] == day:
            ref = bars[0][4]  # backtest hit: the close on the day it was picked
        return _pct(ref, bars[-1][4])

    by_sector: dict[str, list] = {}
    for p in picks:
        by_sector.setdefault(p[3], []).append(p)
    rows = []
    for sector, ps in by_sector.items():
        cur = {p[2] for p in ps if p[0] >= cur_from}
        prev = {p[2] for p in ps if prev_from <= p[0] < cur_from}
        if not cur and not prev:
            continue
        first_pick: dict[str, tuple] = {}
        for p in sorted(ps, key=lambda p: p[:3]):
            if p[0] >= prev_from:
                first_pick.setdefault(p[2], p)
        moves = [m for p in first_pick.values() if (m := move_since(p[2], p[0], p[4])) is not None]
        weekly = [len({p[2] for p in ps if week_starts[i] <= p[0] < (week_starts[i + 1] if i + 1 < WEEKS else "9999")})
                  for i in range(WEEKS)]
        recent = [p[2] for p in sorted(ps, key=lambda p: p[:3], reverse=True) if p[0] >= cur_from]
        rows.append({
            "sector": sector,
            "cur": len(cur),
            "prev": len(prev),
            "scanners": sorted({p[1] for p in ps if p[0] >= cur_from}),
            "avg_move": round(sum(moves) / len(moves), 2) if moves else None,
            "moves_n": len(moves),
            "weekly": weekly,
            "recent": list(dict.fromkeys(recent))[:6],
        })
    rows.sort(key=lambda r: (-r["cur"], -(r["cur"] - r["prev"]), r["sector"]))
    return {"as_of": today.isoformat(), "days": MOMENTUM_DAYS, "weeks": WEEKS,
            "scanner_count": len(db.distinct_backtest_scanners(conn)), "rows": rows}


def main() -> int:
    conn = db.connect()
    latest_run, last_scan = conn.execute("SELECT id, run_at FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    breakouts = breakouts_view(conn, latest_run)
    data = {
        "generated_at": datetime.now(IST).isoformat(timespec="minutes"),
        "last_scan": _ist(last_scan).isoformat(timespec="minutes"),
        "slots": list(SLOTS),
        "window_days": WINDOW_DAYS,
        "scanners": scanners_view(conn, latest_run),
        "breakouts": breakouts,
        "stats": stats_view(breakouts),
        "sectors": sectors_view(conn),
        "sector_momentum": sector_momentum_view(conn, datetime.now(IST).date()),
    }
    conn.close()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT} ({len(breakouts)} breakouts, {sum(len(s['rows']) for s in data['scanners'])} on scanners)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
