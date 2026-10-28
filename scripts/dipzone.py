"""Live rule: buy at the breakout above the trigger, ride the trend.

For every signal (the scanner's trigger = the signal candle's high, the
week's high for Wkly_upswing):
1. buy-stop : from the next session, buy when the price trades above the
              trigger, within 3 sessions (5 after a weekly signal). Filled at
              the trigger, or at the open on a gap-up.
2. exit     : sell at the next open after a close below the 50-day average,
              a 12% stop below the buy price (15% Wkly_upswing), or after 250
              sessions (~1 year).
Backtest 2021-26, same signals: +5.8% a trade and 46% wins vs +4.2% / 41%
for waiting for a pullback, worst portfolio fall -10% vs -18%.
Filters: Wkly_upswing only when daily ATR(14) < 4% of the close;
63_30_daily only within 10% of the 52-week high. Signals another scanner
also flagged in the 10 days before are tagged "confirmed".

The pullback ("dip") rule is kept in `simulate` for the exit comparison in
the weekly report. Decisions use completed daily candles only.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

import breakout_sim as bs
import db
from slot_gate import IST

DIP_PCT = {"63_30_daily": 3.0, "Bullish_Scanner": 3.0, "Wkly_upswing": 5.0}
DEFAULT_DIP = 3.0
FLOOR_PCT = 5.0       # the dip close must stay within 5% below the trigger
ZONE_DAYS = 20        # sessions after the breakout to wait for the dip
TARGET_PCT = 8.0
STOP_PCT = 12.0
STOP_BY_SCANNER = {"Wkly_upswing": 15.0}  # weekly picks swing more (backtest: 70% wins vs 68% at 12%)
ATR_MAX_PCT = {"Wkly_upswing": 4.0}       # daily ATR(14) under 4% of the close (2023-26: 74% wins vs 68%)
MAX_HOLD = 40         # sessions (8 weeks) - the old +8% target rule (kept for comparison)
EXIT_MA = 50          # live exit: sell at the next open after a close below this daily average
RIDE_MAX_HOLD = 250   # sessions (~1 year) before a riding position is sold anyway
CLOSED = ("target", "stop", "time", "average")
NEAR_HIGH_PCT = {"63_30_daily": 10.0}  # only take signals within this % of the 52-week high
CONFIRM_DAYS = 10     # another scanner within this many days before = confirmed
HISTORY_DAYS = 400    # calendar days of prices needed for the 52-week high
START = "2026-09-25"  # live signals from this date are tracked
ALERT_DAYS = 4        # only alert on events this recent (no flood on the first run)
STAKE = 100_000
MARKET_CLOSE = (15, 30)
ACTIVE = {"waiting for breakout", "watching for dip", "buy zone", "holding"}
LIVE_MODE = "breakout"  # "breakout" (buy-stop at the trigger) or "dip" (wait for the pullback)


def dip_for(scanner: str) -> float:
    return DIP_PCT.get(scanner, DEFAULT_DIP)


def dist_52w_high(df: pd.DataFrame, end_pos: int) -> float | None:
    """Signal-day close vs the highest high of the last 252 sessions, in %
    (None with under 120 sessions of history)."""
    win = df.iloc[max(0, end_pos - 251):end_pos + 1]
    if len(win) < 120:
        return None
    return round((float(df["Close"].iloc[end_pos]) / float(win["High"].max()) - 1) * 100, 2)


def stop_for(scanner: str) -> float:
    return STOP_BY_SCANNER.get(scanner, STOP_PCT)


def atr_pct(df: pd.DataFrame, end_pos: int) -> float | None:
    """Daily ATR(14) as % of the close at the signal bar."""
    if end_pos < 14:
        return None
    w = df.iloc[max(0, end_pos - 40):end_pos + 1]
    prev = w["Close"].shift(1)
    tr = pd.concat([w["High"] - w["Low"], (w["High"] - prev).abs(), (w["Low"] - prev).abs()], axis=1).max(axis=1)
    v = tr.rolling(14).mean().iloc[-1] / w["Close"].iloc[-1] * 100  # same as breakout_sim's atr_pct
    return None if pd.isna(v) else round(float(v), 2)


def passes_filter(scanner: str, dist: float | None, atr: float | None = None) -> bool:
    lim = NEAR_HIGH_PCT.get(scanner)
    if lim is not None and dist is not None and dist < -lim:
        return False
    amax = ATR_MAX_PCT.get(scanner)
    return amax is None or atr is None or atr < amax


def skip_reason(scanner: str, dist: float | None, atr: float | None) -> str:
    lim = NEAR_HIGH_PCT.get(scanner)
    if lim is not None and dist is not None and dist < -lim:
        return f"{-dist:.0f}% below its 52-week high (limit {lim:g}%)"
    return f"too volatile: daily ATR {atr:.1f}% of price (limit {ATR_MAX_PCT[scanner]:g}%)"


def simulate(fwd: pd.DataFrame, trigger: float, scanner: str, ma: np.ndarray | None = None) -> dict:
    """Run the rule over the daily bars after the signal bar. With `ma` (the
    EXIT_MA-day average aligned to `fwd`) the position rides until a close
    below it (the live rule); without it, the old +8% target rule."""
    o, h, l, c = (fwd[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    dates = fwd.index
    n = len(c)
    window = bs.entry_window_for(scanner)
    out = {"trigger": trigger, "dip_pct": dip_for(scanner)}
    b = next((i for i in range(min(window, n)) if h[i] > trigger), None)
    if b is None:
        out["status"] = "waiting for breakout" if n < window else "no breakout"
        return out
    out["breakout_date"] = dates[b]
    floor = trigger * (1 - FLOOR_PCT / 100)
    hi = c[b]
    dip_i = None
    for i in range(b + 1, min(n, b + 1 + ZONE_DAYS)):
        hi = max(hi, c[i - 1])
        if c[i] <= hi * (1 - out["dip_pct"] / 100) and c[i] >= floor:
            dip_i = i
            break
    if dip_i is None:
        out["status"] = "watching for dip" if n < b + 1 + ZONE_DAYS else "no dip"
        out["high_close"] = float(max(c[b:]))
        out["buy_below"] = round(out["high_close"] * (1 - out["dip_pct"] / 100), 2)
        return out
    out.update(dip_date=dates[dip_i], dip_close=float(c[dip_i]), high_close=float(hi))
    e = dip_i + 1
    if e >= n:
        out["status"] = "buy zone"  # buy at the next open
        return out
    ep = float(o[e])
    tgt, stp = ep * (1 + TARGET_PCT / 100), ep * (1 - stop_for(scanner) / 100)
    out.update(entry_date=dates[e], entry=ep, target=tgt, stop=stp)
    if ma is not None:
        return _ride_ma(out, o, l, c, dates, e, ep, stp, ma)
    last = min(n - 1, e + MAX_HOLD)
    for i in range(e, last + 1):
        if i > e and o[i] <= stp:
            return {**out, "status": "stop", "exit_date": dates[i], "exit": float(o[i])} | _ret(ep, o[i])
        if l[i] <= stp:
            return {**out, "status": "stop", "exit_date": dates[i], "exit": stp} | _ret(ep, stp)
        if i > e and o[i] >= tgt:
            return {**out, "status": "target", "exit_date": dates[i], "exit": float(o[i])} | _ret(ep, o[i])
        if h[i] >= tgt:
            return {**out, "status": "target", "exit_date": dates[i], "exit": tgt} | _ret(ep, tgt)
    if e + MAX_HOLD <= n - 1:
        return {**out, "status": "time", "exit_date": dates[last], "exit": float(c[last])} | _ret(ep, c[last])
    return {**out, "status": "holding", "now": float(c[-1]), "sessions_left": e + MAX_HOLD - (n - 1)} | _ret(ep, c[-1])


def simulate_breakout(fwd: pd.DataFrame, trigger: float, scanner: str, ma: np.ndarray) -> dict:
    """The live rule over the daily bars after the signal bar: buy when the
    price trades above the trigger within the entry window (filled at the
    trigger, or the open on a gap-up), then ride until a close below the
    EXIT_MA-day average (`ma` aligned to `fwd`)."""
    o, h, l, c = (fwd[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    dates = fwd.index
    n = len(c)
    window = bs.entry_window_for(scanner)
    out = {"trigger": trigger, "mode": "breakout"}
    b = next((i for i in range(min(window, n)) if h[i] > trigger), None)
    if b is None:
        out["status"] = "waiting for breakout" if n < window else "no breakout"
        out["sessions_left"] = max(window - n, 0)
        return out
    ep = max(float(o[b]), float(trigger))
    stp = ep * (1 - stop_for(scanner) / 100)
    out.update(breakout_date=dates[b], entry_date=dates[b], entry=ep, stop=stp, target=None, gap=bool(o[b] > trigger))
    return _ride_ma(out, o, l, c, dates, b, ep, stp, ma)


def _ride_ma(out, o, l, c, dates, e, ep, stp, ma) -> dict:
    out["target"] = None
    n = len(c)
    last = min(n - 1, e + RIDE_MAX_HOLD)
    for i in range(e, last + 1):
        if i > e and o[i] <= stp:
            return {**out, "status": "stop", "exit_date": dates[i], "exit": float(o[i])} | _ret(ep, o[i])
        if l[i] <= stp:
            return {**out, "status": "stop", "exit_date": dates[i], "exit": stp} | _ret(ep, stp)
        if i > e and not np.isnan(ma[i]) and c[i] < ma[i]:
            if i + 1 <= n - 1:
                return {**out, "status": "average", "exit_date": dates[i + 1], "exit": float(o[i + 1]),
                        "signal_date": dates[i], "ma": float(ma[i])} | _ret(ep, o[i + 1])
            return {**out, "status": "holding", "sell_signal": dates[i], "now": float(c[i]), "ma": float(ma[i]),
                    "sessions_left": 1} | _ret(ep, c[i])
    if e + RIDE_MAX_HOLD <= n - 1:
        return {**out, "status": "time", "exit_date": dates[last], "exit": float(c[last])} | _ret(ep, c[last])
    return {**out, "status": "holding", "now": float(c[-1]), "ma": float(ma[n - 1]) if not np.isnan(ma[n - 1]) else None,
            "sessions_left": e + RIDE_MAX_HOLD - (n - 1)} | _ret(ep, c[-1])


def exit_ma(df: pd.DataFrame, start: int) -> np.ndarray:
    """EXIT_MA-day average of the close, from bar `start` on (aligned to df.iloc[start:])."""
    return df["Close"].rolling(EXIT_MA, min_periods=EXIT_MA).mean().to_numpy()[start:]


def _ret(entry: float, exit_: float) -> dict:
    return {"ret": round((float(exit_) / entry - 1) * 100 - bs.COST_PCT, 2)}


# ----------------------------------------------------------------- live use

def _completed(df: pd.DataFrame, now: datetime) -> pd.DataFrame:
    """Drop today's candle while the market is still open."""
    if df.empty:
        return df
    today = pd.Timestamp(now.date())
    if df.index[-1] == today and (now.hour, now.minute) < MARKET_CLOSE:
        return df.iloc[:-1]
    return df


