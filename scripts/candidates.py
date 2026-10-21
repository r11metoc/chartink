"""Compare a changed scanner (a new Chartink backtest export) with the current one.

Drop the export into data/backtest/candidates/<scanner>__<label>.csv, e.g.
63_30_daily__new_2026-10-21.csv. The bot itself never reads this folder, so
nothing live changes. The weekly report (stock_outcomes.py) then tests the
candidate and the current version over the same dates with:
- the live buy-the-dip rule (dipzone.py), and
- buy and hold for 1 month / 6 months / 1 year.
If the candidate wins, move it to data/backtest/<scanner>.csv and change the
scanner on Chartink.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone

ROOT = Path(__file__).resolve().parent.parent
CAND_DIR = ROOT / "data" / "backtest" / "candidates"
HOLD = {"1 month": 21, "6 months": 126, "1 year": 252}


def load(path: Path) -> pd.DataFrame:
    scanner, label = path.stem.split("__", 1) if "__" in path.stem else (path.stem, "candidate")
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = [{"scanner_name": scanner, "label": label, "symbol": r["Symbol"].strip().upper(),
                 "hit_date": pd.to_datetime(r["Date"], format="%d-%m-%Y"),
                 "marketcap": r.get("Marketcapname", "").strip()} for r in csv.DictReader(f)]
    return pd.DataFrame(rows)


def candidate_hits() -> pd.DataFrame:
    files = sorted(CAND_DIR.glob("*.csv")) if CAND_DIR.exists() else []
    return pd.concat([load(p) for p in files], ignore_index=True) if files else pd.DataFrame()


def evaluate(hits: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], bs.is_weekly(h["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        fwd = df.iloc[sig["end_pos"] + 1:]
        row = {"label": h["label"], "marketcap": h["marketcap"], "year": h["hit_date"].year}
        s = dipzone.simulate(fwd, sig["trigger"], h["scanner_name"])
        if s["status"] in ("target", "stop", "time"):
            row["dip_ret"] = s["ret"]
        c = fwd["Close"].to_numpy(dtype=float)
        e = bs.find_entry(fwd["Open"].to_numpy(dtype=float), fwd["High"].to_numpy(dtype=float), sig["trigger"],
                          bs.entry_window_for(h["scanner_name"]))
        if e is not None:
            for name, n in HOLD.items():
                if e[0] + n < len(c):
                    row[name] = (c[e[0] + n] / e[1] - 1) * 100
        rows.append(row)
    return pd.DataFrame(rows)


def _p(x) -> str:
    return "–" if pd.isna(x) else f"{x:+.1f}%"


def section(current: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> list[str]:
    cand = candidate_hits()
    if cand.empty:
        return []
    L = ["", "## Candidate scanner versions", "",
         "A new Chartink export in `data/backtest/candidates/` compared with the scanner the bot uses now, "
         "over the same dates. The bot does not use the candidate until it is moved to `data/backtest/`.", ""]
    for (scanner, label), c in cand.groupby(["scanner_name", "label"]):
        lo, hi = c["hit_date"].min(), c["hit_date"].max()
        cur = current[(current["scanner_name"] == scanner) & current["hit_date"].between(lo, hi)].copy()
        cur["label"] = "current"
        both = pd.concat([cur[["scanner_name", "label", "symbol", "hit_date", "marketcap"]], c], ignore_index=True)
        ev = evaluate(both, prices)
        if ev.empty:
            continue
        yrs = max((hi - lo).days / 365, 0.1)
        L += [f"### {scanner}: current vs {label} ({lo:%d %b %Y} to {hi:%d %b %Y})", "",
              "| Version | Signals | Signals a year | Dip rule trades | Dip win rate | Dip avg | Dip total (₹1L a trade) | "
              "Hold 1 month | Hold 6 months | Hold 1 year (median) |", "|---|---|---|---|---|---|---|---|---|---|"]
        for lab in ("current", label):
            n_sig = len(cur) if lab == "current" else len(c)
            x = ev[ev["label"] == lab]
            dr = x["dip_ret"].dropna() if "dip_ret" in x else pd.Series(dtype=float)
            hold = {k: x[k].dropna() if k in x else pd.Series(dtype=float) for k in HOLD}
            L.append(f"| {lab} | {n_sig} | {n_sig / yrs:.0f} | {len(dr)} | "
                     f"{(dr > 0).mean():.0%} | {_p(dr.mean())} | {dr.sum() * 1000:,.0f} | "
                     f"{_p(hold['1 month'].mean())} | {_p(hold['6 months'].mean())} | "
                     f"{_p(hold['1 year'].mean())} ({_p(hold['1 year'].median())}) |" if len(dr) else f"| {lab} | {n_sig} | – |")
        L += ["", "| Version | Year | Dip trades | Dip win rate | Dip avg |", "|---|---|---|---|---|"]
        for (lab, yr), x in ev.dropna(subset=["dip_ret"]).groupby(["label", "year"]):
            L.append(f"| {lab} | {yr} | {len(x)} | {(x['dip_ret'] > 0).mean():.0%} | {_p(x['dip_ret'].mean())} |")
        L += ["", "| Version | Cap | Dip trades | Dip win rate | Dip avg |", "|---|---|---|---|---|"]
        for (lab, cap), x in ev.dropna(subset=["dip_ret"]).groupby(["label", "marketcap"]):
            L.append(f"| {lab} | {cap or 'Unknown'} | {len(x)} | {(x['dip_ret'] > 0).mean():.0%} | {_p(x['dip_ret'].mean())} |")
    return L
