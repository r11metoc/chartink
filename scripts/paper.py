"""Paper portfolio: every trigger since PAPER_START traded on paper under the
backtest's own rule (breakout_sim), so live results compare like for like.

Signals are the bot's live triggers plus any Chartink backtest-export hits
dated on or after PAPER_START (same scanner definitions, so still forward
data). Rule: buy-stop at the signal candle's high for 3 sessions (5 after a
weekly signal), stop at the candle's low (kept 2-8% below entry), target 2x
that risk, out after 20 sessions; 0.25% round-trip costs. Recomputed from
daily prices on every run, so nothing is stored and a corrected price fixes
itself.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

import breakout_sim as bs
import db
from slot_gate import IST

PAPER_START = "2026-09-25"
STAKE = 100_000  # rupees per trade, for the P&L column
BENCHMARK = "^CRSLDX"  # Nifty 500, as in the backtest's "vs index"
MARKET_OPEN = (9, 15)


def _frame(conn, symbol: str, since: str) -> pd.DataFrame:
    rows = db.daily_prices_since(conn, symbol, since)
    df = pd.DataFrame(rows, columns=["date", "Open", "High", "Low", "Close"])
    df.index = pd.to_datetime(df.pop("date"))
    return df


def _signals(conn) -> list[tuple[str, str, str, str]]:
    """(hit_date, scanner, symbol, source), one per scanner/symbol/day."""
    seen: dict[tuple[str, str, str], str] = {}
    start = datetime.fromisoformat(PAPER_START).replace(tzinfo=IST)
    for e in db.breakouts_since(conn, start.isoformat()):
        t = datetime.fromisoformat(e["detected_at"]).astimezone(IST)
        # Before the open the scanner still shows the previous session's result.
        day = (t - timedelta(days=1) if (t.hour, t.minute) < MARKET_OPEN else t).date().isoformat()
        seen.setdefault((day, e["scanner_name"], e["symbol"]), "live")
    for scanner, symbol, day in conn.execute(
            "SELECT scanner_name, symbol, hit_date FROM backtest_hits WHERE hit_date >= ?", (PAPER_START,)):
        seen.setdefault((day, scanner, symbol), "backtest export")
    return sorted((d, sc, sym, src) for (d, sc, sym), src in seen.items())


def _bench_return(bench: pd.DataFrame, entry: pd.Timestamp, exit_: pd.Timestamp) -> float | None:
    if bench.empty:
        return None
    before = bench["Close"][bench.index < entry]
    after = bench["Close"][bench.index <= exit_]
    if before.empty or after.empty:
        return None
    return (after.iloc[-1] / before.iloc[-1] - 1) * 100


def paper_trades(conn) -> list[dict]:
    lookback = (datetime.fromisoformat(PAPER_START) - timedelta(days=14)).date().isoformat()
    bench = _frame(conn, BENCHMARK, lookback)
    out = []
    for day, scanner, symbol, source in _signals(conn):
        trade = {"scanner": scanner, "symbol": symbol, "date": day, "source": source}
        df = _frame(conn, symbol, lookback)
        # A daily hit on a non-trading day (weekend, holiday) belongs to the last
        # session before it; one simply not in the data yet waits for its candle.
        hit = pd.Timestamp(day)
        if (not bs.is_weekly(scanner) and not df.empty and hit not in df.index
                and (hit.weekday() >= 5 or df.index[-1] > hit)):
            earlier = df.index[df.index <= hit]
            hit = earlier[-1] if len(earlier) else hit
        sig = bs.signal_bar(df, hit, bs.is_weekly(scanner)) if not df.empty else None
        if sig is None:
            out.append({**trade, "status": "no prices yet"})
            continue
        path = df.iloc[sig["end_pos"] + 1:]
        res = bs.simulate_trade(path, sig["trigger"], sig["bar_low"], bs.entry_window_for(scanner))
        trade["trigger"] = round(sig["trigger"], 2)
        if "entry_price" not in res:
            out.append({**trade, "status": "waiting" if res["status"] == "pending" else "not filled"})
            continue
        entry_date = path.index[res["entry_offset"]]
        exit_date = path.index[res["exit_offset"]]
        bench_ret = _bench_return(bench, entry_date, exit_date)
        out.append({
            **trade,
            "status": "open" if res["status"] == "pending" else "closed",
            "entry_date": entry_date.date().isoformat(),
            "entry": round(res["entry_price"], 2),
            "stop": round(res["stop"], 2),
            "target": round(res["target"], 2),
            "exit_date": exit_date.date().isoformat(),
            "exit": round(float(res["exit_price"]), 2),
            "exit_reason": res["exit_reason"],
            "ret": round(float(res["ret_pct"]), 2),
            "pnl": int(round(res["ret_pct"] / 100 * STAKE)),
            "vs_index": round(float(res["ret_pct"] - bench_ret), 2) if bench_ret is not None else None,
            "days": int(res["hold_days"]),
        })
    return out


def summarize(trades: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {"All scanners": trades}
    for t in trades:
        groups.setdefault(t["scanner"], []).append(t)
    out = []
    for name, ts in groups.items():
        closed = [t for t in ts if t["status"] == "closed"]
        open_ = [t for t in ts if t["status"] == "open"]
        excess = [t["vs_index"] for t in closed if t["vs_index"] is not None]
        out.append({
            "group": name,
            "signals": len(ts),
            "waiting": sum(t["status"] in ("waiting", "no prices yet") for t in ts),
            "not_filled": sum(t["status"] == "not filled" for t in ts),
            "open": len(open_),
            "open_pnl": sum(t["pnl"] for t in open_),
            "closed": len(closed),
            "win": round(100 * sum(t["ret"] > 0 for t in closed) / len(closed)) if closed else None,
            "avg": round(sum(t["ret"] for t in closed) / len(closed), 2) if closed else None,
            "vs_index": round(sum(excess) / len(excess), 2) if excess else None,
            "closed_pnl": sum(t["pnl"] for t in closed),
        })
    return out
