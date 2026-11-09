"""Fundamentals of the scanner stocks from their Screener.in company pages.

For each stock the Chartink scanners pick, the bot reads its public company
page (screener.in/company/<code>/consolidated/, else the standalone page) at
most once every REFRESH_DAYS, a few seconds apart, and maps it to Screener's
own column names (the ones main_screen.py and valuepick_score.py use).
Pledge isn't on the public page, so that check stays "not checked".

Screener's terms allow personal viewing only and forbid copying or public
display, so the figures are kept out of the public repo: they live in
data/screener_cache.json, which is git-ignored and carried between runs in
GitHub's private Actions cache. The public website shows only pass/fail and
which conditions fail; Telegram (private) gets the figures.

fundamentals.py uses this first and falls back to Yahoo when a page can't be
read.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "screener_cache.json"
REFRESH_DAYS = 30
DELAY_S = 3
MAX_FAILS = 5  # stop for this run after this many failed pages in a row (blocked or down)
UA = "Mozilla/5.0 (compatible; personal-scanner-bot)"


def _num(text) -> float | None:
    if text is None:
        return None
    t = re.sub(r"[₹,%\s]|Cr\.?", "", str(text))
    try:
        return float(t)
    except ValueError:
        return None


def _table(soup, section_id: str, which: int = 0) -> tuple[list[str], dict[str, list]]:
    """(column headers, {row label: [values]}) of a statement table."""
    sec = soup.find("section", id=section_id)
    tables = sec.find_all("table", class_="data-table") if sec else []
    if len(tables) <= which:
        return [], {}
    t = tables[which]
    heads = [th.get_text(" ", strip=True) for th in t.select("thead th")][1:]
    rows = {}
    for tr in t.select("tbody tr"):
        cells = tr.find_all("td")
        if not cells:
            continue
        label = re.sub(r"\s*\+\s*$", "", cells[0].get_text(" ", strip=True).replace("\xa0", " ")).strip()
        rows[label] = [_num(c.get_text(strip=True)) for c in cells[1:]]
    return heads, rows


def _growth(new, old):
    return round((new / old - 1) * 100, 1) if new is not None and old and old > 0 else None


def parse(page: str) -> dict:
    """Screener-column row from one company page ('' = not available)."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page, "html.parser")
    top = {}
    for li in soup.select("#top-ratios li"):
        name = li.find(class_="name")
        nums = li.select(".number")
        if name and nums:
            top[name.get_text(strip=True)] = [_num(n.get_text()) for n in nums]
    first = lambda k: (top.get(k) or [None])[0]  # noqa: E731

    _, q = _table(soup, "quarters")
    pl_heads, pl = _table(soup, "profit-loss")
    _, bs = _table(soup, "balance-sheet")
    _, cf = _table(soup, "cash-flow")
    _, ra = _table(soup, "ratios")
    _, sh = _table(soup, "shareholding")

    annual = [i for i, h in enumerate(pl_heads) if not h.upper().startswith("TTM")]
    pick = lambda vals, k: vals[annual[k]] if vals and len(annual) >= -k and annual[k] < len(vals) else None  # noqa: E731
    np_ = pl.get("Net Profit") or pl.get("Profit after tax")
    sales = pl.get("Sales") or pl.get("Revenue")
    opm = pl.get("OPM %") or pl.get("Financing Margin %")
    qnp = q.get("Net Profit") or []
    last = lambda vals, k=-1: vals[k] if vals and len(vals) >= -k else None  # noqa: E731

    eq = (last(bs.get("Equity Capital")) or 0) + (last(bs.get("Reserves")) or 0)
    debt = last(bs.get("Borrowings"))
    dd = ra.get("Debtor Days") or []

    def compounded(title):
        for t in soup.select("table.ranges-table"):
            th = t.find("th")
            if th and title in th.get_text():
                for tr in t.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) == 2 and tds[0].get_text(strip=True).startswith("3 Years"):
                        return _num(tds[1].get_text())
        return None

    ind = soup.select('#peers a[title="Industry"]')
    bse = re.search(r"bseindia\.com/stock-share-price/[^/\"]+/[^/\"]+/(\d{6})/", page)
    out = {
        "Name": (soup.find("h1").get_text(strip=True) if soup.find("h1") else ""),
        "Industry": ind[-1].get_text(strip=True) if ind else "",
        "BSE Code": bse.group(1) if bse else None,
        "Current Price": first("Current Price"),
        "High price": first("High / Low"),
        "Market Capitalization": first("Market Cap"),
        "Price to Earning": first("Stock P/E"),
        "Return on capital employed": first("ROCE") if first("ROCE") is not None else last(ra.get("ROCE %")),
        "Return on equity": first("ROE"),
        "OPM": pick(opm, -1),
        "Debt to equity": round(debt / eq, 2) if debt is not None and eq > 0 else None,
        "Pledged percentage": None,  # not on the public page
        "Promoter holding": last(sh.get("Promoters")),
        "Sales growth 3Years": compounded("Compounded Sales Growth"),
        "Profit growth 3Years": compounded("Compounded Profit Growth"),
        "Sales growth": _growth(pick(sales, -1), pick(sales, -2)),
        "Profit growth": _growth(pick(np_, -1), pick(np_, -2)),
        "YOY Quarterly profit growth": _growth(last(qnp), last(qnp, -5)) if len(qnp) >= 5 else None,
        "Profit after tax": pick(np_, -1),
        "CFO": last(cf.get("Cash from Operating Activity")),
        "Debt": debt,
        "Debt Change": round(debt - last(bs.get("Borrowings"), -2), 1)
        if debt is not None and last(bs.get("Borrowings"), -2) is not None else None,
        "Debtor days": last(dd),
        "Debtor Days Ch": round(dd[-1] - dd[-2], 1) if len(dd) >= 2 and None not in dd[-2:] else None,
    }
    return {k: ("" if v is None else v) for k, v in out.items()}


