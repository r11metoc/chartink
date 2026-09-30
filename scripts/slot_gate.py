"""Decide whether a scheduled run should scan, and for which slot.

GitHub starts scheduled runs hours late, so the workflow fires every 15
minutes and this picks by the actual time instead: the first run inside a
slot's window scans for that slot, every other run exits in seconds.
Writes slot=<slot or empty> to $GITHUB_OUTPUT.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import db

IST = timezone(timedelta(hours=5, minutes=30))
SLOTS = ("09:23", "12:23", "15:23")
WINDOW = timedelta(minutes=90)


def current_slot(now: datetime) -> str | None:
    if now.weekday() >= 5:
        return None
    for s in SLOTS:
        hour, minute = map(int, s.split(":"))
        start = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if start <= now < start + WINDOW:
            return f"{now:%Y-%m-%d} {s}"
    return None


def main() -> None:
    slot = current_slot(datetime.now(IST))
    if slot:
        conn = db.connect()
        if db.slot_done(conn, slot):
            slot = None
        conn.close()
    print(f"slot={slot or '(none)'}")
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as f:
            f.write(f"slot={slot or ''}\n")


if __name__ == "__main__":
    main()
