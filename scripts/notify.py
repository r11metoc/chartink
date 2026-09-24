"""Send Telegram messages summarizing scan results."""

from __future__ import annotations

import os

import requests


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


def _format_symbol_line(row: dict, pct_key: str | None, price_key: str | None, vol_key: str | None, industry_key: str | None) -> str:
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
    return f"  {arrow} <b>{symbol}</b>  {details}" if details else f"  {arrow} <b>{symbol}</b>"


def _format_rows(rows: list[dict]) -> list[str]:
    """Render a scanner's rows sorted by % change (biggest movers first),
    pulling out price/change/volume/industry when those columns exist."""
    if not rows:
        return ["  (no symbols)"]

    headers = [k for k in rows[0].keys() if k != "_symbol"]
    pct_key = _find_column(headers, "%")
    price_key = _find_column(headers, "price")
    vol_key = _find_column(headers, "vol")
    industry_key = _find_column(headers, "industry")

    ordered = sorted(rows, key=lambda r: _as_float(r.get(pct_key)) or 0, reverse=True) if pct_key else rows

    return [_format_symbol_line(row, pct_key, price_key, vol_key, industry_key) for row in ordered]


def format_breakout_message(breakouts: list[tuple[str, dict]]) -> str:
    """breakouts: list of (scanner_name, row) - row must include '_symbol'."""
    by_scanner: dict[str, list[dict]] = {}
    for scanner_name, row in breakouts:
        by_scanner.setdefault(scanner_name, []).append(row)

    lines = ["<b>New Chartink breakouts</b>"]
    for scanner_name, rows in by_scanner.items():
        lines.append(f"\n<b>{scanner_name}</b>")
        lines.extend(_format_rows(rows))
    return "\n".join(lines)


def format_snapshot_message(scans: list) -> str:
    """Full current scan results, regardless of what's new vs. the last run."""
    lines = ["<b>Chartink scan snapshot</b>"]
    for scan in scans:
        lines.append(f"\n<b>{scan.scanner_name}</b> ({len(scan.rows)})")
        lines.extend(_format_rows(scan.rows))
    return "\n".join(lines)