def _load() -> dict:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


_mem: dict | None = None


def cached(symbol: str) -> dict | None:
    global _mem
    if _mem is None:
        _mem = _load()
    e = _mem.get(symbol)
    return dict(e["data"], **{"NSE Code": symbol}) if e else None


def fetched_at(symbol: str) -> str | None:
    cached(symbol)
    e = (_mem or {}).get(symbol)
    return e["fetched_at"][:10] if e else None


def fetch(symbol: str, get=None, sleep=time.sleep) -> dict | None:
    """Row for one stock: consolidated page, else standalone. None if not found."""
    if get is None:
        import requests
        get = lambda url: requests.get(url, headers={"User-Agent": UA}, timeout=30)  # noqa: E731
    best = None
    for k, path in enumerate(("consolidated/", "")):
        if k:
            sleep(DELAY_S)
        r = get(f"https://www.screener.in/company/{symbol}/{path}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        row = parse(r.text)
        if row["Profit after tax"] != "":
            return row
        if row["Market Capitalization"] != "" and best is None:
            best = row
    return best


def refresh(symbols: list[str], days: int = REFRESH_DAYS, get=None, sleep=time.sleep) -> int:
    global _mem
    data = _load()
    now = datetime.now(timezone.utc)
    done = fails = 0
    for sym in sorted(set(symbols)):
        e = data.get(sym)
        if e and (now - datetime.fromisoformat(e["fetched_at"])).days < days and "BSE Code" in e["data"]:
            continue
        try:
            row = fetch(sym, get, sleep)
            fails = 0
        except Exception as ex:
            fails += 1
            print(f"  {sym}: Screener page failed ({ex.__class__.__name__})")
            if fails >= MAX_FAILS:
                print("  Screener isn't answering; the rest wait for the next run (Yahoo covers them).")
                break
            continue
        if row:
            data[sym] = {"fetched_at": now.isoformat(), "data": row}
            done += 1
        sleep(DELAY_S)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    _mem = data
    return done
