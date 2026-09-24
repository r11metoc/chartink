"""Send Telegram messages summarizing scan results."""

from __future__ import annotations

import os

import requests

_KIND_ICON = {"fresh": "🚀", "retest": "🔁"}
_META_KEYS = ("_symbol", "_current_row", "_backtest_hits", "_sector_share", "scanner_name", "kind", "detected_at")


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


def _price_delta(row: dict) -> float | None:
    """current price minus trigger price, or None if either is unknown.
    'row' holds the trigger-time values; row['_current_row'] holds the
    current ones."""
    current_row = row.get("_current_row")
    if not current_row:
        return None
    headers = [k for k in row.keys() if k not in _META_KEYS]
    price_key = _find_column(headers, "price")
    if not price_key:
        return None
    triggered = _as_float(row.get(price_key))
    current = _as_float(current_row.get(price_key))
    if triggered is None or current is None:
        return None
    return current - triggered


def _price_status(row: dict) -> str:
    """Mechanical rule, evaluated per scanner: BUY only if the current known
    price is above the price recorded when the breakout triggered, otherwise
    HOLD. This is the user's own stated rule applied to stored numbers, not
    an independent recommendation."""
    delta = _price_delta(row)
    if delta is None:
        return ""
    headers = [k for k in row.keys() if k not in _META_KEYS]
    price_key = _find_column(headers, "price")
    current_row = row["_current_row"]
    if delta > 0:
        return f"  🟢 BUY (₹{row[price_key]} → ₹{current_row[price_key]})"
    return f"  ⏸ HOLD (₹{row[price_key]} → ₹{current_row[price_key]})"


def _backtest_context(row: dict) -> str:
    """Descriptive-only context from Chartink's own backtest export: how
    often this exact symbol has triggered this scanner before, and roughly
    how common its sector is among the scanner's historical hits. Not a
    return prediction - the backtest data has no price/outcome history."""
    parts = []
    hits = row.get("_backtest_hits")
    if hits:
        parts.append(f"seen {len(hits)}x before, last {hits[-1]}")
    share = row.get("_sector_share")
    if share and share[1]:
        matches, total = share
        parts.append(f"sector ~{round(100 * matches / total)}% of history")
    return f"\n      📚 {' · '.join(parts)}" if parts else ""


def _format_symbol_line(row: dict, prefix: str = "") -> str:
    headers = [k for k in row.keys() if k not in _META_KEYS]
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
    base = f"  {label}  {details}" if details else f"  {label}"
    return base + _price_status(row) + _backtest_context(row)


def _format_rows(rows: list[dict]) -> list[str]:
    """Render rows sorted by % change (biggest movers first), pulling out
    price/change/volume/industry when those columns exist."""
    if not rows:
        return ["  (no symbols)"]

    headers = [k for k in rows[0].keys() if k not in _META_KEYS]
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
        headers = [k for k in kind_rows[0][1].keys() if k not in _META_KEYS]
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


def _sector_table(windows: dict) -> str:
    """Monospace table: sector, 7-day count, 30-day count - sorted by the
    30-day count so the most persistently active sector leads."""
    weekly = dict(windows.get("weekly") or [])
    monthly = dict(windows.get("monthly") or [])
    sectors = sorted(set(weekly) | set(monthly), key=lambda s: monthly.get(s, 0), reverse=True)[:5]
    if not sectors:
        return "<pre>no hits</pre>"
    rows = [f"{'Sector':<22}{'7d':>4}{'30d':>5}"]
    for s in sectors:
        rows.append(f"{s[:22]:<22}{weekly.get(s, 0):>4}{monthly.get(s, 0):>5}")
    return "<pre>" + "\n".join(rows) + "</pre>"


def _outcome_table(outcomes: list[dict]) -> str:
    """Monospace table: date, symbol, % return, BUY/HOLD result."""
    rows = [f"{'Date':<11}{'Symbol':<13}{'Ret%':>7}  Result"]
    for o in outcomes:
        result = "BUY " if o["label"] == 1 else "HOLD"
        rows.append(f"{o['hit_date']:<11}{o['symbol'][:13]:<13}{o['pct_return']:>+6.1f}%  {result}")
    return "<pre>" + "\n".join(rows) + "</pre>"


