"""Send Telegram messages summarizing scan results."""

from __future__ import annotations

import html
import os
import re
from datetime import datetime, timedelta, timezone

import requests

TELEGRAM_LIMIT = 4096
IST = timezone(timedelta(hours=5, minutes=30))
DIVIDER = "━━━━━━━━━━━━━━━━━━━━"
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


def _short_date(iso: str) -> str:
    return datetime.fromisoformat(iso).astimezone(IST).strftime("%d %b")


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


def _move_pct(trigger: dict | None, current: dict | None) -> float | None:
    """% change from the trigger price to the current price."""
    t, c = _price(trigger), _price(current)
    if t is None or c is None or t == 0:
        return None
    return (c - t) / t * 100


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


def _stock_line(icon: str, symbol: str, current: dict, trigger: dict | None) -> str:
    """'🟢 VETO ₹150.32 · +0.6% vs trig ₹149.40'"""
    line = f"{icon} <b>{html.escape(symbol)}</b>"
    now = _price(current)
    if now is not None:
        line += f" ₹{now:.2f}"
    move = _move_pct(trigger, current)
    if move is not None:
        line += f" · <b>{move:+.1f}%</b> vs trig ₹{_price(trigger):.2f}"
    return line


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
            lines.append(_stock_line(_KIND_ICON.get(kind, "🚀"), row["_symbol"], row, None))
            lines.append(_details(row, row.get("_backtest_hits")))
        blocks.append("\n".join(filter(None, lines)))
    blocks.append("🚀 first time on this scanner · 🔁 back after dropping off")
    return "\n\n".join(blocks)


def format_scan_message(scans: list, trigger_lookup: dict, new_symbols: set[tuple[str, str]] = frozenset()) -> str:
    """Every stock currently on each scanner, split into BUY (price above its
    trigger price) and HOLD (at or below). trigger_lookup maps
    (scanner_name, symbol) -> trigger row, or None if unknown; new_symbols
    holds (scanner_name, symbol) pairs that triggered this very run."""
    blocks = [f"<b>📋 Scan snapshot</b> · {_now_ist()}"]

    for scan in scans:
        header = f"<b>{html.escape(scan.scanner_name)}</b> ({len(scan.rows)})"
        if not scan.rows:
            blocks.append(f"{header}\n  no stocks right now")
            continue

        buys, holds, fresh = [], [], []
        for row in scan.rows:
            symbol = row["_symbol"]
            trigger = trigger_lookup.get((scan.scanner_name, symbol))
            if (scan.scanner_name, symbol) in new_symbols:
                bucket, trigger = fresh, None
            else:
                move = _move_pct(trigger, row)
                bucket = buys if move is not None and move > 0 else holds
            entry = (_move_pct(trigger, row) or 0, [
                _stock_line("", symbol, row, trigger).lstrip(),
                _details(row, (trigger or row).get("_backtest_hits")),
            ])
            bucket.append(entry)

        lines = [header]
        for title, bucket in (("🆕 NEW (triggered this run)", fresh), ("🟢 BUY", buys), ("⏸ HOLD", holds)):
            if not bucket:
                continue
            lines.append(f"{title} ({len(bucket)})")
            for _, entry_lines in sorted(bucket, key=lambda e: e[0], reverse=True):
                lines.append("  " + entry_lines[0])
                if entry_lines[1]:
                    lines.append(entry_lines[1])
        blocks.append("\n".join(lines))

    blocks.append("<i>BUY = price above the trigger price; HOLD = at or below.</i>")
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


def _buy_list_table(outcomes: list[dict]) -> str:
    """Monospace table: date, symbol, % return - buy-list rows only (all
    already real breakouts), so no separate result column is needed."""
    rows = [f"{'Date':<11}{'Symbol':<15}{'Ret%':>6}"]
    for o in outcomes:
        rows.append(f"{o['hit_date']:<11}{o['symbol'][:15]:<15}{o['pct_return']:>+5.1f}%")
    return "<pre>" + html.escape("\n".join(rows)) + "</pre>"


def format_sector_focus_message(sector_focus: dict) -> str:
    """Standalone message: {scanner_name: {"weekly": [...], "monthly": [...]}}
    from Chartink's backtest history. Kept separate from the digest so the
    digest has more room for the buy list."""
    blocks = ["<b>🏭 Sectors in focus</b> (backtest hits)"]
    for scanner_name, windows in sector_focus.items():
        blocks.append(f"<b>{html.escape(scanner_name)}</b>\n{_sector_table(windows)}")
    return "\n\n".join(blocks)


