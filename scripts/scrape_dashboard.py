"""Scrape scanner result tables off a public Chartink dashboard page.

Chartink dashboards render their widgets client-side, so a plain HTTP GET
returns an empty shell. This uses a headless browser to load the page fully,
then extracts every <table> on the page along with a best-guess title for
the widget it belongs to (so multiple scanners on one dashboard come back
as separate, named result sets).

The table/title detection is intentionally generic (no Chartink-specific
CSS classes) since it was written without being able to inspect the live
page. If it doesn't split your three scanners correctly, run with
CHARTINK_DEBUG_DUMP=1 to save the full page HTML + a screenshot, inspect
them, and tighten the logic in `_EXTRACT_JS` below.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import sync_playwright

DEBUG_DIR = Path(__file__).resolve().parent.parent / "debug"

# The dashboard's own headings/titles for each widget aren't detectable
# generically from the DOM, so the three scanners are identified by
# position instead: 1st, 2nd, 3rd non-empty table on the page. This order
# was cross-checked against Chartink's own backtest exports (matching
# today's live results against each scanner's most recent backtest date) -
# it is NOT the order the scanners were originally described in, which was
# wrong. Override with the CHARTINK_SCANNER_NAMES env var (comma-separated)
# if the dashboard's widget order ever changes.
DEFAULT_SCANNER_NAMES = ["63_30_daily", "Bullish_Scanner", "Wkly_upswing"]
# Each widget now shows its scanner's name as its title, so tables are named
# by the title text above them (match_names). Position is only a fallback.
# Oct 2026: the dashboard's widgets were reordered and position-based naming
# filed Bullish_Scanner stocks under 63_30_daily.
LOAD_WAIT_S = 45  # widgets that still say "Loading" get this long to finish
ATTEMPTS = 3


def _scanner_names() -> list[str]:
    override = os.environ.get("CHARTINK_SCANNER_NAMES")
    if override:
        return [n.strip() for n in override.split(",") if n.strip()]
    return DEFAULT_SCANNER_NAMES

# Runs in the page context. Walks every <table>, climbs a few ancestor
# levels looking for a heading-like element to use as the widget/scanner
# title, and pulls out header + body cell text.
_EXTRACT_JS = """
(names) => {
  const tables = Array.from(document.querySelectorAll('table'));
  return tables.map((table, idx) => {
    let title = null;
    let named = null;
    let el = table;
    // Climb to the nearest ancestor that mentions exactly one known scanner
    // name: that is the table's own widget. An ancestor mentioning several
    // names is the whole dashboard, so the table belongs to no widget (e.g.
    // Chartink's hidden "debug filters" table) and stays unnamed.
    for (let i = 0; i < 10 && el && !named; i++) {
      el = el.parentElement;
      if (!el) break;
      const text = el.innerText || '';
      const found = names.filter(n => text.includes(n));
      if (found.length > 1) break;
      if (found.length === 1) named = found[0];
    }
    el = table;
    for (let i = 0; i < 6 && el; i++) {
      el = el.parentElement;
      if (!el) break;
      const heading = el.querySelector(
        'h1,h2,h3,h4,h5,.panel-title,.widget-title,.card-title,.box-title,.card-header'
      );
      if (heading && heading.innerText && heading.innerText.trim()) {
        title = heading.innerText.trim();
        break;
      }
    }
    // th.innerText often includes a hidden "Sort table by X in ascending
    // order" accessibility label after the visible text - keep only the
    // first line.
    const cellLabel = (c) => c.innerText.trim().split('\\n')[0].trim();
    let headers = Array.from(table.querySelectorAll('thead th, thead td')).map(cellLabel);
    if (headers.length === 0) {
      const firstRow = table.querySelector('tr');
      if (firstRow) headers = Array.from(firstRow.children).map(cellLabel);
    }
    let bodyRows = Array.from(table.querySelectorAll('tbody tr'));
    if (bodyRows.length === 0) {
      bodyRows = Array.from(table.querySelectorAll('tr')).slice(headers.length ? 1 : 0);
    }
    const rows = bodyRows
      .map(tr => Array.from(tr.children).map(td => td.innerText.trim()))
      .filter(cells => cells.some(c => c.length > 0));
    return { title: title || `Scanner ${idx + 1}`, named, headers, rows };
  });
}
"""

_SYMBOL_HEADER_PRIORITY = [
    re.compile(r"symbol", re.I),
    re.compile(r"stock\s*name", re.I),
    re.compile(r"stock", re.I),
    re.compile(r"^name$", re.I),
]


@dataclass
class ScanResult:
    scanner_name: str
    rows: list[dict[str, str]]


def _pick_symbol_index(headers: list[str]) -> int:
    for pattern in _SYMBOL_HEADER_PRIORITY:
        for i, h in enumerate(headers):
            if pattern.search(h):
                return i
    # Fallback: first column is often a serial number, so prefer the second
    # column if there is one.
    return 1 if len(headers) > 1 else 0


def _rows_to_dicts(headers: list[str], raw_rows: list[list[str]]) -> list[dict[str, str]]:
    if not headers:
        return []
    symbol_idx = _pick_symbol_index(headers)
    out = []
    for raw in raw_rows:
        if not raw:
            continue
        row = {
            headers[i]: raw[i]
            for i in range(min(len(headers), len(raw)))
            if i != symbol_idx
        }
        symbol = raw[symbol_idx] if symbol_idx < len(raw) else raw[0]
        row["_symbol"] = symbol.strip().upper()
        out.append(row)
    return out


def match_names(named: list[str | None], names: list[str]) -> list[str | None] | None:
    """Scanner name per table from its widget title, or None when the titles
    can't be trusted (no table titled, or two tables with the same title)."""
    hits = [n for n in named if n in names]
    if not hits or len(hits) != len(set(hits)):
        return None
    return [n if n in names else None for n in named]