def live_states(conn, now: datetime | None = None) -> list[dict]:
    import paper  # local import: paper imports policy/track_record
    now = now or datetime.now(IST)
    lookback = (date.fromisoformat(START) - timedelta(days=HISTORY_DAYS)).isoformat()
    confirm_from = (date.fromisoformat(START) - timedelta(days=CONFIRM_DAYS)).isoformat()
    seen: dict[str, list[tuple[pd.Timestamp, str]]] = {}
    for d0, sc0, sym0, _ in paper._signals(conn, confirm_from):
        seen.setdefault(sym0, []).append((pd.Timestamp(d0), sc0))
    out = []
    active: set[tuple[str, str]] = set()  # one open idea per scanner + stock
    for day, scanner, symbol, source in paper._signals(conn, START):
        t = pd.Timestamp(day)
        if (scanner, symbol) in active:
            out.append({"scanner": scanner, "symbol": symbol, "date": day, "source": source,
                        "status": "duplicate", "why": "already watching or holding this stock for this scanner"})
            continue
        others = sorted({sc for d0, sc in seen.get(symbol, [])
                         if sc != scanner and t - pd.Timedelta(days=CONFIRM_DAYS) <= d0 <= t})
        df = _completed(paper._frame(conn, symbol, lookback), now)
        hit = pd.Timestamp(day)
        if not bs.is_weekly(scanner) and not df.empty and hit not in df.index and df.index[-1] > hit:
            earlier = df.index[df.index <= hit]
            hit = earlier[-1] if len(earlier) else hit
        sig = bs.signal_bar(df, hit, bs.is_weekly(scanner)) if not df.empty else None
        base = {"scanner": scanner, "symbol": symbol, "date": day, "source": source, "confirmed_by": others}
        if sig is None:
            out.append({**base, "status": "no prices yet"})
            continue
        base["dist_52w_high"] = dist_52w_high(df, sig["end_pos"])
        base["atr_pct"] = atr_pct(df, sig["end_pos"])
        if not passes_filter(scanner, base["dist_52w_high"], base["atr_pct"]):
            out.append({**base, "status": "skipped", "trigger": sig["trigger"],
                        "why": skip_reason(scanner, base["dist_52w_high"], base["atr_pct"])})
            continue
        st = live_sim(df, sig, scanner)
        if st["status"] == "waiting for breakout":
            st["valid_until"] = df.index[sig["end_pos"]] + pd.offsets.BDay(bs.entry_window_for(scanner))
        if st["status"] in ACTIVE:
            active.add((scanner, symbol))
        out.append({**base, **st, "last_close": float(df["Close"].iloc[-1]), "last_date": df.index[-1]})
    return out


