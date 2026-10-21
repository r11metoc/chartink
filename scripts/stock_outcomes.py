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
  data/model/reentry_trades.csv      trigger-price stop with re-entry, one row per signal
  data/model/pullback_rules.csv      pullback buy rules (scripts/pullback.py), one row per signal x rule

Usage: python stock_outcomes.py
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import candidates
import dipzone
import pullback
from build_dataset import load_hits
from market_data import fetch_daily

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "stock_outcomes.md"
TRADES_CSV = ROOT / "data" / "model" / "stock_outcomes.csv"
SUMMARY_CSV = ROOT / "data" / "model" / "stock_summary.csv"
REENTRY_CSV = ROOT / "data" / "model" / "reentry_trades.csv"
PULLBACK_CSV = ROOT / "data" / "model" / "pullback_rules.csv"

HORIZONS = [("2w", 10, "Short"), ("1m", 21, "Short"), ("3m", 63, "Medium"),
            ("6m", 126, "Medium"), ("1y", 252, "Long"), ("2y", 504, "Long")]
LABEL = {"2w": "2 weeks", "1m": "1 month", "3m": "3 months", "6m": "6 months",
         "1y": "1 year", "2y": "2 years"}
BENCH_TICKERS = ["^CRSLDX", "^NSEI"]  # Nifty 500, else Nifty 50
MIN_STOCK_TRADES = 3


REENTRY_WINDOW = 63  # sessions after the signal in which a (re-)entry is allowed (3 months)
REENTRY_MODES = {
    "close": "sell at the next open after a daily close below the trigger",
    "intraday": "sell the moment price trades below the trigger (at the trigger, or the open on a gap-down)",
}


def simulate_reentry(o, h, l, c, trigger: float, mode: str, window: int = REENTRY_WINDOW) -> dict:
    """Buy above the trigger, sell below it, buy again above it, for as long
    as entries are allowed (`window` sessions); a position opened in the
    window is held with no target and no time limit until the stop."""
    legs, pos, e_i, e_px, sell_next_open = [], False, 0, 0.0, False
    n = len(c)
    for i in range(n):
        if pos and sell_next_open:  # close-mode exit decided yesterday
            legs.append((e_i, i, e_px, float(o[i]), "stop"))
            pos, sell_next_open = False, False
        if not pos:
            if i >= window or h[i] <= trigger:
                continue
            e_px, e_i, pos = max(float(o[i]), trigger), i, True
            gapped_in = o[i] >= trigger
            if mode == "intraday" and gapped_in and l[i] < trigger:
                legs.append((e_i, i, e_px, trigger, "stop"))
                pos = False
                continue
            if mode == "close" and c[i] < trigger:
                sell_next_open = True
            continue
        if mode == "intraday":
            if o[i] < trigger:
                legs.append((e_i, i, e_px, float(o[i]), "stop")); pos = False
            elif l[i] < trigger:
                legs.append((e_i, i, e_px, trigger, "stop")); pos = False
        elif c[i] < trigger:
            sell_next_open = True
    if pos:
        legs.append((e_i, n - 1, e_px, float(c[-1]), "holding"))
    growth = 1.0
    for _, _, a, b, _ in legs:
        growth *= (b / a) * (1 - bs.COST_PCT / 100)
    return {"legs": legs, "total_ret": (growth - 1) * 100 if legs else np.nan,
            "days_in": sum(x - e + 1 for e, x, *_ in legs)}


