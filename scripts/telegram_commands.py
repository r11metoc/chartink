"""Answer Telegram commands sent to the bot (only from TELEGRAM_CHAT_ID).

The bot pushes only today's actions on its own. Everything else is on request:

  /today         what to do now (sells, buy-stops to place, recent buys)
  /holdings      open positions with P&L, plus booked P&L
  /scanners      every stock on each scanner in the latest scan
  /breakouts     recent scanner entries and sector focus (last 30 days)
  /fundamentals  top of your latest Screener export (Valuepick shortlist)
  /help          this list

Runs from scan.yml on every 15-minute tick, so a reply takes as long as
GitHub takes to start that run (usually 15-60 minutes).
"""

from __future__ import annotations

import html
import json
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

import requests

import db
from notify import send_telegram_message
from slot_gate import IST

COMMANDS = {
    "today": "What to do now",
    "holdings": "Open positions and P&L",
    "scanners": "Stocks on each scanner now",
    "breakouts": "Recent entries and sector focus",
    "fundamentals": "Top of your Screener export",
    "help": "List the commands",
}
SITE = "https://r11metoc.github.io/chartink/"


def _api(token: str, method: str, **params):
    r = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=params, timeout=20)
    r.raise_for_status()
    return r.json().get("result")


def pending(token: str, chat_id: str) -> tuple[list[str], int | None]:
    """Commands from our chat since the last call, and the offset to confirm them."""
    ups = _api(token, "getUpdates", timeout=0, allowed_updates=["message"]) or []
    cmds, last = [], None
    for u in ups:
        last = u["update_id"]
        m = u.get("message") or {}
        if str((m.get("chat") or {}).get("id")) != str(chat_id):
            continue  # ignore anyone else who finds the bot
        text = (m.get("text") or "").strip()
        if text.startswith("/"):
            cmds.append(text[1:].split()[0].split("@")[0].lower())
    return cmds, last


def _states():
    import dipzone
    conn = db.connect()
    try:
        return dipzone.live_states(conn, datetime.now(IST))
    finally:
        conn.close()


def _view():
    import dipzone
    return dipzone.dashboard_view(_states())


def _dt(iso) -> str:
    return datetime.fromisoformat(str(iso)[:10]).strftime("%d %b") if iso else "–"


def _m(v) -> str:
    return "–" if v is None else f"{v:,.2f}"


def today_msg() -> str:
    v = _view()
    cutoff = (datetime.now(IST) - timedelta(days=4)).date().isoformat()
    sells = [h for h in v["holding"] if h.get("sell_signal")]
    stops = [b for b in v["buy_list"] if b["stage"] == "breakout"]
    bought = [h for h in v["holding"] if h["entry_date"] >= cutoff and not h.get("sell_signal")]
    lines = ["📋 <b>To do now</b>"]
    for h in sells:
        lines.append(f"🔻 Sell <b>{h['symbol']}</b> at next open · {h['ret']:+.1f}%")
    for b in stops:
        ml = f" · ML {b['ml']}" if b.get("ml") is not None else ""
        lines.append(f"🟡 <b>{b['symbol']}</b> above {_m(b['level'])} · SL {_m(b['stop'])} · signal {_dt(b['signal'])}{ml}")
    for h in bought:
        lines.append(f"🟢 Bought <b>{h['symbol']}</b> {_m(h['entry'])} on {_dt(h['entry_date'])} · SL {_m(h['stop'])}")
    if len(lines) == 1:
        lines.append("Nothing to do.")
    return "\n".join(lines)


def holdings_msg() -> str:
    v = _view()
    hold = sorted(v["holding"], key=lambda h: -h["ret"])
    open_pnl = sum(h["pnl"] for h in hold)
    booked = sum(c["pnl"] for c in v["closed"])
    lines = [f"💼 <b>Holdings</b> {len(hold)}/15 · open ₹{open_pnl:,} · booked ₹{booked:,}", "<pre>"]
    for h in hold:
        flag = " SELL" if h.get("sell_signal") else ""
        lines.append(f"{h['symbol'][:11]:11} {h['ret']:+6.1f}% {h['entry']:>9,.1f}→{h['now']:>9,.1f}{flag}")
    lines.append("</pre>" if hold else "none</pre>")
    return "\n".join(lines)


def scanners_msg() -> str:
    import dipzone
    from notify import format_scan_message
    conn = db.connect()
    try:
        run = conn.execute("SELECT MAX(id) FROM runs").fetchone()[0]
        scans = []
        for (name,) in conn.execute("SELECT DISTINCT scanner_name FROM results WHERE run_id = ? ORDER BY scanner_name", (run,)):
            rows = [json.loads(r) for (r,) in conn.execute(
                "SELECT row_json FROM results WHERE run_id = ? AND scanner_name = ?", (run, name))]
            scans.append(SimpleNamespace(scanner_name=name, rows=rows))
    finally:
        conn.close()
    trig = {k: {"Price": f"{t:.2f}"} for k, t in dipzone.trigger_map(_states()).items()}
    return format_scan_message(scans, trig)


def breakouts_msgs() -> list[str]:
    from run import digest_messages
    conn = db.connect()
    try:
        names = [n for (n,) in conn.execute("SELECT DISTINCT scanner_name FROM results")]
        return digest_messages(conn, 30, names)
    finally:
        conn.close()


def fundamentals_msg() -> str:
    import fundamental_scan
    v = fundamental_scan.view()
    if not v:
        return "No Screener export uploaded yet (More → Upload in the app)."
    clean = [x for x in v["stocks"] if x["verdict"] == "Shortlist"][:10]
    lines = [f"📊 <b>Fundamental scan</b> · export {v['asof']} · {len(v['stocks'])} stocks", "Clean shortlist (Valuepick ≥ 65, no flags):", "<pre>"]
    for x in clean:
        pe = f"{x['pe']:.0f}" if x["pe"] else "–"
        lines.append(f"{(x['name'] or x['code'])[:16]:16} {x['score']:>4.0f}  P/E {pe:>3}  {'✓' if x['screen']['ok'] else ' '}")
    lines.append("</pre>✓ = passes your main screen. Full list: More → Fundamentals.")
    return "\n".join(lines)


def help_msg() -> str:
    rows = "\n".join(f"/{k} — {v}" for k, v in COMMANDS.items())
    return (f"I send only today's actions on my own. Ask for the rest:\n{rows}\n\n"
            f"Replies come with the next GitHub run (usually 15–60 min). Everything is also on {SITE}")


HANDLERS = {"today": today_msg, "holdings": holdings_msg, "scanners": scanners_msg,
            "breakouts": breakouts_msgs, "fundamentals": fundamentals_msg, "help": help_msg, "start": help_msg}


def main() -> int:
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set.")
        return 0
    cmds, last = pending(token, chat_id)
    if last is not None:
        _api(token, "getUpdates", offset=last + 1, timeout=0)  # confirm, so they aren't answered twice
    if not cmds:
        print("No commands.")
        return 0
    try:
        _api(token, "setMyCommands", commands=[{"command": k, "description": v} for k, v in COMMANDS.items()])
    except Exception:
        pass
    for c in dict.fromkeys(cmds):  # each command once per run
        h = HANDLERS.get(c)
        try:
            out = h() if h else f"Unknown command /{html.escape(c)}.\n\n" + help_msg()
        except Exception as e:  # one failing command must not block the others
            out = f"/{c} failed ({e.__class__.__name__}). Try again later or check the website."
        for msg in out if isinstance(out, list) else [out]:
            send_telegram_message(msg)
        print(f"Answered /{c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