def scrape_dashboard(url: str, debug: bool = False) -> list[ScanResult]:
    debug = debug or os.environ.get("CHARTINK_DEBUG_DUMP") == "1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        names = _scanner_names()
        tables = []
        for attempt in range(1, ATTEMPTS + 1):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                page.wait_for_load_state("networkidle", timeout=30_000)
            except Exception as e:
                print(f"Attempt {attempt}: page load slow ({e.__class__.__name__}), reading what is there")
            # Widgets fill in after the page loads; wait until every scanner
            # has a table and nothing on the page still says "Loading".
            for _ in range(LOAD_WAIT_S):
                tables = page.evaluate(_EXTRACT_JS, names)
                loading = page.evaluate("() => /\\bLoading\\b/.test(document.body.innerText)")
                found = {t["named"] for t in tables if t["named"]}
                if not loading and len(found) >= len(names):
                    break
                page.wait_for_timeout(1_000)
            if tables:
                break
            print(f"Attempt {attempt}: no tables on the page yet")

        if debug:
            DEBUG_DIR.mkdir(parents=True, exist_ok=True)
            (DEBUG_DIR / "page.html").write_text(page.content(), encoding="utf-8")
            page.screenshot(path=str(DEBUG_DIR / "page.png"), full_page=True)

        browser.close()

    if not tables:
        raise RuntimeError("No scanner tables on the Chartink dashboard after "
                           f"{ATTEMPTS} attempts - nothing was scanned (run with debug=true to see the page)")

    names = _scanner_names()
    titled = match_names([t.get("named") for t in tables], names)
    if titled:
        results = []
        for t, name in zip(tables, titled):
            if name:
                results.append(ScanResult(scanner_name=name, rows=_rows_to_dicts(t["headers"], t["rows"])))
        missing = sorted(set(names) - {r.scanner_name for r in results})
        if missing:
            print(f"Warning: no table found for {', '.join(missing)} (still loading or removed from the dashboard)")
        for result in results:
            result.rows = [r for r in result.rows if sum(1 for v in r.values() if str(v).strip()) >= 3]
        return results

    results = []
    for t in tables:
        rows = _rows_to_dicts(t["headers"], t["rows"])
        if not rows:
            continue
        results.append(ScanResult(scanner_name=t["title"], rows=rows))

    print("Warning: widget titles not found, naming tables by position")
    if len(results) == len(names):
        for result, name in zip(results, names):
            result.scanner_name = name
    else:
        print(
            f"Found {len(results)} non-empty table(s) but {len(names)} configured scanner "
            "name(s) - keeping auto-detected titles. Set CHARTINK_SCANNER_NAMES if the "
            "dashboard's scanners changed."
        )

    # An empty widget still renders a single "No data for table" row. It has to
    # count toward the positional naming above, but it isn't a stock.
    for result in results:
        result.rows = [r for r in result.rows if sum(1 for v in r.values() if str(v).strip()) >= 3]
    return results


if __name__ == "__main__":
    import json
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "https://chartink.com/dashboard/45863"
    found = scrape_dashboard(target, debug=True)
    print(json.dumps([{"scanner_name": r.scanner_name, "rows": r.rows} for r in found], indent=2))