def live_sim(df: pd.DataFrame, sig: dict, scanner: str) -> dict:
    """The live rule for one signal, on the full price frame."""
    fwd, ma = df.iloc[sig["end_pos"] + 1:], exit_ma(df, sig["end_pos"] + 1)
    if LIVE_MODE == "breakout":
        return simulate_breakout(fwd, sig["trigger"], scanner, ma)
    return simulate(fwd, sig["trigger"], scanner, ma)


def trigger_map(states: list[dict]) -> dict[tuple[str, str], float]:
    """(scanner, symbol) -> trigger of its latest signal: the signal candle's
    high (the day's high, or the week's high for Wkly_upswing). One trigger
    everywhere: website tabs and Telegram use this, as the dip rule does."""
    out = {}
    for s in states:  # states are in signal-date order, so the latest wins
        if s.get("trigger") is not None:
            out[(s["scanner"], s["symbol"])] = round(float(s["trigger"]), 2)
    return out


def _d(x) -> str:
    return pd.Timestamp(x).strftime("%d %b")


def _exit_by(s: dict) -> str:
    return _d(pd.Timestamp(s["entry_date"]) + pd.offsets.BDay(RIDE_MAX_HOLD)) if "entry_date" in s else "–"


def events(states: list[dict], now: datetime) -> list[tuple[str, dict, str]]:
    """(key, state, kind) for setup / buy / sell / exit events in the last ALERT_DAYS."""
    since = pd.Timestamp(now.date()) - pd.Timedelta(days=ALERT_DAYS)
    ev = []
    for s in states:
        if s.get("mode") == "breakout":
            if s.get("status") == "waiting for breakout":
                ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|setup", s, "setup"))
            if "entry_date" in s and s["entry_date"] >= since:
                ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|bought", s, "bought"))
        elif "dip_date" in s and s["dip_date"] >= since:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|buy", s, "buy"))
        if s.get("sell_signal") is not None and s["sell_signal"] >= since:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|sell", s, "sell"))
        if s.get("status") in CLOSED and s["exit_date"] >= since:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|exit", s, s["status"]))
    return ev


def new_events(conn, states: list[dict], now: datetime) -> list[tuple[str, dict, str]]:
    conn.execute("CREATE TABLE IF NOT EXISTS dip_alerts (key TEXT PRIMARY KEY, sent_at TEXT NOT NULL)")
    fresh = []
    for key, s, kind in events(states, now):
        if conn.execute("SELECT 1 FROM dip_alerts WHERE key = ?", (key,)).fetchone():
            continue
        conn.execute("INSERT INTO dip_alerts (key, sent_at) VALUES (?, ?)", (key, now.isoformat()))
        fresh.append((key, s, kind))
    conn.commit()
    return fresh


def _tags(s: dict) -> str:
    t = ""
    if s.get("confirmed_by"):
        t += " ⭐ also on " + ", ".join(s["confirmed_by"])
    if s.get("dist_52w_high") is not None:
        t += f" · {-s['dist_52w_high']:.0f}% off 52w high"
    return t


