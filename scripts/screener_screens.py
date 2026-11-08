"""Stocks from public Screener.in screens, ranked by technicals.

The screens are listed in data/screener_screens.txt (one URL per line). Once a
day the bot reads page 1 of each screen, which is the page Screener's
robots.txt allows (?page=, ?limit= and ?sort= are disallowed), and keeps the
company list. Screener shows 25 results a page, so a screen with more results
only contributes its first 25 (Screener's default order); split a big screen
into narrower ones to cover them all.

Only the company names and codes are kept. The website shows the bot's own
technical ranking from Yahoo prices, not Screener's numbers.

Ranking (rank()): the average percentile, within the list, of
  - the 20-day return (short-term momentum),
  - how far the close is above its 50-day average,
  - how far it is below its 52-week high (room to run).
In the backtest of every scanner breakout 2019-26 (bo_ma50_all trades), the top
quarter by this score averaged +7.7% a trade vs +3.2% for the bottom quarter,
and held in both halves (2019-22: +6.1 vs +0.6; 2023-26: +8.6 vs +4.5). That
was tested on scanner breakouts, not on these screens, so treat it as an order
to look at, not a buy signal.
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import db

LIST = Path(__file__).resolve().parent.parent / "data" / "screener_screens.txt"
REFRESH_HOURS = 20
UA = "Mozilla/5.0 (compatible; chartink-scanner-bot)"


def _ensure(conn) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS screen_stocks (
        url TEXT NOT NULL, title TEXT, total INTEGER, pos INTEGER NOT NULL,
        symbol TEXT NOT NULL, name TEXT, fetched_at TEXT NOT NULL)""")


def screen_urls(path: Path = LIST) -> list[str]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line.startswith("https://www.screener.in/screens/"):
            out.append(line.split("?", 1)[0])  # page 1 only: query strings are disallowed
    return out


def parse(page: str) -> dict:
    """{title, total, stocks: [(symbol, name)]} from a screen's HTML."""
    t = re.search(r"<h1[^>]*>\s*(.*?)\s*</h1>", page, re.S)
    n = re.search(r"([\d,]+)\s+results?\s+found", page)
    i = page.find("<table")
    j = page.find("</table>", i)
    body = page[i:j] if i >= 0 and j > i else ""
    stocks, seen = [], set()
    for code, name in re.findall(r'href="/company/([^/"]+)/[^"]*"[^>]*>\s*([^<]+?)\s*</a>', body):
        code = code.upper()
        if code not in seen:
            seen.add(code)
            stocks.append((code, html.unescape(name)))
    return {"title": html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else "",
            "total": int(n.group(1).replace(",", "")) if n else len(stocks), "stocks": stocks}


def refresh(conn, urls: list[str] | None = None, now: datetime | None = None) -> int:
    import requests

    _ensure(conn)
    now = now or datetime.now(timezone.utc)
    done = 0
    for url in urls if urls is not None else screen_urls():
        last = conn.execute("SELECT MAX(fetched_at) FROM screen_stocks WHERE url = ?", (url,)).fetchone()[0]
        if last and now - datetime.fromisoformat(last) < timedelta(hours=REFRESH_HOURS):
            continue
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            r.raise_for_status()
        except Exception as e:  # keep yesterday's list
            print(f"  {url}: fetch failed ({e.__class__.__name__})")
            continue
        got = parse(r.text)
        if not got["stocks"]:
            print(f"  {url}: no companies found (screen private or page changed)")
            continue
        conn.execute("DELETE FROM screen_stocks WHERE url = ?", (url,))
        conn.executemany(
            "INSERT INTO screen_stocks (url, title, total, pos, symbol, name, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [(url, got["title"], got["total"], k, s, nm, now.isoformat()) for k, (s, nm) in enumerate(got["stocks"])])
        print(f"  {got['title'] or url}: {len(got['stocks'])} of {got['total']} results")
        done += 1
    conn.commit()
    return done


def symbols(conn) -> list[str]:
    _ensure(conn)
    return sorted({s for (s,) in conn.execute("SELECT DISTINCT symbol FROM screen_stocks")})


def metrics(bars: list[tuple]) -> dict | None:
    """Technicals from daily bars [(date, open, high, low, close)], oldest first."""
    if len(bars) < 60:
        return None
    close = [b[4] for b in bars]
    high = [b[2] for b in bars[-252:]]
    c = close[-1]
    sma50 = sum(close[-50:]) / 50
    sma200 = sum(close[-200:]) / 200 if len(close) >= 200 else None
    return {"date": bars[-1][0], "close": round(c, 2),
            "ret20": round((c / close[-21] - 1) * 100, 1),
            "vs50": round((c / sma50 - 1) * 100, 1),
            "below_high": round((c / max(high) - 1) * 100, 1),
            "above200": None if sma200 is None else c > sma200}


def _pct_rank(vals: list[float]) -> list[float]:
    """Percentile (0..1] of each value within the list, ties averaged."""
    order = sorted(vals)
    n = len(vals)
    out = []
    for v in vals:
        lo = sum(1 for x in order if x < v)
        eq = sum(1 for x in order if x == v)
        out.append((lo + (eq + 1) / 2) / n)
    return out


def rank(rows: list[dict]) -> list[dict]:
    """Adds 'score' (0-100) and sorts best first; rows without prices go last."""
    ok = [r for r in rows if r.get("ret20") is not None]
    if ok:
        a = _pct_rank([r["ret20"] for r in ok])
        b = _pct_rank([r["vs50"] for r in ok])
        c = _pct_rank([-r["below_high"] for r in ok])  # further below the high ranks higher
        for r, x, y, z in zip(ok, a, b, c):
            r["score"] = round((x + y + z) / 3 * 100)
    ok.sort(key=lambda r: -r["score"])
    rest = [r for r in rows if r.get("ret20") is None]
    for k, r in enumerate(ok, 1):
        r["rank"] = k
    return ok + rest


def view(conn, on_scanner: set[str] | None = None, since: str | None = None) -> list[dict]:
    """One entry per screen for the website."""
    _ensure(conn)
    on_scanner = on_scanner or set()
    since = since or (datetime.now(timezone.utc) - timedelta(days=420)).date().isoformat()
    out = []
    for url, title, total, fetched in conn.execute(
            "SELECT url, MAX(title), MAX(total), MAX(fetched_at) FROM screen_stocks GROUP BY url ORDER BY url"):
        rows = []
        for sym, name in conn.execute("SELECT symbol, name FROM screen_stocks WHERE url = ? ORDER BY pos", (url,)):
            m = metrics(db.daily_prices_since(conn, sym, since)) or {}
            rows.append({"symbol": sym, "name": name, "on_scanner": sym in on_scanner, **m})
        out.append({"url": url, "title": title, "total": total, "fetched_at": fetched, "stocks": rank(rows)})
    return out


def main() -> int:
    conn = db.connect()
    n = refresh(conn)
    print(f"Screener screens refreshed: {n}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
