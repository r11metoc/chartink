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
# generically from the DOM (confirmed against a live run), so the three
# scanners are identified by position instead: 1st, 2nd, 3rd non-empty
# table on the page, in the order given by the dashboard owner. Override
# with the CHARTINK_SCANNER_NAMES env var (comma-separated) if the
# dashboard's scanners are ever reordered or added to.
DEFAULT_SCANNER_NAMES = ["63_30_daily", "Bullish_Scanner", "Wkly_upswing"]


def _scanner_names() -> list[str]:
    override = os.environ.get("CHARTINK_SCANNER_NAMES")
    if override:
        return [n.strip() for n in override.split(",") if n.strip()]
    return DEFAULT_SCANNER_NAMES

# Runs in the page context. Walks every <table>, climbs a few ancestor
# levels looking for a heading-like element to use as the widget/scanner
# title, and pulls out header + body cell text.
_EXTRACT_JS = """
() => {
  const tables = Array.from(document.querySelectorAll('table'));
  return tables.map((table, idx) => {
    let title = null;
    let el = table;
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
    let headers = Array.from(table.querySelectorAll('thead th, thead td'))
      .map(c => c.innerText.trim());
    if (headers.length === 0) {
      const firstRow = table.querySelector('tr');
      if (firstRow) headers = Array.from(firstRow.children).map(c => c.innerText.trim());
    }
    let bodyRows = Array.from(table.querySelectorAll('tbody tr'));
    if (bodyRows.length === 0) {
      bodyRows = Array.from(table.querySelectorAll('tr')).slice(headers.length ? 1 : 0);
    }
    const rows = bodyRows
      .map(tr => Array.from(tr.children).map(td => td.innerText.trim()))
      .filter(cells => cells.some(c => c.length > 0));
    return { title: title || `Scanner ${idx + 1}`, headers, rows };
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
        row = {headers[i]: raw[i] for i in range(min(len(headers), len(raw)))}
        symbol = raw[symbol_idx] if symbol_idx < len(raw) else raw[0]
        row["_symbol"] = symbol.strip().upper()
        out.append(row)
    return out


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
        page.goto(url, wait_until="networkidle", timeout=60_000)
        # Widgets can finish their AJAX load slightly after networkidle.
        page.wait_for_timeout(3_000)
        try:
            page.wait_for_selector("table", timeout=15_000)
        except Exception:
            pass

        tables = page.evaluate(_EXTRACT_JS)

        if debug:
            DEBUG_DIR.mkdir(parents=True, exist_ok=True)
            (DEBUG_DIR / "page.html").write_text(page.content(), encoding="utf-8")
            page.screenshot(path=str(DEBUG_DIR / "page.png"), full_page=True)

        browser.close()

    results = []
    for t in tables:
        rows = _rows_to_dicts(t["headers"], t["rows"])
        if not rows:
            continue
        results.append(ScanResult(scanner_name=t["title"], rows=rows))

    names = _scanner_names()
    if len(results) == len(names):
        for result, name in zip(results, names):
            result.scanner_name = name
    else:
        print(
            f"Found {len(results)} non-empty table(s) but {len(names)} configured scanner "
            "name(s) - keeping auto-detected titles. Set CHARTINK_SCANNER_NAMES if the "
            "dashboard's scanners changed."
        )
    return results


if __name__ == "__main__":
    import json
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "https://chartink.com/dashboard/45863"
    found = scrape_dashboard(target, debug=True)
    print(json.dumps([{"scanner_name": r.scanner_name, "rows": r.rows} for r in found], indent=2))
