"""Run an ad-hoc, read-only SQL query against data/chartink.db and send the
result to Telegram - lets you inspect the database without leaving Telegram
or touching git/sqlite yourself. Triggered from the Actions tab, not from
Telegram itself (this bot can't receive messages, only send them).

Safety: the connection is opened in SQLite's URI read-only mode, so any
write attempt (INSERT/UPDATE/DELETE/DROP/etc.) fails at the database level
regardless of what the query text says - not just a keyword blocklist,
which multi-statement tricks could get around.
"""

from __future__ import annotations

import html
import os
import sqlite3
import sys

import db
from notify import send_telegram_message

MAX_ROWS = 50
MAX_COL_WIDTH = 20
MAX_MESSAGE_CHARS = 3800  # leave headroom under Telegram's 4096 limit


def _format_table(columns: list[str], rows: list[tuple]) -> str:
    if not rows:
        return "(no rows)"

    def cell(v) -> str:
        if v is None:
            s = ""
        elif isinstance(v, float):
            s = f"{v:.2f}"
        else:
            s = str(v)
        return s[:MAX_COL_WIDTH]

    widths = [len(c) for c in columns]
    str_rows = [[cell(v) for v in row] for row in rows]
    for row in str_rows:
        for i, v in enumerate(row):
            widths[i] = max(widths[i], len(v))

    def fmt_row(vals: list[str]) -> str:
        return "  ".join(v.ljust(widths[i]) for i, v in enumerate(vals))

    lines = [fmt_row(columns), fmt_row(["-" * w for w in widths])]
    lines.extend(fmt_row(row) for row in str_rows)
    return "\n".join(lines)


def run_query(sql: str) -> str:
    sql = sql.strip()
    if not sql:
        return "No query provided."

    uri = f"file:{db.DB_PATH}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
    except sqlite3.OperationalError as e:
        return f"Could not open database read-only: {e}"

    try:
        cur = conn.execute(sql)
        rows = cur.fetchmany(MAX_ROWS + 1)
        columns = [d[0] for d in cur.description] if cur.description else []
    except sqlite3.Error as e:
        return f"Query failed: {e}"
    finally:
        conn.close()

    if not columns:
        return "Query ran, but returned no columns (not a SELECT?)."

    row_truncated = len(rows) > MAX_ROWS
    table = _format_table(columns, rows[:MAX_ROWS])
    body = html.escape(table)

    suffix = f"\n\n<i>Showing first {MAX_ROWS} rows.</i>" if row_truncated else ""
    overhead = len("<pre></pre>") + len(suffix) + 60  # margin for the truncation note itself
    output_truncated = len(body) > MAX_MESSAGE_CHARS - overhead
    if output_truncated:
        body = body[: MAX_MESSAGE_CHARS - overhead]

    text = f"<pre>{body}</pre>{suffix}"
    if output_truncated:
        text += "\n<i>Output truncated - narrow your query (fewer columns/rows).</i>"

    return text


def main() -> int:
    sql = os.environ.get("CHARTINK_SQL", "")
    print(f"Running query:\n{sql}\n")

    result = run_query(sql)
    print(result)

    header = f"<b>🔎 Query result</b>\n<code>{html.escape(sql[:200])}</code>\n\n"
    send_telegram_message(header + result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
