"""What if I had traded only one stock for the last N years?

Usage: python one_stock.py ENGINERSIN [years=5]

Compares, with ₹10L and 0.25% costs per round trip (taxes not included):
1. Buy and hold.
2. Swing every trend: buy at the next open after a close above the 30-day EMA,
   sell at the next open after a close below it, 15% stop (the bot's exit).
3. Only your scanners' signals on this stock (data/backtest/*.csv + live
   triggers) with the bot's live rule, all the money in each trade.
4. Hindsight ceiling: every swing of 10%+ bought at the exact bottom and sold
   at the exact top. Impossible in practice; shows how much the moves held.
5. Nifty 500 over the same dates.

Writes reports/one_stock_<SYMBOL>.md and prints it.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone

ROOT = Path(__file__).resolve().parent.parent
CAPITAL = 1_000_000
COST = bs.COST_PCT / 100


def _curve_stats(eq: pd.Series) -> dict:
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    return {"final": eq.iloc[-1], "cagr": ((eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1) * 100 if yrs > 0 else np.nan,
            "dd": (eq / eq.cummax() - 1).min() * 100}


def buy_hold(df: pd.DataFrame) -> dict:
    c = df["Close"]
    eq = CAPITAL * (1 - COST / 2) * c / df["Open"].iloc[0]
    return {**_curve_stats(eq), "trades": 1, "win": float(c.iloc[-1] > df["Open"].iloc[0]) * 100, "in_market": 100.0}


def run_trades(df: pd.DataFrame, trades: list[tuple[int, float, int, float]]) -> dict:
    """Equity with all money in each (entry_i, entry_px, exit_i, exit_px) trade, cash otherwise."""
    c = df["Close"].to_numpy()
    eq = np.full(len(df), np.nan)
    cash, last = float(CAPITAL), 0
    rets, held = [], 0
    for e, ep, x, xp in trades:
        eq[last:e] = cash
        shares = cash * (1 - COST / 2) / ep
        eq[e:x] = shares * c[e:x]
        cash = shares * xp * (1 - COST / 2)
        rets.append(xp / ep - 1 - COST)
        held += x - e
        last = x
    eq[last:] = cash
    eq = pd.Series(eq, index=df.index).ffill().fillna(CAPITAL)
    r = np.array(rets)
    return {**_curve_stats(eq), "trades": len(r), "win": (r > 0).mean() * 100 if len(r) else np.nan,
            "avg": r.mean() * 100 if len(r) else np.nan, "in_market": held / len(df) * 100}


def ema_swings(df: pd.DataFrame) -> list[tuple[int, float, int, float]]:
    o, l, c = (df[k].to_numpy(dtype=float) for k in ("Open", "Low", "Close"))
    ema = dipzone.exit_line(df["Close"])
    out, i, n = [], 1, len(df)
    while i < n - 1:
        if not np.isnan(ema[i]) and c[i] > ema[i] and c[i - 1] <= ema[i - 1]:
            e = i + 1
            ep = o[e]
            stop = ep * (1 - dipzone.STOP_PCT / 100)
            x, xp = n - 1, c[-1]
            for j in range(e, n):
                if l[j] <= stop:
                    x, xp = j, min(o[j], stop) if j > e else stop
                    break
                if j > e and c[j] < ema[j] and j + 1 < n:
                    x, xp = j + 1, o[j + 1]
                    break
            out.append((e, ep, x, xp))
            i = x + 1
        else:
            i += 1
    return out


def scanner_trades(df: pd.DataFrame, symbol: str) -> tuple[list, list[str]]:
    from hits import load_hits
    hits = load_hits()
    hits = hits[(hits["symbol"] == symbol) & (hits["hit_date"] >= df.index[0])].sort_values("hit_date")
    out, notes, busy_until = [], [], -1
    for _, h in hits.iterrows():
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"]))
        if sig is None or sig["end_pos"] <= busy_until:
            continue
        if not dipzone.passes_filter(h["scanner_name"], dipzone.dist_52w_high(df, sig["end_pos"]),
                                     dipzone.atr_pct(df, sig["end_pos"])):
            notes.append(f"{h['hit_date']:%d %b %Y} {h['scanner_name']}: skipped by the filter")
            continue
        s = dipzone.live_sim(df, sig, h["scanner_name"])
        if "entry_date" not in s:
            notes.append(f"{h['hit_date']:%d %b %Y} {h['scanner_name']}: never crossed {sig['trigger']:.2f}")
            continue
        e = int(df.index.get_loc(s["entry_date"]))
        if s["status"] in dipzone.CLOSED:
            x, xp = int(df.index.get_loc(s["exit_date"])), s["exit"]
        else:
            x, xp = len(df) - 1, float(df["Close"].iloc[-1])
        out.append((e, s["entry"], x, xp))
        notes.append(f"{h['hit_date']:%d %b %Y} {h['scanner_name']}: bought {s['entry_date']:%d %b %Y} at {s['entry']:.2f}, "
                     + (f"sold {s['exit_date']:%d %b %Y} at {s['exit']:.2f} ({s['ret']:+.1f}%)" if s["status"] in dipzone.CLOSED
                        else f"still open ({s['ret']:+.1f}%)"))
        busy_until = x
    return out, notes


def hindsight(df: pd.DataFrame, swing: float = 0.10) -> list[tuple[int, float, int, float]]:
    """Exact low-to-high legs of every 10%+ swing (zigzag on closes)."""
    c = df["Close"].to_numpy(dtype=float)
    piv, trend, lo_i, hi_i = [], 0, 0, 0
    for i in range(1, len(c)):
        if trend >= 0:
            if c[i] > c[hi_i]:
                hi_i = i
            if c[i] <= c[hi_i] * (1 - swing):
                if trend == 1:
                    piv.append(("H", hi_i))
                trend, lo_i = -1, i
        if trend <= 0:
            if c[i] < c[lo_i]:
                lo_i = i
            if c[i] >= c[lo_i] * (1 + swing):
                piv.append(("L", lo_i))
                trend, hi_i = 1, i
    if trend == 1:
        piv.append(("H", hi_i))
    out = []
    for (k1, a), (k2, b) in zip(piv, piv[1:]):
        if k1 == "L" and k2 == "H":
            out.append((a, c[a], b, c[b]))
    return out


def report(symbol: str, df: pd.DataFrame, bench: pd.Series | None, years: int) -> str:
    rows = [("Buy and hold", buy_hold(df)),
            (f"Swing every trend ({dipzone.EXIT_LABEL})", run_trades(df, ema_swings(df)))]
    st, notes = scanner_trades(df, symbol)
    rows.append(("Only your scanners' signals", run_trades(df, st)))
    hs = hindsight(df)
    rows.append(("Hindsight: every 10%+ swing, exact bottom/top", run_trades(df, hs)))
    if bench is not None:
        b = bench[(bench.index >= df.index[0]) & (bench.index <= df.index[-1])].dropna()
        if len(b) > 1:
            rows.append(("Nifty 500 instead", {**_curve_stats(CAPITAL * b / b.iloc[0]), "trades": 1, "win": np.nan, "in_market": 100.0}))
    L = [f"# {symbol}: last {years} years ({df.index[0]:%d %b %Y} to {df.index[-1]:%d %b %Y})", "",
         f"₹10L, all the money in the trade, 0.25% costs a round trip; taxes not included. "
         f"Price {df['Close'].iloc[0]:.2f} → {df['Close'].iloc[-1]:.2f}; highest close {df['Close'].max():.2f}, lowest {df['Close'].min():.2f}.", "",
         "| Way of trading | ₹10L became | Per year | Worst fall | Trades | Won | Time invested |", "|---|---|---|---|---|---|---|"]
    for name, s in rows:
        win = "–" if np.isnan(s.get("win", np.nan)) else f"{s['win']:.0f}%"
        L.append(f"| {name} | ₹{s['final'] / 1e5:.1f}L | {s['cagr']:+.1f}% | {s['dd']:.1f}% | {s['trades']} | {win} | {s['in_market']:.0f}% |")
    L += ["", "## Your scanners on this stock", ""] + ([f"- {n}" for n in notes] or ["- No scanner signals in this period."])
    yearly = df["Close"].resample("YE").last()
    L += ["", "## Stock by year", "", "| Year | Change |", "|---|---|"]
    prev = df["Close"].iloc[0]
    for d, v in yearly.items():
        L.append(f"| {d.year} | {(v / prev - 1) * 100:+.1f}% |")
        prev = v
    L += ["", f"Hindsight swings found: {len(hs)} rises of 10% or more. No rule can catch them all; "
          "the trend rule gives back part of each move at both ends."]
    return "\n".join(L) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    symbol = sys.argv[1].strip().upper()
    years = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    start = (date.today() - timedelta(days=int(365.25 * years))).isoformat()
    df = fetch_daily([symbol], start).get(symbol)
    if df is None or df.empty:
        print(f"No prices for {symbol} on Yahoo.")
        return 1
    idx = fetch_daily(["^CRSLDX", "^NSEI"], start)
    bench = next((idx[k]["Close"] for k in ("^CRSLDX", "^NSEI") if k in idx), None)
    text = report(symbol, df, bench, years)
    out = ROOT / "reports" / f"one_stock_{symbol}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
