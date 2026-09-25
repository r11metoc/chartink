"""Send Telegram messages summarizing scan results."""

from __future__ import annotations

import html
import os
import re
from datetime import datetime, timedelta, timezone

import requests

TELEGRAM_LIMIT = 4096
IST = timezone(timedelta(hours=5, minutes=30))
_KIND_ICON = {"fresh": "🚀", "retest": "🔁"}


def _chunks(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Split on blank lines, which never fall inside a <pre>/<b> block here."""
    chunks, current = [], ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}" if current else block
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
        current = block[:limit]
    if current:
        chunks.append(current)
    return chunks


def send_telegram_message(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set, skipping notification.")
        return

    def post(body: str, as_html: bool) -> requests.Response:
        payload = {"chat_id": chat_id, "text": body, "disable_web_page_preview": True}
        if as_html:
            payload["parse_mode"] = "HTML"
        return requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload, timeout=15)

    for chunk in _chunks(text):
        resp = post(chunk, as_html=True)
        if resp.status_code == 400:
            print(f"Telegram rejected the HTML ({resp.text}); resending as plain text.")
            resp = post(html.unescape(re.sub(r"<[^>]+>", "", chunk)), as_html=False)
        if not resp.ok:
            print(f"Telegram notification failed: {resp.status_code} {resp.text}")


def _now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %H:%M IST")


def _col(row: dict | None, keyword: str) -> str | None:
    """Value of the first scan column whose header contains keyword."""
    for k, v in (row or {}).items():
        if not k.startswith("_") and keyword in k.lower():
            return v
    return None


def _num(value) -> float | None:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def _price(row: dict | None) -> float | None:
    return _num(_col(row, "price"))


def _details(row: dict, hits: list | None = None) -> str:
    """Indented second line: day change, volume, industry, backtest repeats."""
    bits = []
    day = _num(_col(row, "%"))
    if day is not None:
        bits.append(f"day {day:+.2f}%")
    vol = _col(row, "vol")
    if vol:
        bits.append(f"Vol {vol}")
    industry = _col(row, "industry")
    if industry:
        bits.append(industry[:28].rstrip(" -/"))
    if hits:
        bits.append(f"📚 {len(hits)}x before")
    return "     " + html.escape(" · ".join(bits)) if bits else ""


def _stock_line(icon: str, symbol: str, row: dict) -> str:
    """'🚀 VETO ₹150.32'"""
    line = f"{icon} <b>{html.escape(symbol)}</b>"
    price = _price(row)
    return line + (f" ₹{price:.2f}" if price is not None else "")


def format_breakout_message(breakouts: list[tuple[str, str, dict]]) -> str:
    """breakouts: list of (scanner_name, kind, row) - row must include '_symbol'.
    kind is 'fresh' (never seen before) or 'retest' (re-triggered after a gap)."""
    by_scanner: dict[str, list[tuple[str, dict]]] = {}
    for scanner_name, kind, row in breakouts:
        by_scanner.setdefault(scanner_name, []).append((kind, row))

    blocks = [f"<b>🚨 New breakouts</b> · {_now_ist()}"]
    for scanner_name, kind_rows in by_scanner.items():
        lines = [f"<b>{html.escape(scanner_name)}</b>"]
        for kind, row in sorted(kind_rows, key=lambda kr: _num(_col(kr[1], "%")) or 0, reverse=True):
            lines.append(_stock_line(_KIND_ICON.get(kind, "🚀"), row["_symbol"], row))
            lines.append(_details(row, row.get("_backtest_hits")))
        blocks.append("\n".join(filter(None, lines)))
    blocks.append("🚀 first time on this scanner · 🔁 back after dropping off")
    return "\n\n".join(blocks)


def _fmt_price(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "-"


def _buy_hold_tables(items: list[dict]) -> str:
    """items: {"symbol", "trig", "now", "mark"}. BUY = now above trig, HOLD =
    everything else. One monospace table per group, best move first."""
    def move(item):
        t, c = item["trig"], item["now"]
        return (c - t) / t * 100 if t and c is not None else None

    buys = [i for i in items if (move(i) or 0) > 0]
    holds = [i for i in items if (move(i) or 0) <= 0]
    parts = []
    for title, group in (("🟢 BUY", buys), ("⏸ HOLD", holds)):
        if not group:
            continue
        group.sort(key=lambda i: move(i) if move(i) is not None else float("-inf"), reverse=True)
        lines = [f"{'Symbol':<10} {'Trig':>8} {'Now':>8} {'Chg':>6}"]
        for i in group:
            m = move(i)
            chg = f"{m:+.1f}%" if m is not None else "-"
            lines.append(f"{i['symbol'][:10]:<10} {_fmt_price(i['trig']):>8} {_fmt_price(i['now']):>8} {chg:>6}{i.get('mark', '')}")
        parts.append(f"{title} ({len(group)})\n<pre>" + html.escape("\n".join(lines)) + "</pre>")
    return "\n".join(parts)


RULE_LINE = "<i>BUY = price above trigger · HOLD = at or below</i>"


def format_scan_message(scans: list, trigger_lookup: dict) -> str:
    """Every stock on each scanner right now, as BUY / HOLD tables.
    trigger_lookup maps (scanner_name, symbol) -> trigger row or None."""
    blocks = [f"<b>📋 Snapshot</b> · {_now_ist()}\n{RULE_LINE}"]
    for scan in scans:
        header = f"<b>{html.escape(scan.scanner_name)}</b> ({len(scan.rows)})"
        if not scan.rows:
            blocks.append(f"{header}\nno stocks right now")
            continue
        items = [
            {"symbol": row["_symbol"], "now": _price(row),
             "trig": _price(trigger_lookup.get((scan.scanner_name, row["_symbol"])))}
            for row in scan.rows
        ]
        blocks.append(f"{header}\n{_buy_hold_tables(items)}")
    return "\n\n".join(blocks)


def _sector_table(windows: dict) -> str:
    """Monospace table: sector, 7-day count, 30-day count - sorted by the
    30-day count so the most persistently active sector leads."""
    weekly = dict(windows.get("weekly") or [])
    monthly = dict(windows.get("monthly") or [])
    sectors = sorted(set(weekly) | set(monthly), key=lambda s: (-monthly.get(s, 0), -weekly.get(s, 0), s))[:5]
    if not sectors:
        return "<pre>no hits</pre>"
    rows = [f"{'Sector':<22}{'7d':>4}{'30d':>5}"]
    for s in sectors:
        rows.append(f"{s[:22]:<22}{weekly.get(s, 0):>4}{monthly.get(s, 0):>5}")
    return "<pre>" + html.escape("\n".join(rows)) + "</pre>"


def format_sector_focus_message(sector_focus: dict) -> str:
    """{scanner_name: {"weekly": [...], "monthly": [...]}} from the backtest hits."""
    blocks = ["<b>🏭 Sectors in focus</b>\n<i>How many stocks each scanner picked per sector</i>"]
    for scanner_name, windows in sector_focus.items():
        blocks.append(f"<b>{html.escape(scanner_name)}</b>\n{_sector_table(windows)}")
    return "\n\n".join(blocks)


def format_digest_message(entries: list[dict], days: int) -> str:
    """Stocks that triggered on a scanner in the last `days`, as BUY / HOLD
    tables per scanner. entries come from db.breakouts_since() (newest first)
    with _current_row (latest scraped row) and _on_scan (still on the scanner)."""
    blocks = [f"<b>📊 Digest</b> · triggers in last {days}d · {_now_ist()}\n{RULE_LINE}"]
    if not entries:
        blocks.append("No new triggers in this window.")
        return "\n\n".join(blocks)

    latest: dict[str, dict[str, dict]] = {}
    for e in entries:  # newest first, so the first event per stock is its latest trigger
        latest.setdefault(e["scanner_name"], {}).setdefault(e["symbol"], e)

    any_off = False
    for scanner_name, by_symbol in latest.items():
        items = []
        for symbol, e in by_symbol.items():
            off = not e.get("_on_scan")
            any_off |= off
            items.append({"symbol": symbol, "trig": _price(e), "now": _price(e.get("_current_row")),
                          "mark": " *" if off else ""})
        blocks.append(f"<b>{html.escape(scanner_name)}</b> ({len(items)})\n{_buy_hold_tables(items)}")
    if any_off:
        blocks.append("<i>* no longer on the scanner - last seen price</i>")
    return "\n\n".join(blocks)
