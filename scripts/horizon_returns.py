"""Where was each scanner stock 2, 4, 6, 8 and 12 weeks after it crossed
the trigger price? Plain buy-and-hold from the trigger: no stop, no target.

For every backtest hit (data/model/signals.csv + paths.csv.gz, built by
build_dataset.py):
- entry = first session within the entry window whose high crosses the
  trigger (signal candle high), filled at the trigger or the open on a gap-up
- price N weeks later = close 5*N sessions after the entry session
- also the best and worst close reached within each horizon, and the
  Nifty 500's move over the same days

Also compares trailing-stop exits with plain holding on the same trades.

Writes data/model/horizon_returns.csv (one row per trade, with the prices)
and reports/horizon_returns.md (summary per scanner).

Usage: python horizon_returns.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
from signal_model import MODEL_DIR, add_benchmark, closed_trades, load_benchmark, load_dataset, perf, simulate_all

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "horizon_returns.md"
CSV_PATH = MODEL_DIR / "horizon_returns.csv"
WEEKS = [2, 4, 6, 8, 12]
MAX_HOLD = 60  # 12 weeks

# Exits compared on the same entries. Fixed in advance, not tuned to the data.
TRAIL_RULES = {
    "Hold 12 weeks, no stop": bs.ExitRule(max_risk_pct=100, min_risk_pct=100, target_r=0, max_hold=MAX_HOLD),
    "Trailing stop 10%": bs.ExitRule(max_risk_pct=10, min_risk_pct=10, target_r=0, max_hold=MAX_HOLD, trail_pct=10),
    "Trailing stop 15%": bs.ExitRule(max_risk_pct=15, min_risk_pct=15, target_r=0, max_hold=MAX_HOLD, trail_pct=15),
    "Trailing stop 20%": bs.ExitRule(max_risk_pct=20, min_risk_pct=20, target_r=0, max_hold=MAX_HOLD, trail_pct=20),
    "Candle-low stop (2-8%), then trail 15%": bs.ExitRule(target_r=0, max_hold=MAX_HOLD, trail_pct=15),
}


def horizon_rows(signals: pd.DataFrame, paths: dict[int, pd.DataFrame], bench: pd.Series | None) -> pd.DataFrame:
    rows = []
    for _, s in signals[signals["data_status"] == "ok"].iterrows():
        path = paths.get(s["hit_id"])
        if path is None or path.empty:
            continue
        window = bs.entry_window_for(s["scanner_name"])
        entry = bs.find_entry(path["Open"].to_numpy(), path["High"].to_numpy(), s["trigger"], window)
        if entry is None:
            continue
        e_i, e_px = entry
        closes = path["Close"].to_numpy()
        row = {
            "scanner_name": s["scanner_name"], "symbol": s["symbol"], "marketcap": s["marketcap"],
            "sector": s["sector"], "signal_date": s["signal_date"].date(), "trigger": s["trigger"],
            "entry_date": path.index[e_i].date(), "entry_price": e_px,
        }
        bench_start = None
        if bench is not None:
            prior = bench[bench.index < path.index[e_i]]
            bench_start = prior.iloc[-1] if len(prior) else None
        for w in WEEKS:
            j = e_i + 5 * w
            if j >= len(path):
                break  # not enough time has passed yet
            seg = closes[e_i:j + 1]
            row[f"price_{w}w"] = closes[j]
            row[f"ret_{w}w"] = (closes[j] / e_px - 1) * 100
            row[f"best_{w}w"] = (seg.max() / e_px - 1) * 100
            row[f"worst_{w}w"] = (seg.min() / e_px - 1) * 100
            if bench_start is not None:
                b_end = bench[bench.index <= path.index[j]].iloc[-1]
                row[f"nifty500_{w}w"] = (b_end / bench_start - 1) * 100
        rows.append(row)
    return pd.DataFrame(rows)


def summary_table(df: pd.DataFrame) -> list[str]:
    L = ["| Horizon | Trades | Up | Avg | Median | Avg best / worst close | Nifty 500 avg | Beat Nifty 500 |",
         "|---|---|---|---|---|---|---|---|"]
    for w in WEEKS:
        col = f"ret_{w}w"
        if col not in df or df[col].notna().sum() == 0:
            continue
        d = df[df[col].notna()]
        r = d[col]
        nifty = d.get(f"nifty500_{w}w")
        n_txt = f"{nifty.mean():+.1f}%" if nifty is not None else "-"
        beat = f"{(r > nifty).mean():.0%}" if nifty is not None else "-"
        L.append(f"| {w} weeks | {len(d)} | {(r > 0).mean():.0%} | {r.mean():+.1f}% | {r.median():+.1f}% | "
                 f"{d[f'best_{w}w'].mean():+.1f}% / {d[f'worst_{w}w'].mean():+.1f}% | {n_txt} | {beat} |")
    return L


def compare_trailing(signals: pd.DataFrame, paths: dict[int, pd.DataFrame],
                     bench: pd.Series | None) -> dict[str, pd.DataFrame]:
    """Trades per exit rule, restricted to signals with a full 12 weeks of
    prices after the latest possible entry, so every rule is judged on the
    same trades and none is still open."""
    def full_length(row):
        path = paths.get(row["hit_id"])
        return path is not None and len(path) >= bs.entry_window_for(row["scanner_name"]) + MAX_HOLD
    eligible = signals[(signals["data_status"] == "ok") & signals.apply(full_length, axis=1)]
    return {name: add_benchmark(closed_trades(simulate_all(eligible, paths, rule)), bench)
            for name, rule in TRAIL_RULES.items()}


def trailing_section(results: dict[str, pd.DataFrame]) -> list[str]:
    if not results:
        return []
    L = ["", "## Trailing stop vs just holding (up to 12 weeks)", "",
         "Same entries as above. Each trailing stop starts that % below the entry and, after every "
         "close, moves up to that % below the highest close so far (it never moves down). It exits "
         "when a low touches it (at the open on a gap-down), or after 12 weeks at the close. The last "
         "row starts with the tight signal-candle-low stop instead. After 0.25% round-trip costs. "
         "Only signals with a full 12 weeks of prices are used, so every rule is judged on the same trades.", ""]
    for name in sorted(next(iter(results.values()))["scanner_name"].unique()):
        L += [f"### {name}", "",
              "| Exit | Trades | Win rate | Avg return | Median | Avg win / loss | Avg hold (d) | vs Nifty 500 (t) |",
              "|---|---|---|---|---|---|---|---|"]
        for rule_name, trades in results.items():
            g = trades[trades["scanner_name"] == name]
            p = perf(g)
            if not p.get("n"):
                continue
            ex = "-" if np.isnan(p["avg_excess"]) else f"{p['avg_excess']:+.1f}% ({p['t_excess']:+.1f})"
            L.append(f"| {rule_name} | {p['n']} | {p['win_rate']:.0%} | {p['avg_ret']:+.1f}% | "
                     f"{p['median_ret']:+.1f}% | {p['avg_win']:+.1f}% / {p['avg_loss']:+.1f}% | "
                     f"{p['avg_hold']:.0f} | {ex} |")
        L.append("")
    return L


def build_report(df: pd.DataFrame, signals: pd.DataFrame, trailing: dict[str, pd.DataFrame] | None = None) -> str:
    L = [
        "# Price after the trigger: 2 to 12 weeks",
        "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} by `scripts/horizon_returns.py`.",
        "",
        "Buy when price crosses the trigger (the signal candle's high; the completed week's candle for "
        f"`Wkly_upswing`) within {bs.DAILY_ENTRY_WINDOW} sessions ({bs.WEEKLY_ENTRY_WINDOW} for weekly), then just hold. "
        "No stop-loss, no target, no costs deducted. **Up** = share of trades above the entry price at "
        "that point. **Best / worst close** = the highest and lowest close reached at any time up to "
        "that point, averaged across trades. **Beat Nifty 500** = share of trades that did better than "
        "the index over the same days. Recent signals only count for horizons that have fully passed, "
        "so longer horizons have fewer trades and lean towards older signals.",
        "",
        "Per-trade prices: `data/model/horizon_returns.csv`.",
    ]
    for name, g in df.groupby("scanner_name"):
        n_sig = int((signals["scanner_name"] == name).sum())
        L += ["", f"## {name}", "",
              f"{n_sig} signals, {len(g)} crossed the trigger "
              f"({g['signal_date'].min():%d %b %Y} to {g['signal_date'].max():%d %b %Y}).", ""]
        L += summary_table(g)

    # Same window for all three, so the scanners can be compared fairly.
    start = df.loc[df["scanner_name"] != "Wkly_upswing", "signal_date"].min()
    if pd.notna(start):
        common = df[df["signal_date"] >= start]
        L += ["", f"## Side by side, signals since {start:%d %b %Y}", "",
              "Average return / share of trades up, over the same period for every scanner.", "",
              "| Horizon | " + " | ".join(sorted(common["scanner_name"].unique())) + " |",
              "|---|" + "---|" * common["scanner_name"].nunique()]
        for w in WEEKS:
            col = f"ret_{w}w"
            if col not in common:
                continue
            cells = []
            for name in sorted(common["scanner_name"].unique()):
                r = common.loc[common["scanner_name"] == name, col].dropna()
                cells.append(f"{r.mean():+.1f}% / {(r > 0).mean():.0%} (n={len(r)})" if len(r) else "-")
            L.append(f"| {w} weeks | " + " | ".join(cells) + " |")

    L += trailing_section(trailing or {})

    L += ["", "## Reading this", "",
          "- A positive average with a much lower median means a few big winners carry the result; "
          "most individual trades did worse than the average.",
          "- Compare every number with the Nifty 500 column. When the market rises, most stocks rise; "
          "the scanner adds value only if its picks beat the index.",
          "- The gap between the average best close and the final return shows how much of the gain "
          "is given back by holding to a fixed date. That is what a trailing stop or target tries to keep.",
          "- Yahoo prices; symbols it doesn't carry are missing (survivorship bias). Corporate actions "
          "Yahoo hasn't adjusted can show up as false big moves (e.g. TRIVENI, Jul 2026)."]
    return "\n".join(L)


def main() -> int:
    signals, paths = load_dataset()
    bench = load_benchmark()
    bench_series = bench[1] if bench else None
    df = horizon_rows(signals, paths, bench_series)
    if df.empty:
        print("No triggered signals found.")
        return 1
    df.to_csv(CSV_PATH, index=False, float_format="%.2f")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    trailing = compare_trailing(signals, paths, bench_series)
    REPORT_PATH.write_text(build_report(df, signals, trailing), encoding="utf-8")
    print(f"Wrote {CSV_PATH} ({len(df)} trades) and {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
