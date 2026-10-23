"""Buy-the-dip rule: wait for the pullback after a breakout, buy it, take +8%.

For every signal (the scanner's trigger = the signal candle's high):
1. breakout : price crosses above the trigger within 3 sessions (5 after a
              weekly signal)
2. buy zone : within 20 sessions of the breakout, a daily close at least
              DIP% below the highest close since the breakout, while the close
              is still no more than 5% below the trigger -> buy at the next open
3. exit     : +8% target, 12% stop below the buy price, or the close after
              40 sessions (8 weeks), whichever comes first
Wkly_upswing: only when daily ATR(14) < 4% of the close, with a 15% stop.
Filters: 63_30_daily signals are only taken when the signal-day close is
within 10% of the 52-week high (NEAR_HIGH_PCT; backtest 2024-26: 72% wins
vs 66%). Signals another scanner also flagged in the 10 days before are
tagged "confirmed" (78% wins in 2024-26).

Used live by run.py (Telegram alerts on every scan) and in the weekly
backtest report (stock_outcomes.py). Decisions use completed daily candles
only, so a buy-zone alert in the morning means "buy at today's open".
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
MAX_HOLD = 40         # sessions (8 weeks)
NEAR_HIGH_PCT = {"63_30_daily": 10.0}  # only take signals within this % of the 52-week high
CONFIRM_DAYS = 10     # another scanner within this many days before = confirmed
HISTORY_DAYS = 400    # calendar days of prices needed for the 52-week high
START = "2026-09-25"  # live signals from this date are tracked
ALERT_DAYS = 4        # only alert on events this recent (no flood on the first run)
STAKE = 100_000
MARKET_CLOSE = (15, 30)
ACTIVE = {"waiting for breakout", "watching for dip", "buy zone", "holding"}


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


def simulate(fwd: pd.DataFrame, trigger: float, scanner: str) -> dict:
    """Run the rule over the daily bars after the signal bar."""
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
        st = simulate(df.iloc[sig["end_pos"] + 1:], sig["trigger"], scanner)
        if st["status"] in ACTIVE:
            active.add((scanner, symbol))
        out.append({**base, **st, "last_close": float(df["Close"].iloc[-1]), "last_date": df.index[-1]})
    return out


def _d(x) -> str:
    return pd.Timestamp(x).strftime("%d %b")


def _exit_by(s: dict) -> str:
    return _d(pd.Timestamp(s["entry_date"]) + pd.offsets.BDay(MAX_HOLD)) if "entry_date" in s else "–"


def events(states: list[dict], now: datetime) -> list[tuple[str, dict, str]]:
    """(key, state, kind) for buy-zone / exit events dated in the last ALERT_DAYS."""
    since = pd.Timestamp(now.date()) - pd.Timedelta(days=ALERT_DAYS)
    ev = []
    for s in states:
        if "dip_date" in s and s["dip_date"] >= since:
            ev.append((f"{s['scanner']}|{s['symbol']}|{s['date']}|buy", s, "buy"))
        if s.get("status") in ("target", "stop", "time") and s["exit_date"] >= since:
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
    lines = ["🎯 <b>Buy-the-dip alerts</b>"]
    buys = [s for _, s, k in fresh if k == "buy"]
    if buys:
        lines += ["", "<b>BUY ZONE</b> (buy at the next open):"]
        for s in buys:
            ref = s.get("entry", s["dip_close"])
            lines.append(f"🟢 <b>{s['symbol']}</b> ({s['scanner']}){_tags(s)} dipped {s['dip_pct']:g}% to {s['dip_close']:.2f} "
                         f"(trigger {s['trigger']:.2f}). Buy ~{ref:.2f}, target {ref * (1 + TARGET_PCT / 100):.2f} "
                         f"(+{TARGET_PCT:g}%), stop {ref * (1 - stop_for(s['scanner']) / 100):.2f} (-{stop_for(s['scanner']):g}%), "
                         f"exit by {_exit_by(s) if 'entry_date' in s else 'day 40'}")
    icon = {"target": "✅", "stop": "🛑", "time": "⏱"}
    label = {"target": "target hit", "stop": "stopped", "time": "8 weeks up, sold"}
    exits = [(s, k) for _, s, k in fresh if k != "buy"]
    if exits:
        lines += ["", "<b>CLOSED</b>:"]
        for s, k in exits:
            lines.append(f"{icon[k]} <b>{s['symbol']}</b> ({s['scanner']}) {label[k]} {_d(s['exit_date'])}: "
                         f"{s['entry']:.2f} → {s['exit']:.2f} ({s['ret']:+.1f}%)")
    lines += ["", f"<i>Rule: after the breakout, buy a {DIP_PCT['63_30_daily']:g}% dip "
                  f"({DIP_PCT['Wkly_upswing']:g}% for Wkly_upswing) that stays within {FLOOR_PCT:g}% of the trigger; "
                  f"+{TARGET_PCT:g}% target, -{STOP_PCT:g}% stop (-{STOP_BY_SCANNER.get('Wkly_upswing', STOP_PCT):g}% weekly), "
                  f"out after 8 weeks. Backtest, not advice.</i>"]
    return "\n".join(lines)


def summary(states: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {"All scanners": states}
    for s in states:
        groups.setdefault(s["scanner"], []).append(s)
    out = []
    for g, xs in groups.items():
        closed = [x for x in xs if x.get("status") in ("target", "stop", "time")]
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
    buy_list, holding, activity = [], [], []
    cutoff = pd.Timestamp(date.today()) - pd.Timedelta(days=activity_days)
    for s in states:
        base = {"scanner": s["scanner"], "symbol": s["symbol"], "signal": s["date"],
                "confirmed_by": s.get("confirmed_by", []), "off_high": s.get("dist_52w_high"),
                "trigger": _r(s.get("trigger")), "now": _r(s.get("last_close")), "now_date": _iso(s.get("last_date"))}
        st = s.get("status")
        if st == "waiting for breakout":
            buy_list.append({**base, "stage": "breakout", "level": _r(s["trigger"])})
        elif st == "watching for dip":
            buy_list.append({**base, "stage": "dip", "level": s["buy_below"], "high_close": _r(s["high_close"]),
                             "floor": _r(s["trigger"] * (1 - FLOOR_PCT / 100)), "dip_pct": s["dip_pct"],
                             "breakout": _iso(s["breakout_date"])})
        elif st == "buy zone":
            ref = s["dip_close"]
            buy_list.append({**base, "stage": "zone", "level": _r(ref), "dip_pct": s["dip_pct"],
                             "target": _r(ref * (1 + TARGET_PCT / 100)), "stop": _r(ref * (1 - stop_for(s["scanner"]) / 100))})
        if "entry_date" in s:
            trade = {**base, "entry_date": _iso(s["entry_date"]), "entry": _r(s["entry"]),
                     "target": _r(s["target"]), "stop": _r(s["stop"]), "exit_by": _iso(
                         pd.Timestamp(s["entry_date"]) + pd.offsets.BDay(MAX_HOLD)), "ret": s.get("ret")}
            if st == "holding":
                holding.append({**trade, "pnl": int(s["ret"] / 100 * STAKE)})
            if pd.Timestamp(s["entry_date"]) >= cutoff:
                activity.append({**trade, "side": "BUY", "when": trade["entry_date"], "price": trade["entry"]})
            if st in ("target", "stop", "time") and pd.Timestamp(s["exit_date"]) >= cutoff:
                activity.append({**trade, "side": "SELL", "when": _iso(s["exit_date"]), "price": _r(s["exit"]),
                                 "reason": st, "pnl": int(s["ret"] / 100 * STAKE)})
    order = {"zone": 0, "dip": 1, "breakout": 2}
    buy_list.sort(key=lambda x: (order[x["stage"]], x["signal"]), reverse=False)
    holding.sort(key=lambda x: x["entry_date"], reverse=True)
    activity.sort(key=lambda x: (x["when"], x["side"] == "SELL"), reverse=True)
    skipped = sum(s.get("status") == "skipped" for s in states)
    return {"rule": {"dip": DIP_PCT, "floor": FLOOR_PCT, "zone_days": ZONE_DAYS, "target": TARGET_PCT,
                     "stop": STOP_PCT, "stop_by": STOP_BY_SCANNER, "atr_max": ATR_MAX_PCT, "max_hold": MAX_HOLD, "stake": STAKE,
                     "near_high": NEAR_HIGH_PCT},
            "skipped": skipped,
            "summary": summary(states), "buy_list": buy_list, "holding": holding, "activity": activity}


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
        s = simulate(df.iloc[sig["end_pos"] + 1:], sig["trigger"], h["scanner_name"])
        if s["status"] in ("target", "stop", "time"):
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
    L = ["", "## Buy-the-dip rule (the live alert rule)", "",
         f"After the breakout, buy at the next open once a close is {DIP_PCT['63_30_daily']:g}% below the highest close "
         f"since the breakout ({DIP_PCT['Wkly_upswing']:g}% for Wkly_upswing), within {ZONE_DAYS} sessions and no more than "
         f"{FLOOR_PCT:g}% below the trigger. Exit at +{TARGET_PCT:g}%, a {STOP_PCT:g}% stop "
         f"({', '.join(f'{k} {v:g}%' for k, v in STOP_BY_SCANNER.items())}), or after {MAX_HOLD} sessions. "
         f"Wkly_upswing only when daily ATR(14) is under {ATR_MAX_PCT.get('Wkly_upswing', 0):g}% of the close. "
         f"Filter: {', '.join(f'{k} only within {v:g}% of the 52-week high' for k, v in NEAR_HIGH_PCT.items())}. "
         f"{bs.COST_PCT}% costs.", "",
         "| Group | Trades | Win rate | Avg | Avg win / loss | Target / stop / time | Avg days | ₹ on ₹1L a trade |",
         "|---|---|---|---|---|---|---|---|"]
    groups = [(k, g) for k, g in d.groupby("scanner")] + [(f"{k}", g) for k, g in d.groupby("cap") if k] + [("**All**", d)]
    for name, x in groups:
        r = x["ret"]
        L.append(f"| {name} | {len(x)} | {(r > 0).mean():.0%} | {r.mean():+.2f}% | {r[r > 0].mean():+.1f}% / "
                 f"{r[r <= 0].mean():+.1f}% | {(x.status == 'target').mean():.0%} / {(x.status == 'stop').mean():.0%} / "
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
    "target8": "+8% target, 12% stop, 8 weeks (now)",
    "trail10": "10% trailing stop",
    "trail15": "15% trailing stop",
    "ma20": "close below 20-day average",
    "ma50": "close below 50-day average",
    "half8_ma20": "half at +8%, rest on close below 20-day average",
    "lock8_ma20": "after +8%: stop at cost, sell on close below 20-day average",
    "lock8_ma50": "after +8%: stop at cost, sell on close below 50-day average",
}


def ride(df: pd.DataFrame, e: int, scanner: str, rule: str) -> dict | None:
    """Exit for a position bought at the open of bar e. Every riding rule keeps
    the fixed starting stop (12%, 15% Wkly_upswing) and exits after
    EXIT_MAX_HOLD sessions. None while the trade would still be open."""
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    n, ep = len(c), float(o[e])
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
    """Same dip buys as the live rule, sold by each rule in EXIT_RULES."""
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        if not passes_filter(h["scanner_name"], dist_52w_high(df, sig["end_pos"]), atr_pct(df, sig["end_pos"])):
            continue
        base = simulate(df.iloc[sig["end_pos"] + 1:], sig["trigger"], h["scanner_name"])
        if "entry_date" not in base:
            continue
        e = int(df.index.get_loc(base["entry_date"]))
        common = {"scanner": h["scanner_name"], "symbol": h["symbol"], "cap": h["marketcap"],
                  "entry_date": pd.Timestamp(base["entry_date"])}
        if base["status"] in ("target", "stop", "time"):
            rows.append({**common, "rule": "target8", "ret": base["ret"], "why": base["status"],
                         "exit_date": pd.Timestamp(base["exit_date"]),
                         "days": int(df.index.get_loc(base["exit_date"])) - e + 1})
        for rule in EXIT_RULES:
            if rule == "target8":
                continue
            x = ride(df, e, h["scanner_name"], rule)
            if x:
                rows.append({**common, "rule": rule, **x})
    return pd.DataFrame(rows)


def exits_compare(et: pd.DataFrame, start: pd.Timestamp) -> list[dict]:
    """Per exit rule: trade stats and the ₹10L portfolio, from `start`, using
    only buys every rule has closed (so all rules see the same buys)."""
    if et.empty:
        return []
    et = et[et["entry_date"] >= start]
    key = ["scanner", "symbol", "entry_date"]
    done = et.groupby(key)["rule"].nunique()
    common = done[done == et["rule"].nunique()].index
    et = et.set_index(key).loc[common].reset_index()
    out = []
    for rule, label in EXIT_RULES.items():
        g = et[et["rule"] == rule]
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
