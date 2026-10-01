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


def _track_line(track: dict | None) -> str:
    """How similar setups did in the backtest (track_record.TrackRecord.lookup)."""
    if not track:
        return ""
    vs = f", {track['vs_index']:+.1f}% vs Nifty 500" if track["vs_index"] is not None else ""
    return ("     " + html.escape(f"📊 Past {track['group']}: {track['n']} trades, {track['win']}% won, "
                                 f"avg {track['avg']:+.1f}%{vs}"))


def _learned_line(learned: dict | None) -> str:
    """The learned call on a signal (policy.verdict)."""
    if not learned:
        return ""
    if not learned["take"]:
        return "     " + html.escape(f"🧠 Skip: {learned['why']}")
    note = f" ({learned['status']})" if learned["status"] in ("proven", "promising") else ""
    return "     " + html.escape(f"🧠 Take: {learned['why']}{note}")


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
            lines.append(_track_line(row.get("_track")))
            lines.append(_learned_line(row.get("_learned")))
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
        lines = [f"{'Symbol':<10} {'Trig':>8} {'Now':>8} {'Chg':>7}"]
        for i in group:
            m = move(i)
            chg = f"{m:+.2f}%" if m is not None else "-"
            lines.append(f"{i['symbol'][:10]:<10} {_fmt_price(i['trig']):>8} {_fmt_price(i['now']):>8} {chg:>7}{i.get('mark', '')}")
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


def _sector_momentum_block(m: dict, limit: int = 8) -> str:
    """Compact table of export_dashboard.sector_momentum_view(): stocks picked
    in the last m['days'] days across all scanners, change vs the period
    before, scanners agreeing, average move since pick."""
    rows = [r for r in m["rows"] if r["cur"]][:limit]
    if not rows:
        return ""
    lines = [f"{'Sector':<16}{'Now':>4}{'Chg':>5}{'Sc':>4}{'Avg':>8}"]
    for r in rows:
        avg = f"{r['avg_move']:+.1f}%" if r["avg_move"] is not None else "-"
        lines.append(f"{r['sector'][:16]:<16}{r['cur']:>4}{r['cur'] - r['prev']:>+5}{len(r['scanners']):>4}{avg:>8}")
    return (
        f"<b>📈 Sector momentum</b> (last {m['days']}d, all scanners)\n"
        "<pre>" + html.escape("\n".join(lines)) + "</pre>\n"
        f"<i>Now = stocks picked · Chg = vs the {m['days']}d before · Sc = scanners agreeing · "
        "Avg = move since picked</i>"
    )


def _paper_block(paper: dict) -> str:
    """Compact table of paper.summarize(): closed trades, win rate, average
    return and open trades per scanner, then rupee totals. paper =
    {"start": ISO date, "stake": rupees, "summary": [...]}"""
    summary = paper["summary"]
    if not summary or not summary[0]["signals"]:
        return ""
    lines = [f"{'Scanner':<15}{'Done':>5}{'Won':>5}{'Avg':>7}{'Open':>5}"]
    for g in summary:
        name = "All" if g["group"] == "All scanners" else g["group"]
        won = f"{g['win']}%" if g["win"] is not None else "-"
        avg = f"{g['avg']:+.1f}%" if g["avg"] is not None else "-"
        lines.append(f"{name[:15]:<15}{g['closed']:>5}{won:>5}{avg:>7}{g['open']:>5}")
    total = summary[0]
    vs = f" · vs Nifty 500 {total['vs_index']:+.1f}%" if total["vs_index"] is not None else ""
    since = datetime.fromisoformat(paper["start"]).strftime("%d %b")
    rupees = lambda v: f"{'+' if v > 0 else '−' if v < 0 else ''}₹{abs(v):,}"
    block = (
        f"<b>📒 Paper portfolio</b> (since {since}, ₹{paper['stake'] / 100_000:g}L a trade)\n"
        "<pre>" + html.escape("\n".join(lines)) + "</pre>\n"
        + html.escape(f"Closed P&L {rupees(total['closed_pnl'])} · open {rupees(total['open_pnl'])}{vs} · "
                      f"{total['waiting']} waiting for entry")
    )
    learned = paper.get("learned") or {}
    if learned.get("summary"):
        lt = learned["summary"][0]
        won = f", {lt['win']}% won" if lt["win"] is not None else ""
        block += "\n" + html.escape(
            f"🧠 Learned book (since {datetime.fromisoformat(learned['start']).strftime('%d %b')}): "
            f"{lt['closed']} done{won} · closed {rupees(lt['closed_pnl'])} · open {rupees(lt['open_pnl'])} · "
            f"{lt['waiting']} waiting · {lt['skipped']} skipped")
    return block


def format_digest_message(entries: list[dict], days: int, sector_momentum: dict | None = None,
                          paper: dict | None = None) -> str:
    """Stocks that triggered on a scanner in the last `days`, as BUY / HOLD
    tables per scanner, then the sector momentum table if given. entries come
    from db.breakouts_since() (newest first) with _current_row (latest scraped
    row) and _on_scan (still on the scanner)."""
    blocks = [f"<b>📊 Digest</b> · triggers in last {days}d · {_now_ist()}\n{RULE_LINE}"]
    if not entries:
        blocks.append("No new triggers in this window.")

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
        blocks.append("<i>* no longer on the scanner - price is the latest daily close</i>")
    if paper and (block := _paper_block(paper)):
        blocks.append(block)
    if sector_momentum and (block := _sector_momentum_block(sector_momentum)):
        blocks.append(block)
    return "\n\n".join(blocks)
