"""Live rule: buy at the breakout above the trigger, ride the trend.

For every signal (the scanner's trigger = the signal candle's high, the
week's high for Wkly_upswing):
1. buy-stop : from the next session, buy when the price trades above the
              trigger, within 3 sessions (5 after a weekly signal). Filled at
              the trigger, or at the open on a gap-up.
2. exit     : sell at the next open after a close below the 30-day EMA,
              a 15% stop below the buy price, or after 250
              sessions (~1 year).
Backtest 2021-26, same signals: +5.8% a trade and 46% wins vs +4.2% / 41%
for waiting for a pullback, worst portfolio fall -10% vs -18%.
Filters: Wkly_upswing only when daily ATR(14) < 4% of the close;
63_30_daily only within 10% of the 52-week high. Signals another scanner
also flagged in the 10 days before are tagged "confirmed".

When more buys than free slots: the ML ranker's order once it has passed its
walk-forward test (ranker.py), else mid caps, then large, then small.
Decisions use completed daily candles only.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

import breakout_sim as bs
import db
from slot_gate import IST

# 13 Nov 2026: exit on a close below the 30-day EMA (was the 50-day simple
# average) and a 15% stop for every scanner (was 12%, 15% weekly). Backtest
# 2019-26 (performance.json): 26.6% a year, worst fall -9.2%, vs 24.0% and
# -14.1% before; better in both 2019-22 and 2023-26. The 3/5-session
# buy-stop and the weekly volatility filter stay: longer windows (25.9%) and
# no filter (25.2%) both did worse.
STOP_PCT = 15.0
STOP_BY_SCANNER: dict[str, float] = {}
ATR_MAX_PCT = {"Wkly_upswing": 4.0}       # daily ATR(14) under 4% of the close
EXIT_MA = 30          # live exit: sell at the next open after a close below this daily EMA
EXIT_LABEL = f"{EXIT_MA}-day EMA"
RIDE_MAX_HOLD = 250   # sessions (~1 year) before a riding position is sold anyway
CLOSED = ("target", "stop", "time", "average")
NEAR_HIGH_PCT = {"63_30_daily": 10.0}  # only take signals within this % of the 52-week high
CONFIRM_DAYS = 10     # another scanner within this many days before = confirmed
HISTORY_DAYS = 400    # calendar days of prices needed for the 52-week high
START = "2026-09-25"  # live signals from this date are tracked
ALERT_DAYS = 4        # only alert on events this recent (no flood on the first run)
STAKE = 100_000
MARKET_CLOSE = (15, 30)
ACTIVE = {"waiting for breakout", "holding"}
# When more signals than free slots: mid caps first, then large, then small.
# Backtest 2021-26 (10 slots, 12 shuffles): 17.4% a year vs 14.3% first come,
# better in both 2021-23 (22.1% vs 17.3%) and 2024-26 (10.8% vs 7.1%), worst
# fall -11.8% vs -13.0%. "Two scanners first" helped 2021-23 but hurt 2024-26.
CAP_PRIORITY = {"Midcap": 0, "Largecap": 1, "Smallcap": 2}
CHOICE = {0: "1st choice", 1: "2nd choice", 2: "3rd choice"}


def priority(cap: str | None) -> int:
    return CAP_PRIORITY.get(cap or "", 3)


_RANKER: dict | None = None


def _ranker() -> dict | None:
    """The ML ranker (data/model/ranker.json), loaded once."""
    global _RANKER
    if _RANKER is None:
        import ranker
        _RANKER = ranker.load() or {}
    return _RANKER or None


def slot_order(s: dict) -> tuple:
    """Sort key when more buys than free slots: highest ML rank first when the
    ranker is switched on (passed its walk-forward test), else mid, large, small."""
    m = _ranker()
    ml = s.get("ml")
    if m and m.get("on") and ml is not None:
        return (0, -ml)
    return (1, s.get("priority", 3))


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


def exit_line(close: pd.Series) -> np.ndarray:
    """The live exit line: EXIT_MA-day exponential average of the close."""
    return close.ewm(span=EXIT_MA, adjust=False, min_periods=EXIT_MA).mean().to_numpy()


def exit_ma(df: pd.DataFrame, start: int) -> np.ndarray:
    """The exit line from bar `start` on (aligned to df.iloc[start:])."""
    return exit_line(df["Close"])[start:]


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
    import live_signals as paper
    import track_record
    now = now or datetime.now(IST)
    lookback = (date.fromisoformat(START) - timedelta(days=HISTORY_DAYS)).isoformat()
    confirm_from = (date.fromisoformat(START) - timedelta(days=CONFIRM_DAYS)).isoformat()
    seen: dict[str, list[tuple[pd.Timestamp, str]]] = {}
    for d0, sc0, sym0, _ in paper._signals(conn, confirm_from):
        seen.setdefault(sym0, []).append((pd.Timestamp(d0), sc0))
    nifty = paper._frame(conn, "^NSEI", lookback)
    model = _ranker()
    out = []
    # One open buy-stop per scanner + stock. Holdings don't block a new signal
    # here: apply_slots() decides (one position per stock, 15 slots), as in the
    # backtest, so a stock that got no slot can be bought on a later signal.
    active: set[tuple[str, str]] = set()
    for day, scanner, symbol, source in paper._signals(conn, START):
        t = pd.Timestamp(day)
        if (scanner, symbol) in active:
            out.append({"scanner": scanner, "symbol": symbol, "date": day, "source": source,
                        "status": "duplicate", "why": "a buy-stop from an earlier signal is still open"})
            continue
        others = sorted({sc for d0, sc in seen.get(symbol, [])
                         if sc != scanner and t - pd.Timedelta(days=CONFIRM_DAYS) <= d0 <= t})
        df = _completed(paper._frame(conn, symbol, lookback), now)
        hit = pd.Timestamp(day)
        if not bs.is_weekly(scanner) and not df.empty and hit not in df.index and df.index[-1] > hit:
            earlier = df.index[df.index <= hit]
            hit = earlier[-1] if len(earlier) else hit
        sig = bs.signal_bar(df, hit, bs.is_weekly(scanner)) if not df.empty else None
        cap = track_record.tier_of(conn, symbol)
        base = {"scanner": scanner, "symbol": symbol, "date": day, "source": source, "confirmed_by": others,
                "cap": cap, "priority": priority(cap)}
        if sig is None:
            out.append({**base, "status": "no prices yet"})
            continue
        if model:
            import ranker
            base["ml"] = ranker.rank(model, scanner, cap, ranker.signal_features(df, sig, nifty if not nifty.empty else None))
        base["dist_52w_high"] = dist_52w_high(df, sig["end_pos"])
        base["atr_pct"] = atr_pct(df, sig["end_pos"])
        if not passes_filter(scanner, base["dist_52w_high"], base["atr_pct"]):
            out.append({**base, "status": "skipped", "trigger": sig["trigger"],
                        "why": skip_reason(scanner, base["dist_52w_high"], base["atr_pct"])})
            continue
        st = live_sim(df, sig, scanner)
        if st["status"] == "waiting for breakout":
            st["valid_until"] = df.index[sig["end_pos"]] + pd.offsets.BDay(bs.entry_window_for(scanner))
        if st["status"] == "waiting for breakout":
            active.add((scanner, symbol))
        if "entry_date" in st:
            st["path"] = trade_path(df, sig["end_pos"], st.get("exit_date"))
        out.append({**base, **st, "last_close": float(df["Close"].iloc[-1]), "last_date": df.index[-1]})
    return apply_slots(out)


def trade_path(df: pd.DataFrame, signal_pos: int, exit_date=None, before: int = 10, after: int = 3) -> dict:
    """Closes and the exit line around a trade, for the journal's mini chart."""
    end = len(df) if exit_date is None else min(len(df), int(df.index.searchsorted(pd.Timestamp(exit_date))) + 1 + after)
    a = max(0, signal_pos - before)
    ema = exit_line(df["Close"])[a:end]
    return {"d": [x.date().isoformat() for x in df.index[a:end]],
            "c": [round(float(x), 2) for x in df["Close"].iloc[a:end]],
            "e": [None if np.isnan(x) else round(float(x), 2) for x in ema]}


