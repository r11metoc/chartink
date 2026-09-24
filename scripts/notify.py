"""Send a Telegram message summarizing newly detected breakouts."""

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
