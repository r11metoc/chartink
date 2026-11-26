"""How good is a Chartink scan? Check a backtest export against the live rule.

Usage: python scan_quality.py "<Chartink backtest export.csv>" [--weekly]

For every hit (Date, Symbol, Marketcapname, Sector) it fetches daily prices
(Yahoo) and applies the bot's live rule: buy-stop at the signal day's high for
3 sessions (5 for a weekly scan), sell at the next open after a close below the
30-day EMA, 15% stop, at most 250 sessions, 0.25% costs. Then it compares:

- per trade: trades, win rate, average, average win / loss, days held;
- the same stocks on random days (does the scan's timing add anything?);
- a ₹10L, 15-slot portfolio vs the Nifty 500 over the same dates;
- per year, per market cap and per sector;
- data checks: duplicates, weekend dates, symbols Yahoo doesn't know.

Writes reports/scan_quality_<file name>.md and prints it.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone

ROOT = Path(__file__).resolve().parent.parent
RANDOM_DRAWS = 3


def load(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, encoding="utf-8-sig")
    d.columns = [c.strip() for c in d.columns]
    d["hit_date"] = pd.to_datetime(d["Date"], format="%d-%m-%Y")
    d["symbol"] = d["Symbol"].astype(str).str.strip().str.upper()
    d["marketcap"] = d.get("Marketcapname", pd.Series("", index=d.index)).fillna("").astype(str).str.strip()
    d["sector"] = d.get("Sector", pd.Series("", index=d.index)).fillna("").astype(str).str.strip()
    return d


def trades_for(hits: pd.DataFrame, prices: dict, scanner: str) -> pd.DataFrame:
    h = hits.assign(scanner_name=scanner)
    t = dipzone.backtest_trades(h, prices)
    if t.empty:
        return t
    sec = hits.drop_duplicates("symbol").set_index("symbol")["sector"]
    return t.assign(sector=t["symbol"].map(sec))


def random_hits(hits: pd.DataFrame, prices: dict, seed: int) -> pd.DataFrame:
    """Same stocks, random trading days in the same date range."""
    rng = np.random.default_rng(seed)
    lo, hi = hits["hit_date"].min(), hits["hit_date"].max()
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        if df is None:
            continue
        days = df.index[(df.index >= lo) & (df.index <= hi)]
        if len(days):
            rows.append({**h.to_dict(), "hit_date": days[rng.integers(len(days))]})
    return pd.DataFrame(rows)


EXITS = {
    "bounce": "sell when the close is back above the 5-day average (max 10 days, 8% stop)",
    "t3w": "+3% target, 12% stop, max 30 days",
    "t5w": "+5% target, 15% stop, max 40 days",
    "t5": "+5% target, 8% stop, max 20 days",
    "t10": "+10% target, 8% stop, max 40 days",
    "ema": f"ride: sell below the {dipzone.EXIT_LABEL}, {dipzone.STOP_PCT:g}% stop",
}


def _exit(o, h, l, c, sma5, ema, e: int, rule: str) -> tuple[int, float] | None:
    """(exit bar, exit price) for a buy at the open of bar e, or None while still open."""
    ep, n = o[e], len(c)
    stop = ep * (1 - {"ema": dipzone.STOP_PCT, "t3w": 12.0, "t5w": 15.0}.get(rule, 8.0) / 100)
    tgt = {"t3w": 1.03, "t5w": 1.05, "t5": 1.05, "t10": 1.10}.get(rule)
    maxd = {"bounce": 10, "t3w": 30, "t5w": 40, "t5": 20, "t10": 40, "ema": dipzone.RIDE_MAX_HOLD}[rule]
    for i in range(e, min(n, e + maxd + 1)):
        if i > e and o[i] <= stop:
            return i, o[i]
        if l[i] <= stop:
            return i, stop
        if tgt:
            if i > e and o[i] >= ep * tgt:
                return i, o[i]
            if h[i] >= ep * tgt:
                return i, ep * tgt
        if rule == "bounce" and c[i] > sma5[i] and i + 1 < n:
            return i + 1, o[i + 1]
        if rule == "ema" and i > e and not np.isnan(ema[i]) and c[i] < ema[i] and i + 1 < n:
            return i + 1, o[i + 1]
        if i == e + maxd:
            return i, c[i]
    return None


def other_exits(hits: pd.DataFrame, prices: dict, weekly: bool) -> dict[str, pd.DataFrame]:
    """Every hit bought at the next open, sold by each rule in EXITS."""
    rows = {k: [] for k in EXITS}
    cache = {}
    for _, hh in hits.iterrows():
        df = prices.get(hh["symbol"])
        sig = bs.signal_bar(df, hh["hit_date"], weekly) if df is not None else None
        if sig is None or sig["end_pos"] + 1 >= len(df):
            continue
        if hh["symbol"] not in cache:
            c = df["Close"]
            cache[hh["symbol"]] = (*(df[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")),
                                   c.rolling(5).mean().to_numpy(), dipzone.exit_line(c))
        o, h, l, c, sma5, ema = cache[hh["symbol"]]
        e = sig["end_pos"] + 1
        for k in EXITS:
            x = _exit(o, h, l, c, sma5, ema, e, k)
            if x:
                rows[k].append({"scanner": "scan", "symbol": hh["symbol"], "cap": hh["marketcap"],
                                "entry_date": df.index[e], "exit_date": df.index[x[0]],
                                "ret": (x[1] / o[e] - 1) * 100 - bs.COST_PCT, "days": x[0] - e + 1,
                                "status": "stop" if x[1] < o[e] * 0.95 else "other"})
    return {k: pd.DataFrame(v) for k, v in rows.items()}


def stats(t: pd.DataFrame) -> dict:
    r = t["ret"]
    return {"trades": len(t), "win": (r > 0).mean() * 100 if len(t) else np.nan, "avg": r.mean(),
            "avg_win": r[r > 0].mean(), "avg_loss": r[r <= 0].mean(), "days": t["days"].mean(),
            "stop": (t["status"] == "stop").mean() * 100 if len(t) else np.nan}


def row(name: str, s: dict) -> str:
    return (f"| {name} | {s['trades']} | {s['win']:.0f}% | {s['avg']:+.2f}% | {s['avg_win']:+.1f}% / {s['avg_loss']:+.1f}% "
            f"| {s['days']:.0f} | {s['stop']:.0f}% |")


def report(name: str, hits: pd.DataFrame, prices: dict, bench: pd.Series | None, weekly: bool) -> str:
    scanner = "Wkly_upswing" if weekly else "Backtest_New"
    t = trades_for(hits, prices, scanner)
    L = [f"# Scan quality: {name}", "",
         f"{len(hits):,} hits, {hits['symbol'].nunique()} stocks, {hits['hit_date'].min():%d %b %Y} to "
         f"{hits['hit_date'].max():%d %b %Y}. Live rule: buy-stop at the signal {'week' if weekly else 'day'}'s high for "
         f"{bs.entry_window_for(scanner)} sessions, sell below the {dipzone.EXIT_LABEL}, {dipzone.STOP_PCT:g}% stop, 0.25% costs.", ""]
    missing = sorted(set(hits["symbol"]) - set(prices))
    wk = hits["hit_date"].dt.dayofweek >= 5
    L += ["## Data checks", "",
          f"- Duplicate rows: {hits.duplicated(['Date', 'Symbol']).sum()}",
          f"- Weekend dates: {int(wk.sum())}" + (f" ({', '.join(sorted({d.strftime('%d %b %Y') for d in hits.loc[wk, 'hit_date']}))})" if wk.any() else ""),
          f"- Stocks without Yahoo prices: {len(missing)}" + (f" ({', '.join(missing[:15])}{'…' if len(missing) > 15 else ''})" if missing else ""),
          f"- Hits per day: median {hits.groupby('hit_date').size().median():.0f}, max {hits.groupby('hit_date').size().max()}",
          f"- Market caps: " + ", ".join(f"{k or 'blank'} {v}" for k, v in hits["marketcap"].value_counts().items()), ""]
    if t.empty:
        return "\n".join(L + ["No closed trades: nothing crossed its trigger, or no prices."]) + "\n"
    s = stats(t)
    base = pd.concat([trades_for(random_hits(hits, prices, k), prices, scanner) for k in range(RANDOM_DRAWS)])
    b = stats(base) if not base.empty else None
    crossed = len(t) / max(1, len(hits)) * 100
    L += ["## Per trade", "", "| | Trades | Won | Avg | Avg win / loss | Days held | Stopped out |", "|---|---|---|---|---|---|---|",
          row("This scan", s)] + ([row(f"Same stocks, random days (x{RANDOM_DRAWS})", b)] if b else []) + [
          "", f"{crossed:.0f}% of hits crossed their trigger in time and closed (open trades not counted).",
          "Reference, the bot's three scanners 2019-26 under the same rule: 6,487 trades, 43% won, +4.2% a trade.", ""]
    pf = dipzone.portfolio(t)
    eq = pf["equity"]
    cagr = dipzone._cagr(pf["capital"], eq.iloc[-1], eq.index[0], eq.index[-1])
    dd = (eq / eq.cummax() - 1).min() * 100
    alt = other_exits(hits, prices, weekly)
    L += ["## Other ways to trade the same signals (buy at the next open)", "",
          "| Sell rule | Trades | Won | Avg | Avg win / loss | Days | ₹10L, 15 slots: per year | Worst fall |",
          "|---|---|---|---|---|---|---|---|"]
    for k, label in EXITS.items():
        a = alt[k]
        if a.empty:
            continue
        sa = stats(a)
        pa = dipzone.portfolio(a)["equity"]
        ca = dipzone._cagr(1_000_000, pa.iloc[-1], pa.index[0], pa.index[-1])
        L.append(f"| {label} | {sa['trades']} | {sa['win']:.0f}% | {sa['avg']:+.2f}% | {sa['avg_win']:+.1f}% / {sa['avg_loss']:+.1f}% "
                 f"| {sa['days']:.0f} | {ca:.1f}% | {(pa / pa.cummax() - 1).min() * 100:.1f}% |")
    L += ["", "A high win rate only pays when the average trade (Avg) stays well above zero.", ""]
    L += ["## ₹10L portfolio, 15 slots (this scan alone)", "",
          f"₹10L → ₹{eq.iloc[-1] / 1e5:.1f}L, {cagr:.1f}% a year, worst fall {dd:.1f}%, "
          f"{len(pf['taken'])} trades taken, {pf['skipped']} skipped (no free slot)."]
    if bench is not None:
        bb = bench[(bench.index >= eq.index[0]) & (bench.index <= eq.index[-1])].dropna()
        if len(bb) > 1:
            L.append(f"Nifty 500 over the same dates: {dipzone._cagr(bb.iloc[0], bb.iloc[-1], bb.index[0], bb.index[-1]):.1f}% a year, "
                     f"worst fall {(bb / bb.cummax() - 1).min() * 100:.1f}%.")
    yearly = eq.resample("YE").last()
    prev = yearly.shift(1).fillna(pf["capital"])
    L += ["", "| Year | Portfolio | Trades | Won | Avg |", "|---|---|---|---|---|"]
    for d, v, p in zip(yearly.index, yearly, prev):
        g = t[t["entry_date"].dt.year == d.year]
        L.append(f"| {d.year} | {(v / p - 1) * 100:+.1f}% | {len(g)} | {(g['ret'] > 0).mean() * 100:.0f}% | {g['ret'].mean():+.2f}% |"
                 if len(g) else f"| {d.year} | {(v / p - 1) * 100:+.1f}% | 0 | – | – |")
    for by, title in (("cap", "Market cap"), ("sector", "Sector (10+ trades)")):
        L += ["", f"| {title} | Trades | Won | Avg |", "|---|---|---|---|"]
        for k, g in sorted(t.groupby(by), key=lambda x: -len(x[1])):
            if len(g) >= (10 if by == "sector" else 1):
                L.append(f"| {k or 'blank'} | {len(g)} | {(g['ret'] > 0).mean() * 100:.0f}% | {g['ret'].mean():+.2f}% |")
    best = t.nlargest(5, "ret")
    L += ["", "Best trades: " + ", ".join(f"{r.symbol} {r.ret:+.0f}% ({r.entry_date:%b %Y})" for r in best.itertuples())]
    top = t.nlargest(max(1, len(t) // 20), "ret")["ret"].sum()
    if t["ret"].sum() > 0:
        share = top / t["ret"].sum() * 100
        L += ["", "The best 5% of trades made " + ("more than all of the net profit (the rest lost money overall)."
                                                    if share > 100 else f"{share:.0f}% of the net profit.")]
    return "\n".join(L) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    path = Path(sys.argv[1])
    hits = load(path)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    syms = sorted(hits["symbol"].unique())
    print(f"{len(hits)} hits, {len(syms)} stocks: fetching prices since {start}…")
    prices = fetch_daily(syms, start)
    idx = fetch_daily(["^CRSLDX", "^NSEI"], start)
    bench = next((idx[k]["Close"] for k in ("^CRSLDX", "^NSEI") if k in idx), None)
    text = report(path.stem, hits, prices, bench, "--weekly" in sys.argv)
    out = ROOT / "reports" / f"scan_quality_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