def apply_slots(states: list[dict], slots: int | None = None) -> list[dict]:
    """Trade the paper portfolio like the backtest: at most PF_MAX_POS open
    positions, one per stock, and on a day with more buys than free slots,
    mid caps first, then large, then small. Buys that don't fit become
    'no slot' (the buy-stop alert still went out; the paper book skips it).
    Same-day order: slot_order (ML rank when switched on, else market cap)."""
    slots = slots or PF_MAX_POS
    bought = sorted((s for s in states if "entry_date" in s),
                    key=lambda s: (pd.Timestamp(s["entry_date"]), slot_order(s), s["date"]))
    open_: list[dict] = []
    for s in bought:
        d = pd.Timestamp(s["entry_date"])
        open_ = [o for o in open_ if o.get("status") not in CLOSED or pd.Timestamp(o["exit_date"]) > d]
        if any(o["symbol"] == s["symbol"] for o in open_):
            why = "already holding this stock"
        elif len(open_) >= slots:
            why = f"all {slots} slots were full"
        else:
            open_.append(s)
            continue
        for k in ("entry_date", "entry", "stop", "target", "exit_date", "exit", "ret", "now", "ma",
                  "sell_signal", "sessions_left", "signal_date", "gap", "path"):
            s.pop(k, None)
        s["status"], s["why"] = "no slot", why
    return states