def format_digest_message(
    entries: list[dict],
    days: int,
    sector_focus: dict | None = None,
    recent_outcomes: list[dict] | None = None,
    outcome_params: tuple[int, float] | None = None,
) -> str:
    """entries: breakout rows from db.breakouts_since(), each with
    scanner_name/symbol/kind/detected_at plus the scan's own columns.
    sector_focus: {scanner_name: {"weekly": [(sector, count), ...], "monthly": [...]}}
    from Chartink's backtest history, shown per scanner regardless of
    whether there were any live breakouts in this window.
    recent_outcomes: backtest_outcomes rows (db.outcomes_with_context with
    since_date) - real BUY/HOLD results from actual historical price data,
    distinct from the live entries above which only exist once the scan
    itself has run long enough to see a change."""
    DIVIDER = "━━━━━━━━━━━━━━━━━━━━"
    lines = [f"<b>📊 Chartink digest</b> (last {days} days)"]

    # --- Live scan activity (from this repo's own scheduled scans) ---
    lines.append(f"\n{DIVIDER}\n<b>🔴 Live scan activity</b> (from this tool's own scans)")

    if not entries:
        lines.append("  No breakouts recorded in this window yet.")

    by_symbol: dict[str, list[dict]] = {}
    for e in entries:
        by_symbol.setdefault(e["symbol"], []).append(e)

    recurring = {s: es for s, es in by_symbol.items() if len(es) > 1}
    if recurring:
        lines.append("\n<b>⭐ Top recurring symbols</b>")
        for symbol, es in sorted(recurring.items(), key=lambda kv: len(kv[1]), reverse=True):
            scanners = [e["scanner_name"] for e in es]
            summary = ", ".join(f"{name} x{scanners.count(name)}" for name in dict.fromkeys(scanners))
            earliest = min(es, key=lambda e: e["detected_at"])
            lines.append(f"  <b>{symbol}</b> — {len(es)}x ({summary})" + _price_status(earliest))

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

    # --- Backtest-derived context (historical, from Chartink's own export + Yahoo Finance prices) ---
    if sector_focus:
        lines.append(f"\n{DIVIDER}\n<b>🏭 Sectors in focus</b> (backtest history, per scanner)")
        for scanner_name, windows in sector_focus.items():
            lines.append(f"\n<b>{scanner_name}</b>")
            lines.append(_sector_table(windows))

    if recent_outcomes:
        horizon_days, threshold_pct = outcome_params or (None, None)
        rule = f"+{threshold_pct:g}% within {horizon_days}d = real breakout" if horizon_days else ""
        lines.append(f"\n{DIVIDER}\n<b>📜 Backtest outcomes</b> (last {days} days{f', {rule}' if rule else ''})")

        total = len(recent_outcomes)
        wins = sum(1 for o in recent_outcomes if o["label"] == 1)
        lines.append(f"Overall: {wins}/{total} real breakouts ({wins / total:.0%})")

        by_scanner: dict[str, list[dict]] = {}
        for o in recent_outcomes:
            by_scanner.setdefault(o["scanner_name"], []).append(o)

        max_per_scanner = 5
        for scanner_name, outcomes in by_scanner.items():
            w = sum(1 for o in outcomes if o["label"] == 1)
            lines.append(f"\n<b>{scanner_name}</b> — {w}/{len(outcomes)} ({w / len(outcomes):.0%})")
            lines.append(_outcome_table(outcomes[:max_per_scanner]))
            if len(outcomes) > max_per_scanner:
                lines.append(f"  ...+{len(outcomes) - max_per_scanner} more this scanner")

        lines.append("\n<i>Full list: query backtest_outcomes in data/chartink.db</i>")

    return "\n".join(lines)


def format_buy_hold_message(scans: list, trigger_lookup: dict) -> str:
    """Every symbol currently on each scanner, split into a BUY list
    (current price above the price it had when it first triggered that
    scanner) and a HOLD list (at or below). trigger_lookup maps
    (scanner_name, symbol) -> trigger row dict or None if unknown."""
    lines = ["<b>🎯 Buy / Hold list</b> (current price vs. trigger price, per scanner)"]

    for scan in scans:
        buy_lines, hold_lines, unknown_symbols = [], [], []

        for row in scan.rows:
            symbol = row.get("_symbol", "?")
            trigger = trigger_lookup.get((scan.scanner_name, symbol))
            if trigger is None:
                unknown_symbols.append(symbol)
                continue
            merged = dict(trigger)
            merged["_current_row"] = row
            delta = _price_delta(merged)
            line = "  " + _format_symbol_line(merged).lstrip()
            if delta is not None and delta > 0:
                buy_lines.append(line)
            else:
                hold_lines.append(line)

        lines.append(f"\n<b>{scan.scanner_name}</b>")
        lines.append(f"  🟢 BUY ({len(buy_lines)})")
        lines.extend(buy_lines or ["    (none)"])
        lines.append(f"  ⏸ HOLD ({len(hold_lines)})")
        lines.extend(hold_lines or ["    (none)"])
        if unknown_symbols:
            lines.append(f"  ❓ No trigger data yet: {', '.join(unknown_symbols)}")

    return "\n".join(lines)
