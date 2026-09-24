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


def format_breakout_message(breakouts: list[tuple[str, str]]) -> str:
    by_scanner: dict[str, list[str]] = {}
    for scanner_name, symbol in breakouts:
        by_scanner.setdefault(scanner_name, []).append(symbol)

    lines = ["<b>New Chartink breakouts</b>"]
    for scanner_name, symbols in by_scanner.items():
        lines.append(f"\n<b>{scanner_name}</b>")
        for s in symbols:
            lines.append(f"  • {s}")
    return "\n".join(lines)


def format_snapshot_message(scans: list) -> str:
    """Full current scan results, regardless of what's new vs. the last run."""
    lines = ["<b>Chartink scan snapshot</b>"]
    for scan in scans:
        lines.append(f"\n<b>{scan.scanner_name}</b> ({len(scan.rows)})")
        if not scan.rows:
            lines.append("  (no symbols)")
            continue
        for row in scan.rows:
            symbol = row.get("_symbol", "?")
            details = ", ".join(f"{k}: {v}" for k, v in row.items() if k != "_symbol" and v)
            lines.append(f"  • <b>{symbol}</b> — {details}" if details else f"  • {symbol}")
    return "\n".join(lines)