def reentry_trades(hits: pd.DataFrame, prices: dict[str, pd.DataFrame], bench: pd.Series | None) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        fwd = df.iloc[sig["end_pos"] + 1:]
        if len(fwd) == 0:
            continue
        arr = [fwd[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close")]
        for mode in REENTRY_MODES:
            r = simulate_reentry(*arr, sig["trigger"], mode)
            if not r["legs"]:
                continue
            first, last = r["legs"][0], r["legs"][-1]
            d0, d1 = fwd.index[first[0]], fwd.index[last[1]]
            row = {"mode": mode, "scanner_name": h["scanner_name"], "symbol": h["symbol"],
                   "marketcap": h["marketcap"], "sector": h["sector"], "hit_date": h["hit_date"].date(),
                   "trigger": round(sig["trigger"], 2), "entries": len(r["legs"]),
                   "first_entry": d0.date(), "last_exit": d1.date(), "status": last[4],
                   "total_ret": round(r["total_ret"], 2), "days_invested": r["days_in"],
                   "span_days": last[1] - first[0] + 1,
                   "last_leg_ret": round((last[3] / last[2] - 1) * 100, 2)}
            if bench is not None:
                b0 = bench[bench.index < d0]
                b1 = bench[bench.index <= d1]
                if len(b0) and len(b1):
                    row["index_ret"] = round((b1.iloc[-1] / b0.iloc[-1] - 1) * 100, 2)
            rows.append(row)
    return pd.DataFrame(rows)


def reentry_section(rt: pd.DataFrame) -> list[str]:
    if rt.empty:
        return []
    L = ["", "## Trigger-price stop with re-entry", "",
         "Buy when price crosses above the trigger (the signal candle's high). No target and no time limit. "
         "Sell when price falls below the trigger; buy again each time it climbs back above it, for "
         f"{REENTRY_WINDOW} sessions (3 months) after the signal. A position bought inside those 3 months is "
         "held until the stop, however long that takes; open positions are valued at the latest close. "
         f"Every buy/sell pays {bs.COST_PCT}% costs. Two versions of the stop:", ""]
    L += [f"- **{m}**: {d}" for m, d in REENTRY_MODES.items()]
    L += ["", "Return = all the buys and sells of one signal compounded. Nifty 500 = from the first buy to the "
          "last sell (or today).", ""]
    for mode in REENTRY_MODES:
        x = rt[rt["mode"] == mode]
        L += [f"### Stop on {'a close' if mode == 'close' else 'any trade'} below the trigger", "",
              "| Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | Worst 10% avg | "
              "Avg days invested | Still holding | Nifty 500 avg | Avg vs Nifty 500 |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, y in [(n, g) for n, g in x.groupby("scanner_name")] + [("**All**", x)]:
            r = y["total_ret"]
            worst = r[r <= r.quantile(0.10)].mean()
            idx = y["index_ret"] if "index_ret" in y else pd.Series(dtype=float)
            L.append(f"| {name} | {len(y)} | {y['entries'].mean():.1f} | {(r > 0).mean():.0%} | {_pct(r.mean())} | "
                     f"{_pct(r.median())} | {_pct(worst)} | {y['days_invested'].mean():.0f} | "
                     f"{(y['status'] == 'holding').sum()} | {_pct(idx.mean())} | {_pct((r - idx).mean())} |")
        L += ["", "| Scanner | Cap | Signals | Profitable | Avg return | Median | Avg days invested |",
              "|---|---|---|---|---|---|---|"]
        for (name, cap), y in x.groupby(["scanner_name", "marketcap"]):
            if len(y) < 20:
                continue
            r = y["total_ret"]
            L.append(f"| {name} | {cap or 'Unknown'} | {len(y)} | {(r > 0).mean():.0%} | {_pct(r.mean())} | "
                     f"{_pct(r.median())} | {y['days_invested'].mean():.0f} |")
        L += ["", "| Buys per signal | Signals | Profitable | Avg return |", "|---|---|---|---|"]
        for k, y in x.groupby(x["entries"].clip(upper=6)):
            r = y["total_ret"]
            L.append(f"| {k if k < 6 else '6+'} | {len(y)} | {(r > 0).mean():.0%} | {_pct(r.mean())} |")
        L.append("")
    return L


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


def build_report(t: pd.DataFrame, s: pd.DataFrame, rt: pd.DataFrame | None = None,
                 pb: tuple | None = None, dz: list[str] | None = None) -> str:
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

    if rt is not None:
        L += reentry_section(rt)
    if pb is not None:
        L += pullback.section(*pb)
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
    cand = candidates.candidate_hits()
    if not cand.empty:  # candidate scanner versions need their prices too
        symbols = sorted(set(symbols) | set(cand["symbol"]))
        start = min(start, (cand["hit_date"].min() - timedelta(days=30)).date().isoformat())
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
    rt = reentry_trades(hits, prices, bench)
    rt.to_csv(REENTRY_CSV, index=False)
    pb = pullback.analyse(hits, prices)
    pb[0].to_csv(PULLBACK_CSV, index=False)
    dz = dipzone.backtest_section(hits, prices) + candidates.section(hits, prices)
    REPORT.write_text(build_report(t, s, rt, pb, dz), encoding="utf-8")
    print(f"Wrote {REPORT} ({len(b)} bought of {len(t)} signals)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
