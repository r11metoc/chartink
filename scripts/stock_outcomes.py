"""If I had bought every scanner stock, how would it have done short,
medium and long term?

For every hit in data/backtest/*.csv (plus the bot's live triggers):
- entry = the bot's own rule: buy when price crosses the signal candle's
  high within 3 sessions (5 after a weekly signal); filled at the trigger,
  or at the open on a gap-up. Hits that never cross are counted as
  "not triggered".
- then just hold: no stop, no target, no costs.
- return after each horizon = close N sessions after the entry session.

Horizons (trading sessions):
  short  : 2 weeks (10), 1 month (21)
  medium : 3 months (63), 6 months (126)
  long   : 1 year (252), 2 years (504)

Each return is compared with the Nifty 500 over the same days.

Writes:
  reports/stock_outcomes.md          the report
  data/model/stock_outcomes.csv      one row per trade
  data/model/stock_summary.csv       one row per scanner x stock

Usage: python stock_outcomes.py
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone
from build_dataset import load_hits
from market_data import fetch_daily

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "stock_outcomes.md"
TRADES_CSV = ROOT / "data" / "model" / "stock_outcomes.csv"
SUMMARY_CSV = ROOT / "data" / "model" / "stock_summary.csv"
PERF_JSON = ROOT / "data" / "model" / "performance.json"
EXITS_CSV = ROOT / "data" / "model" / "exit_trades.csv"

HORIZONS = [("2w", 10, "Short"), ("1m", 21, "Short"), ("3m", 63, "Medium"),
            ("6m", 126, "Medium"), ("1y", 252, "Long"), ("2y", 504, "Long")]
LABEL = {"2w": "2 weeks", "1m": "1 month", "3m": "3 months", "6m": "6 months",
         "1y": "1 year", "2y": "2 years"}
BENCH_TICKERS = ["^CRSLDX", "^NSEI"]  # Nifty 500, else Nifty 50
MIN_STOCK_TRADES = 3


def trades(hits: pd.DataFrame, prices: dict[str, pd.DataFrame], bench: pd.Series | None) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        base = {"scanner_name": h["scanner_name"], "symbol": h["symbol"], "marketcap": h["marketcap"],
                "sector": h["sector"], "hit_date": h["hit_date"].date(), "source": h.get("source", "backtest")}
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            rows.append({**base, "status": "no_price_data"})
            continue
        fwd = df.iloc[sig["end_pos"] + 1:]
        window = bs.entry_window_for(h["scanner_name"])
        entry = bs.find_entry(fwd["Open"].to_numpy(), fwd["High"].to_numpy(), sig["trigger"], window) if len(fwd) else None
        if entry is None:
            status = "pending" if len(fwd) < window else "not_triggered"
            rows.append({**base, "status": status, "trigger": sig["trigger"]})
            continue
        e_i, e_px = entry
        closes = fwd["Close"].to_numpy()
        dates = fwd.index
        row = {**base, "status": "bought", "trigger": sig["trigger"], "entry_date": dates[e_i].date(),
               "entry_price": round(e_px, 2)}
        b0 = None
        if bench is not None:
            prior = bench[bench.index < dates[e_i]]
            b0 = prior.iloc[-1] if len(prior) else None
        for key, n, _ in HORIZONS:
            j = e_i + n
            if j >= len(closes):
                break
            seg = closes[e_i:j + 1]
            row[f"ret_{key}"] = round((closes[j] / e_px - 1) * 100, 2)
            row[f"best_{key}"] = round((seg.max() / e_px - 1) * 100, 2)
            row[f"worst_{key}"] = round((seg.min() / e_px - 1) * 100, 2)
            if b0 is not None:
                b1 = bench[bench.index <= dates[j]].iloc[-1]
                row[f"index_{key}"] = round((b1 / b0 - 1) * 100, 2)
        rows.append(row)
    return pd.DataFrame(rows)


def _pct(x: float) -> str:
    return "–" if pd.isna(x) else f"{x:+.1f}%"


def horizon_table(d: pd.DataFrame) -> list[str]:
    L = ["| Term | Horizon | Trades | Up | Avg | Median | Avg best / worst | Nifty 500 avg | Beat Nifty 500 | Avg vs Nifty 500 |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for key, _, term in HORIZONS:
        col = f"ret_{key}"
        if col not in d or d[col].notna().sum() == 0:
            continue
        x = d[d[col].notna()]
        r = x[col]
        idx = x.get(f"index_{key}")
        beat = (r > idx).mean() if idx is not None and idx.notna().any() else np.nan
        exc = (r - idx).mean() if idx is not None and idx.notna().any() else np.nan
        L.append(f"| {term} | {LABEL[key]} | {len(x)} | {(r > 0).mean():.0%} | {_pct(r.mean())} | {_pct(r.median())} | "
                 f"{_pct(x[f'best_{key}'].mean())} / {_pct(x[f'worst_{key}'].mean())} | "
                 f"{_pct(idx.mean() if idx is not None else np.nan)} | "
                 f"{'–' if pd.isna(beat) else f'{beat:.0%}'} | {_pct(exc)} |")
    return L


def group_table(d: pd.DataFrame, by: str, keys=("1m", "6m", "1y"), min_n: int = 20) -> list[str]:
    head = "| " + by.replace("_", " ").title() + " | " + " | ".join(
        f"{LABEL[k]}: n / up / avg / vs index" for k in keys) + " |"
    L = [head, "|---|" + "---|" * len(keys)]
    for g, x in sorted(d.groupby(by), key=lambda t: str(t[0])):
        cells = []
        for k in keys:
            c = f"ret_{k}"
            y = x[x[c].notna()] if c in x else x.iloc[0:0]
            if len(y) < min_n:
                cells.append(f"{len(y)} / – / – / –")
                continue
            exc = (y[c] - y[f"index_{k}"]).mean() if f"index_{k}" in y else np.nan
            cells.append(f"{len(y)} / {(y[c] > 0).mean():.0%} / {_pct(y[c].mean())} / {_pct(exc)}")
        L.append(f"| {g or 'Unknown'} | " + " | ".join(cells) + " |")
    return L


def stock_summary(b: pd.DataFrame) -> pd.DataFrame:
    agg = {"signals": ("symbol", "size"), "first": ("entry_date", "min"), "last": ("entry_date", "max"),
           "sector": ("sector", "last"), "marketcap": ("marketcap", "last")}
    for key, _, _ in HORIZONS:
        if f"ret_{key}" in b:
            agg[f"avg_{key}"] = (f"ret_{key}", "mean")
            agg[f"up_{key}"] = (f"ret_{key}", lambda s: (s > 0).mean() * 100 if s.notna().any() else np.nan)
    s = b.groupby(["scanner_name", "symbol"]).agg(**agg).reset_index()
    return s.round(1)


def stock_lines(s: pd.DataFrame, key: str, n: int = 10) -> list[str]:
    col = f"avg_{key}"
    x = s[(s["signals"] >= MIN_STOCK_TRADES) & s[col].notna()]
    if x.empty:
        return []
    L = []
    for title, part in (("Best", x.nlargest(n, col)), ("Worst", x.nsmallest(n, col))):
        L += ["", f"**{title} repeat stocks by average {LABEL[key]} return** (at least {MIN_STOCK_TRADES} buys)", "",
              "| Stock | Sector | Cap | Buys | Avg 1 month | Avg 6 months | Avg 1 year | Up after 1 year |",
              "|---|---|---|---|---|---|---|---|"]
        for _, r in part.iterrows():
            up = r.get("up_1y")
            L.append(f"| {r['symbol']} | {r['sector']} | {r['marketcap']} | {int(r['signals'])} | "
                     f"{_pct(r.get('avg_1m'))} | {_pct(r.get('avg_6m'))} | {_pct(r.get('avg_1y'))} | "
                     f"{'–' if pd.isna(up) else f'{up:.0f}%'} |")
    return L


def best_trades(b: pd.DataFrame, key: str = "1y", n: int = 10) -> list[str]:
    col = f"ret_{key}"
    x = b[b[col].notna()] if col in b else b.iloc[0:0]
    if x.empty:
        return []
    L = ["", f"**Biggest single winners after {LABEL[key]}**", "",
         "| Stock | Bought | Price | Return | Nifty 500 |", "|---|---|---|---|---|"]
    for _, r in x.nlargest(n, col).iterrows():
        L.append(f"| {r['symbol']} | {r['entry_date']} | {r['entry_price']:.2f} | {_pct(r[col])} | {_pct(r.get(f'index_{key}'))} |")
    return L


def build_report(t: pd.DataFrame, s: pd.DataFrame, dz: list[str] | None = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    b = t[t["status"] == "bought"].copy()
    if not b.empty:
        b["year"] = pd.to_datetime(b["entry_date"]).dt.year
    L = [f"# If I had bought every scanner stock", "",
         f"Generated {now} by `scripts/stock_outcomes.py` from `data/backtest/*.csv` plus the bot's live triggers.", "",
         "**Rule:** buy when price crosses the signal candle's high within 3 sessions (5 for `Wkly_upswing`), "
         "filled at the trigger or at the open on a gap-up; then hold. No stop, no target, no costs. "
         "**Short** = 2 weeks / 1 month, **Medium** = 3 / 6 months, **Long** = 1 / 2 years. "
         "**Beat Nifty 500** = share of buys that did better than the index over the same days. "
         "Recent buys only count for horizons that have fully passed.", "",
         "Per-trade data: `data/model/stock_outcomes.csv`; per-stock: `data/model/stock_summary.csv`.", ""]

    L += ["## All scanners at a glance", "",
          "| Scanner | Signals | Bought | 1 month avg | 6 months avg | 1 year avg | 2 years avg | 1 year vs Nifty 500 |",
          "|---|---|---|---|---|---|---|---|"]
    for name, x in t.groupby("scanner_name"):
        y = b[b["scanner_name"] == name]
        def m(k):
            c = f"ret_{k}"
            return y[c].mean() if c in y else np.nan
        exc = (y["ret_1y"] - y["index_1y"]).mean() if "ret_1y" in y and "index_1y" in y else np.nan
        L.append(f"| {name} | {len(x)} | {len(y)} | {_pct(m('1m'))} | {_pct(m('6m'))} | {_pct(m('1y'))} | "
                 f"{_pct(m('2y'))} | {_pct(exc)} |")

    for name, x in t.groupby("scanner_name"):
        y = b[b["scanner_name"] == name]
        counts = x["status"].value_counts()
        span = f"{pd.to_datetime(x['hit_date']).min():%d %b %Y} to {pd.to_datetime(x['hit_date']).max():%d %b %Y}"
        L += ["", f"## {name}", "",
              f"{len(x)} signals ({span}): {counts.get('bought', 0)} bought, "
              f"{counts.get('not_triggered', 0)} never crossed the trigger, "
              f"{counts.get('no_price_data', 0)} without Yahoo prices, {counts.get('pending', 0)} still pending.", ""]
        if y.empty:
            continue
        L += horizon_table(y)
        L += ["", "### By market cap", ""] + group_table(y, "marketcap", min_n=10)
        L += ["", "### By year bought", ""] + group_table(y, "year", min_n=10)
        L += ["", "### By sector (20+ buys)", ""] + [ln for ln in group_table(y, "sector", min_n=20)
                                                     if not ln.endswith("– / – / – |") or ln.startswith("|---")]
        L += stock_lines(s[s["scanner_name"] == name], "1y")
        L += best_trades(y)

    if dz is not None:
        L += dz

    L += ["", "## Reading this", "",
          "- Average vs median: a high average with a low median means a few big winners carry the result; "
          "most buys did worse than the average.",
          "- Compare with the Nifty 500 column: a scanner adds value only when its picks beat the index.",
          "- Stocks Yahoo no longer lists (delisted, renamed) are missing, which flatters long-term results "
          "a little (survivorship bias).",
          "- No costs, taxes or stop-loss are included; real results will be lower, and holding with no stop "
          "means sitting through every drawdown shown in 'Avg best / worst'."]
    return "\n".join(L) + "\n"


def main() -> int:
    hits = load_hits()
    symbols = sorted(hits["symbol"].unique())
    start = (hits["hit_date"].min() - timedelta(days=30)).date().isoformat()
    print(f"{len(hits)} hits, {len(symbols)} symbols, prices from {start}")
    prices = fetch_daily(symbols, start)
    idx = fetch_daily(BENCH_TICKERS, start)
    bench = next((idx[k]["Close"] for k in BENCH_TICKERS if k in idx), None)
    if bench is None:
        print("WARNING: no index data; 'vs Nifty 500' columns will be blank")

    t = trades(hits, prices, bench)
    b = t[t["status"] == "bought"]
    s = stock_summary(b) if not b.empty else pd.DataFrame()
    TRADES_CSV.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(TRADES_CSV, index=False)
    s.to_csv(SUMMARY_CSV, index=False)
    dt = dipzone.backtest_trades(hits, prices)
    et = dipzone.exit_trades(hits, prices)
    et.to_csv(EXITS_CSV, index=False)  # every dip buy, sold by each exit rule
    perf = dipzone.performance(dt, bench, et)
    PERF_JSON.write_text(json.dumps(perf, allow_nan=False), encoding="utf-8")
    dz = dipzone.performance_section(perf) + dipzone.backtest_section(hits, prices, dt)
    REPORT.write_text(build_report(t, s, dz), encoding="utf-8")
    print(f"Wrote {REPORT} ({len(b)} bought of {len(t)} signals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
