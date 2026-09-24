"""Send Telegram messages summarizing scan results."""

from __future__ import annotations

import os

import requests

_KIND_ICON = {"fresh": "🚀", "retest": "🔁"}


def send_telegram_message(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set, skipping notification.")
        return

    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True},
        timeout=15,
    )
    if not resp.ok:
        print(f"Telegram notification failed: {resp.status_code} {resp.text}")


def _find_column(headers: list[str], *keywords: str) -> str | None:
    for h in headers:
        low = h.lower()
        if any(k in low for k in keywords):
            return h
    return None


def _as_float(value) -> float | None:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def _format_symbol_line(row: dict, prefix: str = "") -> str:
    headers = [k for k in row.keys() if k not in ("_symbol", "scanner_name", "kind", "detected_at")]
    pct_key = _find_column(headers, "%")
    price_key = _find_column(headers, "price")
    vol_key = _find_column(headers, "vol")
    industry_key = _find_column(headers, "industry")

    symbol = row.get("_symbol", "?")
    pct = _as_float(row.get(pct_key)) if pct_key else None
    arrow = "🟢" if pct is None or pct >= 0 else "🔴"

    bits = []
    if price_key and row.get(price_key):
        bits.append(f"₹{row[price_key]}")
    if pct_key and row.get(pct_key) not in (None, ""):
        sign = "+" if (pct or 0) >= 0 else ""
        bits.append(f"{sign}{row[pct_key]}%")
    if vol_key and row.get(vol_key):
        bits.append(f"Vol {row[vol_key]}")
    if industry_key and row.get(industry_key):
        bits.append(row[industry_key])

    details = "  ·  ".join(bits)
    label = f"{prefix}{arrow} <b>{symbol}</b>"
    return f"  {label}  {details}" if details else f"  {label}"


def _format_rows(rows: list[dict]) -> list[str]:
    """Render rows sorted by % change (biggest movers first), pulling out
    price/change/volume/industry when those columns exist."""
    if not rows:
        return ["  (no symbols)"]

    headers = [k for k in rows[0].keys() if k not in ("_symbol", "scanner_name", "kind", "detected_at")]
    pct_key = _find_column(headers, "%")
    ordered = sorted(rows, key=lambda r: _as_float(r.get(pct_key)) or 0, reverse=True) if pct_key else rows

    return [_format_symbol_line(row) for row in ordered]


def format_breakout_message(breakouts: list[tuple[str, str, dict]]) -> str:
    """breakouts: list of (scanner_name, kind, row) - row must include '_symbol'.
    kind is 'fresh' (never seen before) or 'retest' (re-triggered after a gap)."""
    by_scanner: dict[str, list[tuple[str, dict]]] = {}
    for scanner_name, kind, row in breakouts:
        by_scanner.setdefault(scanner_name, []).append((kind, row))

    lines = ["<b>New Chartink breakouts</b>"]
    for scanner_name, kind_rows in by_scanner.items():
        lines.append(f"\n<b>{scanner_name}</b>")
        headers = [k for k in kind_rows[0][1].keys() if k not in ("_symbol", "scanner_name", "kind", "detected_at")]
        pct_key = _find_column(headers, "%")
        ordered = sorted(kind_rows, key=lambda kr: _as_float(kr[1].get(pct_key)) or 0, reverse=True) if pct_key else kind_rows
        for kind, row in ordered:
            lines.append(_format_symbol_line(row, prefix=_KIND_ICON.get(kind, "")))
    return "\n".join(lines)


def format_snapshot_message(scans: list) -> str:
    """Full current scan results, regardless of what's new vs. the last run."""
    lines = ["<b>Chartink scan snapshot</b>"]
    for scan in scans:
        lines.append(f"\n<b>{scan.scanner_name}</b> ({len(scan.rows)})")
        lines.extend(_format_rows(scan.rows))
    return "\n".join(lines)


def format_digest_message(entries: list[dict], days: int) -> str:
    """entries: breakout rows from db.breakouts_since(), each with
    scanner_name/symbol/kind/detected_at plus the scan's own columns."""
    if not entries:
        return f"<b>📊 Chartink digest</b> (last {days} days)\n\nNo breakouts recorded in this window."

    lines = [f"<b>📊 Chartink digest</b> (last {days} days)"]

    scanners_by_symbol: dict[str, list[str]] = {}
    for e in entries:
        scanners_by_symbol.setdefault(e["symbol"], []).append(e["scanner_name"])

    recurring = {s: scs for s, scs in scanners_by_symbol.items() if len(scs) > 1}
    if recurring:
        lines.append("\n<b>⭐ Top recurring symbols</b>")
        for symbol, scanners in sorted(recurring.items(), key=lambda kv: len(kv[1]), reverse=True):
            summary = ", ".join(f"{name} x{scanners.count(name)}" for name in dict.fromkeys(scanners))
            lines.append(f"  <b>{symbol}</b> — {len(scanners)}x ({summary})")

    retests = [e for e in entries if e["kind"] == "retest"]
    if retests:
        lines.append("\n<b>🔁 Retest candidates</b> (re-triggered after a gap)")
        for e in retests:
            lines.append(f"  [{e['scanner_name']}] " + _format_symbol_line(e).lstrip())

    fresh = [e for e in entries if e["kind"] == "fresh"]
    if fresh:
        lines.append("\n<b>🚀 Fresh breakouts</b> (first time seen)")
        for e in fresh:
            lines.append(f"  [{e['scanner_name']}] " + _format_symbol_line(e).lstrip())

    return "\n".join(lines)