def live_sim(df: pd.DataFrame, sig: dict, scanner: str) -> dict:
    """The live rule for one signal, on the full price frame."""
    fwd, ma = df.iloc[sig["end_pos"] + 1:], exit_ma(df, sig["end_pos"] + 1)
    return simulate_breakout(fwd, sig["trigger"], scanner, ma)


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
    held = {s["symbol"] for s in states if s.get("status") == "holding"}
    for s in states:
        if s.get("status") == "waiting for breakout" and s["symbol"] not in held:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|setup", s, "setup"))
        if "entry_date" in s and s["entry_date"] >= since:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|bought", s, "bought"))
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


SHORT = {"63_30_daily": "63/30", "Bullish_Scanner": "Bullish", "Wkly_upswing": "Weekly"}


def format_alerts(fresh: list[tuple[str, dict, str]]) -> str | None:
    """Today's actions as a short list: what to do, at what price."""
    if not fresh:
        return None
    sc = lambda s: SHORT.get(s["scanner"], s["scanner"])  # noqa: E731
    lines = ["📋 <b>Today's actions</b>"]
    setups = sorted((s for _, s, k in fresh if k == "setup"), key=slot_order)
    if setups:
        lines += ["", "<b>Place buy-stop</b>"]
        for s in setups:
            stp = s["trigger"] * (1 - stop_for(s["scanner"]) / 100)
            ml = f" · ML {s['ml']}" if s.get("ml") is not None else ""
            lines.append(f"🟡 <b>{s['symbol']}</b> above {s['trigger']:.2f} · SL {stp:.2f} · signal {_d(s['date'])} · {sc(s)}{ml}")
    bought = [s for _, s, k in fresh if k == "bought"]
    if bought:
        lines += ["", "<b>Bought</b>"]
        for s in bought:
            lines.append(f"🟢 <b>{s['symbol']}</b> {s['entry']:.2f} on {_d(s['entry_date'])} · SL {s['stop']:.2f} · {sc(s)}")
    sells = [s for _, s, k in fresh if k == "sell"]
    if sells:
        lines += ["", "<b>Sell at next open</b>"]
        for s in sells:
            lines.append(f"🔻 <b>{s['symbol']}</b> closed {s['now']:.2f} < {EXIT_LABEL} {s['ma']:.2f} · {s['ret']:+.1f}%")
    icon = {"target": "✅", "stop": "🛑", "time": "⏱", "average": "📉"}
    why = {"target": "target", "stop": "stop-loss", "time": "1 year", "average": f"below {EXIT_LABEL}"}
    exits = [(s, k) for _, s, k in fresh if k in icon]
    if exits:
        lines += ["", "<b>Closed</b>"]
        for s, k in exits:
            lines.append(f"{icon[k]} <b>{s['symbol']}</b> {s['entry']:.2f} → {s['exit']:.2f} ({s['ret']:+.1f}%) · {why[k]}")
    lines += ["", "<i>Paper trades, not advice · /help for more</i>"]
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
                    "watching": sum(x.get("status") == "waiting for breakout" for x in xs),
                    "holding": len(hold), "closed": len(closed),
                    "win": round(100 * np.mean([r > 0 for r in rets])) if rets else None,
                    "pnl": int(sum(r / 100 * STAKE for r in rets)),
                    "open_pnl": int(sum(x["ret"] / 100 * STAKE for x in hold))})
    return {"start": START, "rows": out}