def format_alerts(fresh: list[tuple[str, dict, str]]) -> str | None:
    if not fresh:
        return None
    lines = ["🎯 <b>Breakout alerts</b>"]
    setups = [s for _, s, k in fresh if k == "setup"]
    if setups:
        lines += ["", "<b>SET A BUY-STOP</b> (buy only if the price trades above the trigger):"]
        for s in setups:
            stp = s["trigger"] * (1 - stop_for(s["scanner"]) / 100)
            until = f" until {_d(s['valid_until'])}" if s.get("valid_until") is not None else ""
            lines.append(f"🟡 <b>{s['symbol']}</b> ({s['scanner']}){_tags(s)}: buy above {s['trigger']:.2f}{until}. "
                         f"Stop ~{stp:.2f} (-{stop_for(s['scanner']):g}%), then hold while it closes above its {EXIT_MA}-day average")
    bought = [s for _, s, k in fresh if k == "bought"]
    if bought:
        lines += ["", "<b>BOUGHT</b> (crossed the trigger):"]
        for s in bought:
            gap = " on a gap-up open" if s.get("gap") else ""
            lines.append(f"🟢 <b>{s['symbol']}</b> ({s['scanner']}){_tags(s)} bought {_d(s['entry_date'])} at {s['entry']:.2f}{gap}. "
                         f"Stop {s['stop']:.2f} (-{stop_for(s['scanner']):g}%), sell on a close below the {EXIT_MA}-day average")
    buys = [s for _, s, k in fresh if k == "buy"]
    if buys:
        lines += ["", "<b>BUY ZONE</b> (buy at the next open):"]
        for s in buys:
            ref = s.get("entry", s["dip_close"])
            lines.append(f"🟢 <b>{s['symbol']}</b> ({s['scanner']}){_tags(s)} dipped {s['dip_pct']:g}% to {s['dip_close']:.2f} "
                         f"(trigger {s['trigger']:.2f}). Buy ~{ref:.2f}, stop {ref * (1 - stop_for(s['scanner']) / 100):.2f} "
                         f"(-{stop_for(s['scanner']):g}%), then hold while it closes above its {EXIT_MA}-day average")
    sells = [s for _, s, k in fresh if k == "sell"]
    if sells:
        lines += ["", f"<b>SELL</b> (closed below the {EXIT_MA}-day average, sell at the next open):"]
        for s in sells:
            lines.append(f"🔻 <b>{s['symbol']}</b> ({s['scanner']}) closed {s['now']:.2f} below its {EXIT_MA}-day average "
                         f"{s['ma']:.2f} on {_d(s['sell_signal'])}. Bought {s['entry']:.2f} ({s['ret']:+.1f}%)")
    icon = {"target": "✅", "stop": "🛑", "time": "⏱", "average": "📉"}
    label = {"target": "target hit", "stop": "stopped", "time": "a year up, sold", "average": f"sold below the {EXIT_MA}-day average"}
    exits = [(s, k) for _, s, k in fresh if k in icon]
    if exits:
        lines += ["", "<b>CLOSED</b>:"]
        for s, k in exits:
            lines.append(f"{icon[k]} <b>{s['symbol']}</b> ({s['scanner']}) {label[k]} {_d(s['exit_date'])}: "
                         f"{s['entry']:.2f} → {s['exit']:.2f} ({s['ret']:+.1f}%)")
    lines += ["", f"<i>Rule: buy when the price trades above the trigger (the signal candle's high) within "
                  f"{bs.entry_window_for('63_30_daily')} sessions ({bs.entry_window_for('Wkly_upswing')} weekly); "
                  f"-{STOP_PCT:g}% stop (-{STOP_BY_SCANNER.get('Wkly_upswing', STOP_PCT):g}% weekly), sell on a close below "
                  f"the {EXIT_MA}-day average or after a year. Backtest, not advice.</i>"]
    return "\n".join(lines)


