"""Where was each scanner stock 2, 4, 6, 8 and 12 weeks after it crossed
the trigger price? Plain buy-and-hold from the trigger: no stop, no target.

For every backtest hit (data/model/signals.csv + paths.csv.gz, built by
build_dataset.py):
- entry = first session within the entry window whose high crosses the
  trigger (signal candle high), filled at the trigger or the open on a gap-up
- price N weeks later = close 5*N sessions after the entry session
- also the best and worst close reached within each horizon, and the
  Nifty 500's move over the same days

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
from signal_model import MODEL_DIR, load_benchmark, load_dataset

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "horizon_returns.md"
CSV_PATH = MODEL_DIR / "horizon_returns.csv"
WEEKS = [2, 4, 6, 8, 12]


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


def build_report(df: pd.DataFrame, signals: pd.DataFrame) -> str:
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
    df = horizon_rows(signals, paths, bench[1] if bench else None)
    if df.empty:
        print("No triggered signals found.")
        return 1
    df.to_csv(CSV_PATH, index=False, float_format="%.2f")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(df, signals), encoding="utf-8")
    print(f"Wrote {CSV_PATH} ({len(df)} trades) and {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