def format_summary(book: dict) -> str:
    lines = [f"🎯 <b>Paper book</b> (since {book['start']}, ₹1L a trade)", "<pre>",
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


def _public_fund(f: dict | None) -> dict | None:
    """For the public website: when the figures come from a Screener company
    page, keep the verdicts and which conditions fail, drop the numbers
    (Screener allows personal viewing only). Telegram, which is private, gets them."""
    if not f or not f.get("private"):
        return f
    sc = dict(f["screen"], fails=[c + " fails" for c in f["screen"].get("fail_labels", [])])
    return {**f, "screen": sc, "pe": None, "roce": None, "promoter": None}


def dashboard_view(states: list[dict]) -> dict:
    """JSON for site/data.json: buy list, holdings, sold trades (with price paths)."""
    import fundamentals
    buy_list, holding, closed = [], [], []
    for s in states:
        base = {"scanner": s["scanner"], "symbol": s["symbol"], "signal": s["date"],
                "confirmed_by": s.get("confirmed_by", []), "off_high": s.get("dist_52w_high"),
                "fund": _public_fund(fundamentals.check(s["symbol"])),
                "trigger": _r(s.get("trigger")), "now": _r(s.get("last_close")), "now_date": _iso(s.get("last_date")),
                "cap": s.get("cap"), "priority": s.get("priority", 3), "ml": s.get("ml")}
        st = s.get("status")
        if st == "waiting for breakout":
            buy_list.append({**base, "stage": "breakout", "level": _r(s["trigger"]),
                             "stop": _r(s["trigger"] * (1 - stop_for(s["scanner"]) / 100)),
                             "valid_until": _iso(s.get("valid_until"))})
        if "entry_date" in s:
            trade = {**base, "entry_date": _iso(s["entry_date"]), "entry": _r(s["entry"]),
                     "target": _r(s.get("target")), "stop": _r(s["stop"]), "ma": _r(s.get("ma")),
                     "sell_signal": _iso(s.get("sell_signal")), "gap": s.get("gap"), "path": s.get("path"),
                     "status": st, "exit_date": _iso(s.get("exit_date")), "exit": _r(s.get("exit")), "exit_by": _iso(
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
    # Recent scanner signals the rule didn't take (no free slot, filter), latest per stock,
    # so the Today page covers everything on the scanners without a separate list.
    active = {x["symbol"] for x in buy_list + holding}
    recent = pd.Timestamp(date.today()) - pd.Timedelta(days=7)
    passed: dict[str, dict] = {}
    for s in states:
        if s.get("status") in ("no slot", "skipped") and pd.Timestamp(s["date"]) >= recent and s["symbol"] not in active:
            key = f'{s["scanner"]}|{s["symbol"]}'
            prev = passed.get(key)
            if prev is None or _iso(s["date"]) >= prev["signal"]:
                passed[key] = {"symbol": s["symbol"], "scanner": s["scanner"], "signal": _iso(s["date"]),
                                       "why": "no free slot" if s["status"] == "no slot" else s.get("why", "filtered out")}
    held = {x["symbol"] for x in holding}
    seen_bl: set[str] = set()
    keep = []
    for x in sorted(buy_list, key=lambda x: x["signal"], reverse=True):  # newest buy-stop per stock
        if x["symbol"] in held or x["symbol"] in seen_bl:
            continue
        seen_bl.add(x["symbol"])
        keep.append(x)
    buy_list = keep
    buy_list.sort(key=lambda x: (slot_order(x), x["signal"]))
    holding.sort(key=lambda x: x["entry_date"], reverse=True)
    closed.sort(key=lambda x: x["exit_date"], reverse=True)
    skipped = sum(s.get("status") == "skipped" for s in states)
    return {"rule": {"mode": "breakout", "entry_days": bs.entry_window_for("63_30_daily"),
                     "entry_days_weekly": bs.entry_window_for("Wkly_upswing"), "target": None, "exit_ma": EXIT_MA,
                     "ml_on": bool(_ranker() and _ranker().get("on")),
                     "stop": STOP_PCT, "stop_by": STOP_BY_SCANNER, "atr_max": ATR_MAX_PCT, "max_hold": RIDE_MAX_HOLD, "stake": STAKE,
                     "near_high": NEAR_HIGH_PCT},
            "skipped": skipped,
            "fund_asof": fundamentals.scores().get("_asof"),
            "summary": summary(states), "buy_list": buy_list, "holding": holding,
            "closed": closed, "passed": sorted(passed.values(), key=lambda x: x["signal"], reverse=True),
            # signals whose candle isn't complete yet (today's, or this week's for weekly)
            "pending": [{"symbol": s["symbol"], "scanner": s["scanner"], "signal": _iso(s["date"])}
                        for s in states if s.get("status") == "no prices yet"]}


# ------------------------------------------------------------ backtest report

def backtest_trades(hits: pd.DataFrame, prices: dict[str, pd.DataFrame], nifty: pd.DataFrame | None = None,
                    features: bool = False) -> pd.DataFrame:
    """Every closed backtest trade under the live rule (filters applied); with
    `features`, also the ML ranker's facts at the signal close."""
    import ranker
    ind: dict[str, pd.DataFrame] = {}
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
            f = {}
            if features:
                if h["symbol"] not in ind:
                    ind[h["symbol"]] = bs.indicator_frame(df)
                f = ranker.signal_features(df, sig, nifty, ind[h["symbol"]])
            rows.append({"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                         "hit_date": pd.Timestamp(h["hit_date"]), **f,
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
         f"filled at the trigger or the open on a gap-up. Sell at the next open after a close below the {EXIT_LABEL}, "
         f"a {STOP_PCT:g}% stop" + (f" ({', '.join(f'{k} {v:g}%' for k, v in STOP_BY_SCANNER.items())})" if STOP_BY_SCANNER else "")
         + f", or after {RIDE_MAX_HOLD} sessions. "
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
PF_MAX_POS = 15          # each trade gets 1/15 of the portfolio's value at the time
# Backtest 2021-26 (breakout rule, mid caps first, 8 shuffles): 15 slots 23.0% a year
# vs 17.0% with 10 (2021-23: 27.6% vs 22.7%; 2024-26: 10.9% vs 9.0%), worst fall
# about the same (-11%). 20 slots 21.6%, 30 slots 18.8% (too thin). Ranking by
# signal-day volume was tested and dropped: it helped 2021-23 but not 2024-26.


def portfolio(trades: pd.DataFrame, capital: float = PF_CAPITAL, max_pos: int = PF_MAX_POS) -> dict | None:
    """Trade the alerts with limited money: first come, first served (on the
    same day by the `ml` column when given, else mid caps first, then large,
    then small: CAP_PRIORITY), at most
    max_pos open, one position per stock. Each buy is 1/max_pos of the
    portfolio's value that day (cash + open positions at cost), so profits are
    reinvested. Returns the daily equity curve and the trades taken."""
    if trades.empty:
        return None
    capp = trades["cap"].map(CAP_PRIORITY).fillna(3) if "cap" in trades else pd.Series(3, index=trades.index)
    if "ml" in trades:  # ML score (higher first) where there is one, else market cap
        has = trades["ml"].notna()
        t = trades.assign(_g=np.where(has, 0, 1), _p=np.where(has, -trades["ml"].fillna(0), capp))
    else:
        t = trades.assign(_g=1, _p=capp)
    t = t.sort_values(["entry_date", "_g", "_p", "scanner", "symbol"]).reset_index(drop=True)
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


def _rn(x) -> float | None:
    return None if x is None or pd.isna(x) else round(float(x), 1)


def _cagr(first: float, last: float, start, end) -> float:
    yrs = (pd.Timestamp(end) - pd.Timestamp(start)).days / 365.25
    return ((last / first) ** (1 / yrs) - 1) * 100 if yrs > 0 and first > 0 else float("nan")


def performance(trades: pd.DataFrame, bench: pd.Series | None) -> dict | None:
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
    return L