def summary(states: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {"All scanners": states}
    for s in states:
        groups.setdefault(s["scanner"], []).append(s)
    out = []
    for g, xs in groups.items():
        closed = [x for x in xs if x.get("status") in CLOSED]
        hold = [x for x in xs if x.get("status") == "holding"]
        rets = [x["ret"] for x in closed]
        xs = [x for x in xs if x.get("status") != "duplicate"]
        out.append({"group": g, "signals": len(xs),
                    "watching": sum(x.get("status") in ("waiting for breakout", "watching for dip", "buy zone") for x in xs),
                    "holding": len(hold), "closed": len(closed),
                    "win": round(100 * np.mean([r > 0 for r in rets])) if rets else None,
                    "pnl": int(sum(r / 100 * STAKE for r in rets)),
                    "open_pnl": int(sum(x["ret"] / 100 * STAKE for x in hold))})
    return {"start": START, "rows": out}


def format_summary(book: dict) -> str:
    lines = [f"🎯 <b>Buy-the-dip paper book</b> (since {book['start']}, ₹1L a trade)", "<pre>",
             f"{'':16}{'Watch':>6}{'Hold':>5}{'Done':>5}{'Win':>5}{'P&L':>9}{'Open':>8}"]
    for r in book["rows"]:
        win = f"{r['win']}%" if r["win"] is not None else "–"
        lines.append(f"{r['group'][:16]:16}{r['watching']:>6}{r['holding']:>5}{r['closed']:>5}{win:>5}"
                     f"{r['pnl']:>9,}{r['open_pnl']:>8,}")
    lines.append("</pre>")
    return "\n".join(lines)


# ----------------------------------------------------------------- dashboard

def _iso(x) -> str | None:
    return None if x is None else pd.Timestamp(x).date().isoformat()


def _r(x) -> float | None:
    return None if x is None else round(float(x), 2)


def dashboard_view(states: list[dict], activity_days: int = 60) -> dict:
    """JSON for site/data.json: buy list, holdings, recent buys and sells."""
    buy_list, holding, activity, closed = [], [], [], []
    cutoff = pd.Timestamp(date.today()) - pd.Timedelta(days=activity_days)
    for s in states:
        base = {"scanner": s["scanner"], "symbol": s["symbol"], "signal": s["date"],
                "confirmed_by": s.get("confirmed_by", []), "off_high": s.get("dist_52w_high"),
                "trigger": _r(s.get("trigger")), "now": _r(s.get("last_close")), "now_date": _iso(s.get("last_date"))}
        st = s.get("status")
        if st == "waiting for breakout":
            buy_list.append({**base, "stage": "breakout", "level": _r(s["trigger"]),
                             "stop": _r(s["trigger"] * (1 - stop_for(s["scanner"]) / 100)),
                             "valid_until": _iso(s.get("valid_until"))})
        elif st == "watching for dip":
            buy_list.append({**base, "stage": "dip", "level": s["buy_below"], "high_close": _r(s["high_close"]),
                             "floor": _r(s["trigger"] * (1 - FLOOR_PCT / 100)), "dip_pct": s["dip_pct"],
                             "breakout": _iso(s["breakout_date"])})
        elif st == "buy zone":
            ref = s["dip_close"]
            buy_list.append({**base, "stage": "zone", "level": _r(ref), "dip_pct": s["dip_pct"],
                             "stop": _r(ref * (1 - stop_for(s["scanner"]) / 100))})
        if "entry_date" in s:
            trade = {**base, "entry_date": _iso(s["entry_date"]), "entry": _r(s["entry"]),
                     "target": _r(s.get("target")), "stop": _r(s["stop"]), "ma": _r(s.get("ma")),
                     "sell_signal": _iso(s.get("sell_signal")), "exit_by": _iso(
                         pd.Timestamp(s["entry_date"]) + pd.offsets.BDay(RIDE_MAX_HOLD)), "ret": s.get("ret")}
            if st == "holding":
                held = int(np.busday_count(pd.Timestamp(s["entry_date"]).date(), pd.Timestamp(s["last_date"]).date())) + 1
                holding.append({**trade, "pnl": int(s["ret"] / 100 * STAKE), "days": held,
                                "value": int(STAKE * (1 + s["ret"] / 100))})
            if st in CLOSED:
                closed.append({**trade, "exit_date": _iso(s["exit_date"]), "exit": _r(s["exit"]), "reason": st,
                               "pnl": int(s["ret"] / 100 * STAKE),
                               "days": int(np.busday_count(pd.Timestamp(s["entry_date"]).date(),
                                                           pd.Timestamp(s["exit_date"]).date())) + 1})
            if pd.Timestamp(s["entry_date"]) >= cutoff:
                activity.append({**trade, "side": "BUY", "when": trade["entry_date"], "price": trade["entry"]})
            if st in CLOSED and pd.Timestamp(s["exit_date"]) >= cutoff:
                activity.append({**trade, "side": "SELL", "when": _iso(s["exit_date"]), "price": _r(s["exit"]),
                                 "reason": st, "pnl": int(s["ret"] / 100 * STAKE)})
    order = {"zone": 0, "dip": 1, "breakout": 2}
    buy_list.sort(key=lambda x: (order[x["stage"]], x["signal"]), reverse=False)
    holding.sort(key=lambda x: x["entry_date"], reverse=True)
    activity.sort(key=lambda x: (x["when"], x["side"] == "SELL"), reverse=True)
    closed.sort(key=lambda x: x["exit_date"], reverse=True)
    skipped = sum(s.get("status") == "skipped" for s in states)
    return {"rule": {"mode": LIVE_MODE, "entry_days": bs.entry_window_for("63_30_daily"),
                     "entry_days_weekly": bs.entry_window_for("Wkly_upswing"),
                     "dip": DIP_PCT, "floor": FLOOR_PCT, "zone_days": ZONE_DAYS, "target": None, "exit_ma": EXIT_MA,
                     "stop": STOP_PCT, "stop_by": STOP_BY_SCANNER, "atr_max": ATR_MAX_PCT, "max_hold": RIDE_MAX_HOLD, "stake": STAKE,
                     "near_high": NEAR_HIGH_PCT},
            "skipped": skipped,
            "summary": summary(states), "buy_list": buy_list, "holding": holding, "activity": activity,
            "closed": closed}


# ------------------------------------------------------------ backtest report

def backtest_trades(hits: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Every closed backtest trade under the live rule (filters applied)."""
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        if not passes_filter(h["scanner_name"], dist_52w_high(df, sig["end_pos"]), atr_pct(df, sig["end_pos"])):
            continue
        s = live_sim(df, sig, h["scanner_name"])
        if s["status"] in CLOSED:
            rows.append({"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                         "status": s["status"], "ret": s["ret"],
                         "entry_date": pd.Timestamp(s["entry_date"]), "exit_date": pd.Timestamp(s["exit_date"]),
                         "days": int(np.busday_count(pd.Timestamp(s["entry_date"]).date(),
                                                     pd.Timestamp(s["exit_date"]).date())) + 1})
    return pd.DataFrame(rows)


def backtest_section(hits: pd.DataFrame, prices: dict[str, pd.DataFrame], d: pd.DataFrame | None = None) -> list[str]:
    if d is None:
        d = backtest_trades(hits, prices)
    if d.empty:
        return []
    L = ["", "## Breakout rule (the live alert rule)", "",
         f"Buy when the price trades above the trigger (the signal candle's high) within "
         f"{bs.entry_window_for('63_30_daily')} sessions ({bs.entry_window_for('Wkly_upswing')} after a weekly signal), "
         f"filled at the trigger or the open on a gap-up. Sell at the next open after a close below the {EXIT_MA}-day average, "
         f"a {STOP_PCT:g}% stop ({', '.join(f'{k} {v:g}%' for k, v in STOP_BY_SCANNER.items())}), or after {RIDE_MAX_HOLD} sessions. "
         f"Wkly_upswing only when daily ATR(14) is under {ATR_MAX_PCT.get('Wkly_upswing', 0):g}% of the close. "
         f"Filter: {', '.join(f'{k} only within {v:g}% of the 52-week high' for k, v in NEAR_HIGH_PCT.items())}. "
         f"{bs.COST_PCT}% costs.", "",
         "| Group | Trades | Win rate | Avg | Avg win / loss | Average / stop / time | Avg days | ₹ on ₹1L a trade |",
         "|---|---|---|---|---|---|---|---|"]
    groups = [(k, g) for k, g in d.groupby("scanner")] + [(f"{k}", g) for k, g in d.groupby("cap") if k] + [("**All**", d)]
    for name, x in groups:
        r = x["ret"]
        L.append(f"| {name} | {len(x)} | {(r > 0).mean():.0%} | {r.mean():+.2f}% | {r[r > 0].mean():+.1f}% / "
                 f"{r[r <= 0].mean():+.1f}% | {(x.status == 'average').mean():.0%} / {(x.status == 'stop').mean():.0%} / "
                 f"{(x.status == 'time').mean():.0%} | {x['days'].mean():.0f} | {r.sum() * 1000:,.0f} |")
    return L


# ------------------------------------------------------- portfolio backtest

PF_CAPITAL = 1_000_000   # ₹10 lakh to start
PF_MAX_POS = 10          # each trade gets 1/10 of the portfolio's value at the time


def portfolio(trades: pd.DataFrame, capital: float = PF_CAPITAL, max_pos: int = PF_MAX_POS) -> dict | None:
    """Trade the alerts with limited money: first come, first served, at most
    max_pos open, one position per stock. Each buy is 1/max_pos of the
    portfolio's value that day (cash + open positions at cost), so profits are
    reinvested. Returns the daily equity curve and the trades taken."""
    if trades.empty:
        return None
    t = trades.sort_values(["entry_date", "scanner", "symbol"]).reset_index(drop=True)
    by_day = {d: g.to_dict("records") for d, g in t.groupby("entry_date")}
    cash, open_, taken, skipped, curve = float(capital), [], [], 0, {}
    for d in pd.bdate_range(t["entry_date"].min(), t["exit_date"].max()):
        still = []
        for x in open_:
            if x["exit_date"] <= d:
                cash += x["amt"] * (1 + x["ret"] / 100)
            else:
                still.append(x)
        open_ = still
        for x in by_day.get(d, []):
            amt = (cash + sum(o["amt"] for o in open_)) / max_pos
            if len(open_) >= max_pos or cash < amt * 0.999 or any(o["symbol"] == x["symbol"] for o in open_):
                skipped += 1
                continue
            x = {**x, "amt": amt}
            cash -= amt
            open_.append(x)
            taken.append(x)
        curve[d] = cash + sum(o["amt"] for o in open_)
    return {"equity": pd.Series(curve), "taken": pd.DataFrame(taken), "skipped": skipped,
            "capital": capital, "max_pos": max_pos}


# ------------------------------------------------- exit rules compared

EXIT_MAX_HOLD = 250  # sessions (~1 year) for the riding exits
EXIT_RULES = {
    "target8": "wait for pullback, +8% target, 8 weeks (older)",
    "trail10": "10% trailing stop",
    "trail15": "15% trailing stop",
    "ma20": "close below 20-day average",
    "ma50": "wait for pullback, close below 50-day average (old)",
    "half8_ma20": "half at +8%, rest on close below 20-day average",
    "lock8_ma20": "after +8%: stop at cost, sell on close below 20-day average",
    "lock8_ma50": "after +8%: stop at cost, sell on close below 50-day average",
    "bo_ma50": "buy at the breakout, close below 50-day average (now)",
}
BO_ALL = "bo_ma50_all"  # breakout buys of every signal, not only those that later dipped


def ride(df: pd.DataFrame, e: int, scanner: str, rule: str, ep: float | None = None) -> dict | None:
    """Exit for a position bought at the open of bar e. Every riding rule keeps
    the fixed starting stop (12%, 15% Wkly_upswing) and exits after
    EXIT_MAX_HOLD sessions. None while the trade would still be open. `ep`
    overrides the buy price (a breakout buy fills at the trigger on bar e)."""
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    n, ep = len(c), float(o[e]) if ep is None else float(ep)
    stop = ep * (1 - stop_for(scanner) / 100)
    ma = None
    if rule.startswith(("ma", "half", "lock")):
        w = 50 if rule.endswith("ma50") else 20
        ma = pd.Series(c).rolling(w, min_periods=w).mean().to_numpy()
    trail = {"trail10": 0.10, "trail15": 0.15}.get(rule)
    half = rule.startswith("half")
    lock = rule.startswith("lock")  # ride only once the trade has worked
    armed = False
    tgt = ep * (1 + TARGET_PCT / 100)
    banked, hi = 0.0, ep  # banked = % already realised on the first half
    last = min(n - 1, e + EXIT_MAX_HOLD)
    for i in range(e, last + 1):
        if i > e and o[i] <= stop:
            return _close(ep, o[i], banked, half and banked != 0.0, "stop", df.index[i], i - e + 1)
        if l[i] <= stop:
            return _close(ep, stop, banked, half and banked != 0.0, "stop", df.index[i], i - e + 1)
        if half and banked == 0.0 and h[i] >= tgt:
            banked = max(float(o[i]), tgt) / ep - 1 if i > e else tgt / ep - 1
        if lock and not armed and h[i] >= tgt:
            armed, stop = True, max(stop, ep)
        if lock and not armed and i - e >= MAX_HOLD:  # never worked: the usual 8-week exit
            return _close(ep, c[i], 0.0, False, "time", df.index[i], i - e + 1)
        hi = max(hi, c[i])
        if trail:
            stop = max(stop, hi * (1 - trail))
        if ma is not None and (armed or not lock) and not np.isnan(ma[i]) and c[i] < ma[i] and i > e:
            if i + 1 > n - 1:
                return None
            return _close(ep, o[i + 1], banked, half and banked != 0.0, "average", df.index[i + 1], i - e + 2)
    if e + EXIT_MAX_HOLD <= n - 1:
        return _close(ep, c[last], banked, half and banked != 0.0, "time", df.index[last], last - e + 1)
    return None


def _close(ep, px, banked, split, why, when, days) -> dict:
    r = float(px) / ep - 1
    if split:
        r = (banked + r) / 2
    return {"ret": round(r * 100 - bs.COST_PCT, 2), "why": why, "exit_date": pd.Timestamp(when), "days": int(days)}


def exit_trades(hits: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Same dip buys as the live rule, sold by each rule in EXIT_RULES, plus
    buying at the breakout itself (no pullback) with the 50-day-average exit."""
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        if not passes_filter(h["scanner_name"], dist_52w_high(df, sig["end_pos"]), atr_pct(df, sig["end_pos"])):
            continue
        sp, trig = sig["end_pos"], sig["trigger"]
        info = {"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                "hit_date": pd.Timestamp(h["hit_date"])}
        # Breakout buy: first session within the entry window trading above the
        # trigger, filled at the trigger (or the open on a gap-up).
        hi, op = df["High"].to_numpy(dtype=float), df["Open"].to_numpy(dtype=float)
        win = range(sp + 1, min(len(df), sp + 1 + bs.entry_window_for(h["scanner_name"])))
        b = next((i for i in win if hi[i] > trig), None)
        bo = None
        if b is not None:
            px = max(op[b], trig)
            x = ride(df, b, h["scanner_name"], "ma50", ep=px)
            if x:
                bo = {**info, "entry_date": df.index[b], "entry": px, **x}
                rows.append({**bo, "rule": BO_ALL})
        base = simulate(df.iloc[sp + 1:], trig, h["scanner_name"])
        if "entry_date" not in base:
            continue
        e = int(df.index.get_loc(base["entry_date"]))
        common = {**info, "entry_date": pd.Timestamp(base["entry_date"])}
        if base["status"] in ("target", "stop", "time"):
            rows.append({**common, "rule": "target8", "ret": base["ret"], "why": base["status"],
                         "exit_date": pd.Timestamp(base["exit_date"]),
                         "days": int(df.index.get_loc(base["exit_date"])) - e + 1})
        for rule in EXIT_RULES:
            if rule in ("target8", "bo_ma50"):
                continue
            x = ride(df, e, h["scanner_name"], rule)
            if x:
                rows.append({**common, "rule": rule, **x})
        if bo:  # the same signal, bought at the breakout instead of the dip
            rows.append({**bo, "rule": "bo_ma50"})
    return pd.DataFrame(rows)


def exits_compare(et: pd.DataFrame, start: pd.Timestamp) -> list[dict]:
    """Per exit rule: trade stats and the ₹10L portfolio, from `start`, using
    only buys every rule has closed (so all rules see the same buys)."""
    if et.empty:
        return []
    et = et[et["entry_date"] >= start]
    if "hit_date" not in et:
        et = et.assign(hit_date=et["entry_date"])
    every = et[et["rule"] == BO_ALL]
    et = et[et["rule"] != BO_ALL]
    key = ["scanner", "symbol", "hit_date"]
    done = et.groupby(key)["rule"].nunique()
    common = done[done == et["rule"].nunique()].index
    et = et.set_index(key).loc[common].reset_index()
    out = []
    labels = {**EXIT_RULES, BO_ALL: "no pullback, every breakout (incl. stocks that never dipped)"}
    for rule, label in labels.items():
        g = every if rule == BO_ALL else et[et["rule"] == rule]
        if g.empty:
            continue
        pf = portfolio(g)
        eq = pf["equity"]
        r = g["ret"]
        out.append({"rule": rule, "label": label, "trades": len(g), "win": round((r > 0).mean() * 100),
                    "avg": round(r.mean(), 2), "avg_win": _rn(r[r > 0].mean()), "avg_loss": _rn(r[r <= 0].mean()),
                    "days": round(g["days"].mean()),
                    "final": round(eq.iloc[-1]), "cagr": round(_cagr(pf["capital"], eq.iloc[-1], eq.index[0], eq.index[-1]), 1),
                    "max_dd": round((eq / eq.cummax() - 1).min() * 100, 1),
                    "by_scanner": {k: {"trades": len(x), "win": round((x["ret"] > 0).mean() * 100), "avg": round(x["ret"].mean(), 2)}
                                   for k, x in g.groupby("scanner")}})
    return out


def _rn(x) -> float | None:
    return None if x is None or pd.isna(x) else round(float(x), 1)


def _cagr(first: float, last: float, start, end) -> float:
    yrs = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    return ((last / first) ** (1 / yrs) - 1) * 100 if yrs > 0 and first > 0 else float("nan")


def performance(trades: pd.DataFrame, bench: pd.Series | None, exits: pd.DataFrame | None = None) -> dict | None:
    """Would buying on the alerts have made money? Per-trade stats per
    scanner, plus a ₹10L portfolio from the date all three scanners have
    backtest data, compared with the Nifty 500 over the same days."""
    if trades.empty:
        return None
    start = trades.groupby("scanner")["entry_date"].min().max()  # all scanners live from here
    t = trades[trades["entry_date"] >= start]
    per = []
    for name, g in [*t.groupby("scanner"), ("All", t)]:
        r = g["ret"]
        per.append({"group": name, "trades": len(g), "win": round((r > 0).mean() * 100),
                    "avg": round(r.mean(), 2), "avg_win": _rn(r[r > 0].mean()),
                    "avg_loss": _rn(r[r <= 0].mean()), "days": round(g["days"].mean())})
    pf = portfolio(t)
    eq = pf["equity"]
    yearly = eq.resample("YE").last()
    prev = yearly.shift(1).fillna(pf["capital"])
    out = {"start": start.date().isoformat(), "end": eq.index[-1].date().isoformat(), "per_scanner": per,
           "portfolio": {"capital": pf["capital"], "max_pos": pf["max_pos"],
                         "final": round(eq.iloc[-1]), "profit": round(eq.iloc[-1] - pf["capital"]),
                         "cagr": round(_cagr(pf["capital"], eq.iloc[-1], eq.index[0], eq.index[-1]), 1),
                         "max_dd": round((eq / eq.cummax() - 1).min() * 100, 1),
                         "taken": len(pf["taken"]), "skipped": pf["skipped"],
                         "win": round((pf["taken"]["ret"] > 0).mean() * 100)},
           "years": [{"year": int(d.year), "ret": round((v / p - 1) * 100, 1)} for d, v, p in zip(yearly.index, yearly, prev)],
           "monthly": [{"m": d.strftime("%Y-%m"), "v": round(v)} for d, v in eq.resample("ME").last().items()]}
    if exits is not None and not exits.empty:
        out["exits"] = exits_compare(exits, start)
    if bench is not None:
        b = bench[(bench.index >= eq.index[0]) & (bench.index <= eq.index[-1])].dropna()
        if len(b) > 1:
            by = b.resample("YE").last()
            bprev = by.shift(1).fillna(b.iloc[0])
            out["bench"] = {"name": "Nifty 500", "cagr": round(_cagr(b.iloc[0], b.iloc[-1], b.index[0], b.index[-1]), 1),
                            "max_dd": round((b / b.cummax() - 1).min() * 100, 1),
                            "final": round(pf["capital"] * b.iloc[-1] / b.iloc[0])}
            bmap = {int(d.year): round((v / p - 1) * 100, 1) for d, v, p in zip(by.index, by, bprev)}
            for y in out["years"]:
                y["bench"] = bmap.get(y["year"])
            bm = (b / b.iloc[0] * pf["capital"]).resample("ME").last()
            for m in out["monthly"]:
                v = bm.get(pd.Timestamp(m["m"]) + pd.offsets.MonthEnd(0))
                m["b"] = None if v is None or pd.isna(v) else round(v)
    return out


def _pctx(v) -> str:
    return "–" if v is None else f"{v:+.1f}%"


def performance_section(perf: dict | None) -> list[str]:
    if not perf:
        return []
    p, b = perf["portfolio"], perf.get("bench")
    L = ["", "## If I had bought on the alerts", "",
         f"Every buy alert from {perf['start']} (when all three scanners have backtest data) to {perf['end']}, "
         f"starting with ₹{p['capital'] / 1e5:g}L: each buy is 1/{p['max_pos']} of the portfolio's value at the time (profits reinvested), "
         f"at most {p['max_pos']} open, first come first served, one position per stock, after costs.", "",
         "| Scanner | Trades | Win rate | Avg | Avg win / loss | Avg days |", "|---|---|---|---|---|---|"]
    for r in perf["per_scanner"]:
        L.append(f"| {r['group']} | {r['trades']} | {r['win']}% | {r['avg']:+.2f}% | {_pctx(r['avg_win'])} / {_pctx(r['avg_loss'])} | {r['days']} |")
    L += ["", "| | Alerts portfolio | " + (b["name"] if b else "Index") + " |", "|---|---|---|",
          f"| ₹{p['capital'] / 1e5:g}L became | ₹{p['final'] / 1e5:.1f}L | " + (f"₹{b['final'] / 1e5:.1f}L" if b else "–") + " |",
          f"| Yearly growth (CAGR) | {p['cagr']:.1f}% | " + (f"{b['cagr']:.1f}%" if b else "–") + " |",
          f"| Worst fall from a peak | {p['max_dd']:.1f}% | " + (f"{b['max_dd']:.1f}%" if b else "–") + " |",
          f"| Trades taken / skipped (no free slot) | {p['taken']} / {p['skipped']} | |",
          f"| Win rate of trades taken | {p['win']}% | |", "",
          "| Year | Alerts portfolio | " + (b["name"] if b else "Index") + " |", "|---|---|---|"]
    for y in perf["years"]:
        L.append(f"| {y['year']} | {y['ret']:+.1f}% | " + (f"{y['bench']:+.1f}%" if y.get("bench") is not None else "–") + " |")
    L += ["", "Open positions are counted at cost until sold. The current year is year-to-date."]
    if perf.get("exits"):
        L += ["", "### Exit rules compared (same dip buys)", "",
              "Every rule keeps the starting stop (12%, 15% for Wkly_upswing); the riding rules sell after a year at the latest. "
              "Only buys that every rule has closed are counted.", "",
              "| Exit | Trades | Win rate | Avg | Avg win / loss | Avg days | ₹10L became | Per year | Worst fall |",
              "|---|---|---|---|---|---|---|---|---|"]
        for x in perf["exits"]:
            L.append(f"| {x['label']} | {x['trades']} | {x['win']}% | {x['avg']:+.2f}% | {_pctx(x['avg_win'])} / {_pctx(x['avg_loss'])} | "
                     f"{x['days']} | ₹{x['final'] / 1e5:.1f}L | {x['cagr']:.1f}% | {x['max_dd']:.1f}% |")
        L += ["", "| Exit | " + " | ".join(sorted(perf["exits"][0]["by_scanner"])) + " |",
              "|---|" + "---|" * len(perf["exits"][0]["by_scanner"])]
        for x in perf["exits"]:
            L.append(f"| {x['label']} | " + " | ".join(f"{v['win']}% · {v['avg']:+.2f}%" for _, v in sorted(x["by_scanner"].items())) + " |")
    return L