def _live_activity(entries: list[dict]) -> list[str]:
    """One line per symbol per scanner: latest trigger date and price, the
    price move since, and whether it's still on the scan."""
    if not entries:
        return ["  no new triggers in this window"]

    by_scanner: dict[str, dict[str, list[dict]]] = {}
    for e in entries:  # newest first
        by_scanner.setdefault(e["scanner_name"], {}).setdefault(e["symbol"], []).append(e)

    blocks = []
    for scanner_name, by_symbol in by_scanner.items():
        lines = [f"<b>{html.escape(scanner_name)}</b>"]
        for symbol, events in by_symbol.items():
            latest = events[0]
            current = latest.get("_current_row")
            move = _move_pct(latest, current)
            if not latest.get("_on_scan"):
                status = "⚪"
            elif move is not None and move > 0:
                status = "🟢"
            else:
                status = "⏸"
            kinds = "".join(_KIND_ICON.get(e["kind"], "") for e in reversed(events))
            line = f"{status} <b>{html.escape(symbol)}</b> {kinds} {_short_date(latest['detected_at'])}"
            trig, now = _price(latest), _price(current)
            if trig is not None:
                line += f" · ₹{trig:.2f}"
                if now is not None and now != trig:
                    line += f" → ₹{now:.2f} (<b>{move:+.1f}%</b>)"
            lines.append(line)
        blocks.append("\n".join(lines))

    multi = {}
    for e in entries:
        multi.setdefault(e["symbol"], set()).add(e["scanner_name"])
    multi = {s: names for s, names in multi.items() if len(names) > 1}
    if multi:
        blocks.append("<b>⭐ On more than one scanner</b>\n" + "\n".join(
            f"  <b>{html.escape(s)}</b>: {html.escape(', '.join(sorted(names)))}" for s, names in multi.items()
        ))
    blocks.append("<i>🟢 above trigger · ⏸ at/below · ⚪ dropped off the scan (last price)</i>")
    return blocks


def format_digest_message(
    entries: list[dict],
    days: int,
    recent_outcomes: list[dict] | None = None,
    backtest_days: int | None = None,
    buy_min_pct: float = 1.0,
    buy_max_pct: float = 15.0,
) -> str:
    """entries: breakout rows from db.breakouts_since() (newest first), each
    with scanner_name/symbol/kind/detected_at, the scan's own columns, plus
    _current_row (latest scraped row) and _on_scan (still on the scanner).
    recent_outcomes: backtest_outcomes rows from the last backtest_days - the
    buy list shows real breakouts with a return strictly between buy_min_pct
    and buy_max_pct, leaving out near-flat moves and extreme outliers (often
    corporate actions like splits rather than genuine price moves)."""
    blocks = [f"<b>📊 Chartink digest</b> · {_now_ist()}"]
    blocks.append(f"{DIVIDER}\n<b>🔴 Live triggers</b> ({days}d)")
    blocks.extend(_live_activity(entries))

    if recent_outcomes:
        total = len(recent_outcomes)
        wins = sum(1 for o in recent_outcomes if o["label"] == 1)
        blocks.append(
            f"{DIVIDER}\n<b>📜 Backtest outcomes</b> ({backtest_days or days}d)\n"
            f"{wins}/{total} real breakouts ({wins / total:.0%})"
        )

        buy_list = [o for o in recent_outcomes if o["label"] == 1 and buy_min_pct < o["pct_return"] < buy_max_pct]
        blocks.append(f"<b>🎯 Buy list</b> ({len(buy_list)}/{wins})" + ("\n  (none in this range)" if not buy_list else ""))

        by_scanner: dict[str, list[dict]] = {}
        for o in buy_list:
            by_scanner.setdefault(o["scanner_name"], []).append(o)
        for scanner_name, outcomes in by_scanner.items():
            ordered = sorted(outcomes, key=lambda o: o["pct_return"], reverse=True)
            blocks.append(f"<b>{html.escape(scanner_name)}</b> ({len(outcomes)})\n{_buy_list_table(ordered)}")

    return "\n\n".join(blocks)
