"""Evaluate "buy when it crosses the trigger price" on each scanner's
history, train a model that filters the signals, and score new scanner
results.

  python signal_model.py train
      Needs data/model/signals.csv + paths.csv.gz (build_dataset.py).
      Simulates every historical signal with breakout_sim's rule, reports
      raw per-scanner performance, walk-forward-validates a classifier that
      predicts whether a triggered trade ends in profit, and saves it to
      data/model/signal_model.pkl. Report: reports/signal_model_report.md.

  python signal_model.py predict --input results.csv [--scanner NAME] [--date DD-MM-YYYY]
  python signal_model.py predict --from-db
  python signal_model.py predict --symbols KSB,ACI --scanner 63_30_daily
      Scores today's scanner results (a Chartink CSV export, same columns
      as data/backtest/*.csv; the scanner comes from --scanner or the file
      name) and prints BUY / SKIP with trigger, stop and target levels.
      Fetches recent prices, so it also needs internet (GitHub Actions).
"""

from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import breakout_sim as bs

ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT / "data" / "model"
MODEL_PATH = MODEL_DIR / "signal_model.pkl"
META_PATH = MODEL_DIR / "signal_model.json"
REPORT_PATH = ROOT / "reports" / "signal_model_report.md"
PREDICTIONS_PATH = ROOT / "reports" / "latest_signals.csv"

MIN_TRAIN_TRADES = 150   # walk-forward starts once this many trades have closed
MIN_AUC = 0.55           # below this walk-forward AUC the model is not used to filter
BENCHMARKS = ["^CRSLDX", "^NSEI"]  # Nifty 500, falling back to Nifty 50

# Exit rules compared side by side in the report. Fixed in advance, not tuned.
COMPARE_RULES = {
    "Candle-low stop, 2R target, 20d": bs.ExitRule(),
    "Candle-low stop, no target, 20d": bs.ExitRule(target_r=0),
    "Wide stop (≤15%), no target, 20d": bs.ExitRule(max_risk_pct=15, target_r=0),
    "No stop, exit after 10d": bs.ExitRule(max_risk_pct=100, min_risk_pct=100, target_r=0, max_hold=10),
    "No stop, exit after 20d": bs.ExitRule(max_risk_pct=100, min_risk_pct=100, target_r=0, max_hold=20),
}
MODEL_CATEGORICALS = ["scanner_name", "marketcap"]  # sector: too many levels for this sample size


# ---------------------------------------------------------------------------
# Dataset -> trades
# ---------------------------------------------------------------------------

def load_dataset() -> tuple[pd.DataFrame, dict[int, pd.DataFrame]]:
    signals = pd.read_csv(MODEL_DIR / "signals.csv", parse_dates=["hit_date", "signal_date"])
    paths = pd.read_csv(MODEL_DIR / "paths.csv.gz", parse_dates=["date"])
    by_hit = {
        hit_id: g.sort_values("offset").set_index("date")
                 .rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close"})
        for hit_id, g in paths.groupby("hit_id")
    }
    return signals, by_hit


def load_benchmark() -> tuple[str, pd.Series] | None:
    path = MODEL_DIR / "index_closes.csv"
    if not path.exists():
        return None
    idx = pd.read_csv(path, parse_dates=["date"], index_col="date")
    for t in BENCHMARKS:
        if t in idx and idx[t].notna().sum() > 100:
            return {"^CRSLDX": "Nifty 500", "^NSEI": "Nifty 50"}[t], idx[t].dropna()
    return None


def add_benchmark(trades: pd.DataFrame, bench: pd.Series | None) -> pd.DataFrame:
    """Index return from the close before entry to the exit-day close, and
    the trade's return in excess of it: did the scanner beat just holding
    the market over the same days?"""
    if bench is None or trades.empty:
        return trades
    before = bench.reindex(trades["entry_date"] - pd.Timedelta(days=1), method="ffill").to_numpy()
    after = bench.reindex(trades["exit_date"], method="ffill").to_numpy()
    trades = trades.copy()
    trades["bench_ret"] = (after / before - 1) * 100
    trades["excess_pct"] = trades["ret_pct"] - trades["bench_ret"]
    return trades


def simulate_all(signals: pd.DataFrame, paths: dict[int, pd.DataFrame],
                 rule: bs.ExitRule = bs.DEFAULT_RULE) -> pd.DataFrame:
    rows = []
    empty = pd.DataFrame(columns=["Open", "High", "Low", "Close"])
    for _, s in signals[signals["data_status"] == "ok"].iterrows():
        path = paths.get(s["hit_id"], empty)
        res = bs.simulate_trade(path, s["trigger"], s["bar_low"], bs.entry_window_for(s["scanner_name"]), rule)
        if "entry_offset" in res:
            res["entry_date"] = path.index[res["entry_offset"]]
            res["exit_date"] = path.index[res["exit_offset"]]
        rows.append({**s.to_dict(), **res})
    return pd.DataFrame(rows)


def closed_trades(sim: pd.DataFrame) -> pd.DataFrame:
    t = sim[sim["status"] == "triggered"].copy()
    t["win"] = (t["ret_pct"] > 0).astype(int)
    return t.sort_values("signal_date").reset_index(drop=True)


def perf(trades: pd.DataFrame) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0}
    r = trades["ret_pct"]
    gains, losses = r[r > 0].sum(), -r[r <= 0].sum()
    return {
        "n": n,
        "win_rate": float((r > 0).mean()),
        "avg_ret": float(r.mean()),
        "median_ret": float(r.median()),
        "avg_win": float(r[r > 0].mean()) if (r > 0).any() else 0.0,
        "avg_loss": float(r[r <= 0].mean()) if (r <= 0).any() else 0.0,
        "profit_factor": float(gains / losses) if losses > 0 else math.inf,
        "avg_r": float(trades["r_multiple"].mean()),
        "avg_hold": float(trades["hold_days"].mean()),
        "t_stat": _t(r),
        "avg_excess": float(trades["excess_pct"].mean()) if "excess_pct" in trades else float("nan"),
        "t_excess": _t(trades["excess_pct"].dropna()) if "excess_pct" in trades else float("nan"),
    }


def _t(x: pd.Series) -> float:
    n = len(x)
    return float(x.mean() / (x.std(ddof=1) / math.sqrt(n))) if n > 2 and x.std() > 0 else 0.0


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------

def make_model(kind: str):
    num = bs.FEATURE_COLUMNS
    if kind == "logreg":
        pre = ColumnTransformer([
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num),
            ("cat", OneHotEncoder(handle_unknown="ignore"), MODEL_CATEGORICALS),
        ])
        return make_pipeline(pre, LogisticRegression(C=0.1, max_iter=2000))
    pre = ColumnTransformer([
        ("num", "passthrough", num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), MODEL_CATEGORICALS),
    ])
    return make_pipeline(pre, HistGradientBoostingClassifier(
        max_depth=3, learning_rate=0.05, max_iter=150, min_samples_leaf=25,
        l2_regularization=1.0, random_state=0))


def walk_forward(trades: pd.DataFrame, kind: str) -> pd.Series:
    """Out-of-sample probability for each trade. Each calendar month is
    scored by a model trained only on trades that had already *closed*
    before that month began, so no outcome leaks into its own prediction."""
    proba = pd.Series(np.nan, index=trades.index)
    months = trades["signal_date"].dt.to_period("M")
    for m in sorted(months.unique()):
        month_start = m.start_time
        train = trades[trades["exit_date"] < month_start]
        test_idx = trades.index[months == m]
        if len(train) < MIN_TRAIN_TRADES or train["win"].nunique() < 2:
            continue
        model = make_model(kind).fit(train[bs.FEATURE_COLUMNS + MODEL_CATEGORICALS], train["win"])
        proba[test_idx] = model.predict_proba(trades.loc[test_idx, bs.FEATURE_COLUMNS + MODEL_CATEGORICALS])[:, 1]
    return proba


def pick_threshold(trades: pd.DataFrame, proba: pd.Series) -> float | None:
    """Probability cut-off chosen on the walk-forward predictions: the one
    that maximizes total return while keeping at least a third of the
    scored trades (so it can't be a handful of lucky picks). None if no
    cut-off beats taking every trade."""
    scored = trades.assign(p=proba).dropna(subset=["p"])
    best_t, best_total = None, scored["ret_pct"].sum()
    for t in np.round(np.arange(0.30, 0.71, 0.025), 3):
        sel = scored[scored["p"] >= t]
        if len(sel) < len(scored) / 3:
            break
        if sel["ret_pct"].sum() > best_total:
            best_t, best_total = float(t), sel["ret_pct"].sum()
    return best_t


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _fmt_perf(label: str, p: dict) -> str:
    if p.get("n", 0) == 0:
        return f"| {label} | 0 | - | - | - | - | - | - | - | - |"
    pf = "∞" if math.isinf(p["profit_factor"]) else f"{p['profit_factor']:.2f}"
    ex = "-" if math.isnan(p["avg_excess"]) else f"{p['avg_excess']:+.2f}% (t {p['t_excess']:+.1f})"
    return (f"| {label} | {p['n']} | {p['win_rate']:.0%} | {p['avg_ret']:+.2f}% | "
            f"{p['avg_win']:+.2f}% / {p['avg_loss']:+.2f}% | {pf} | {p['avg_r']:+.2f} | "
            f"{p['avg_hold']:.1f} | {p['t_stat']:+.1f} | {ex} |")


PERF_HEADER = [
    "| Group | Trades | Win rate | Avg return | Avg win / loss | Profit factor | Avg R | Avg hold (d) | t-stat | vs index |",
    "|---|---|---|---|---|---|---|---|---|---|",
]


def build_report(sim: pd.DataFrame, trades: pd.DataFrame, oos: pd.DataFrame, meta: dict,
                 signals: pd.DataFrame, rule: bs.ExitRule) -> str:
    L = [
        "# Scanner signal model report",
        "",
        f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} by `scripts/signal_model.py train`.",
        "",
        "## The rule being tested",
        "",
        "- **Trigger price** = high of the signal candle (the day's candle for the daily scanners, "
        "the completed week's candle for `Wkly_upswing`).",
        f"- **Entry**: buy-stop at the trigger, valid for {bs.DAILY_ENTRY_WINDOW} sessions after a daily signal "
        f"({bs.WEEKLY_ENTRY_WINDOW} after a weekly one). Filled at the trigger, or at the open on a gap-up.",
        f"- **Stop** = signal candle low, kept between {rule.min_risk_pct:g}% and {rule.max_risk_pct:g}% below entry. "
        f"**Target** = {rule.target_r:g}× that risk. Otherwise exit at the close after {rule.max_hold} sessions.",
        "- Stop assumed hit first when a candle touches both levels, including on the entry day.",
        f"- Returns are after {bs.COST_PCT}% round-trip costs. A win = return > 0.",
        "",
        "## Data coverage",
        "",
        "| Scanner | Hits | With prices | Triggered & closed | Not triggered | Still open / pending |",
        "|---|---|---|---|---|---|",
    ]
    for name, g in signals.groupby("scanner_name"):
        s = sim[sim["scanner_name"] == name]
        L.append(f"| {name} | {len(g)} | {int((g['data_status'] == 'ok').sum())} | "
                 f"{int((s['status'] == 'triggered').sum())} | {int((s['status'] == 'not_triggered').sum())} | "
                 f"{int((s['status'] == 'pending').sum())} |")
    missing = sorted(signals.loc[signals["data_status"] == "no_price_data", "symbol"].unique())
    if missing:
        L += ["", f"No Yahoo price data for {len(missing)} symbols (renamed/delisted/unsupported ticker), "
                  f"skipped: {', '.join(missing[:40])}{' …' if len(missing) > 40 else ''}"]

    bench_name = meta.get("benchmark") or "index"
    L += ["", "## 1. Does buying every trigger make money?", ""] + PERF_HEADER
    for name, g in trades.groupby("scanner_name"):
        L.append(_fmt_perf(name, perf(g)))
    L.append(_fmt_perf("**All scanners**", perf(trades)))
    L += ["", "t-stat: average return divided by its standard error; below ~2 the average could "
              f"easily be noise. **vs index**: average return minus what the {bench_name} did over the "
              "same days. A scanner that only matches the index adds nothing over buying an index fund.", ""]

    L += ["### By market-cap tier", ""] + PERF_HEADER
    for (name, cap), g in trades.groupby(["scanner_name", "marketcap"]):
        L.append(_fmt_perf(f"{name} · {cap}", perf(g)))

    L += ["", "### By market regime at signal time (Nifty vs its 50-day average)", ""] + PERF_HEADER
    regime = np.where(trades["nifty_dist_sma50"] > 0, "Nifty above 50DMA", "Nifty below 50DMA")
    for (name, reg), g in trades.groupby([trades["scanner_name"], regime]):
        L.append(_fmt_perf(f"{name} · {reg}", perf(g)))

    L += ["", "### Exit reasons", "", "| Scanner | Target | Stop | Time exit |", "|---|---|---|---|"]
    for name, g in trades.groupby("scanner_name"):
        reason = g["exit_reason"].str.replace("_gap", "")
        L.append(f"| {name} | {(reason == 'target').mean():.0%} | {(reason == 'stop').mean():.0%} | "
                 f"{(reason == 'time').mean():.0%} |")

    if meta.get("rule_comparison"):
        L += ["", "### Other exit rules (same entries)", "",
              "Fixed set of alternatives, not optimized. Cells: trades · avg return · vs index (t-stat of the excess).", "",
              "| Exit rule | " + " | ".join(sorted(trades["scanner_name"].unique())) + " |",
              "|---|" + "---|" * trades["scanner_name"].nunique()]
        for rule_name, per in meta["rule_comparison"].items():
            cells = []
            for name in sorted(trades["scanner_name"].unique()):
                p = per.get(name, {"n": 0})
                if not p.get("n"):
                    cells.append("-")
                    continue
                ex = "" if math.isnan(p["avg_excess"]) else f" · {p['avg_excess']:+.2f}% (t {p['t_excess']:+.1f})"
                cells.append(f"{p['n']} · {p['avg_ret']:+.2f}%{ex}")
            L.append(f"| {rule_name} | " + " | ".join(cells) + " |")

    L += ["", "## 2. Model: which triggers to take", ""]
    if oos.empty:
        L.append(f"Not enough closed trades to walk-forward validate (need {MIN_TRAIN_TRADES}).")
    else:
        L += [
            f"Model: `{meta['model_kind']}` predicting P(trade ends in profit) from price/volume "
            "features at the signal candle, market regime, repeat/confluence counts, scanner and "
            "market-cap tier. Validated **walk-forward**: each month is scored by a model trained only "
            "on trades that had closed before that month, so these are honest out-of-sample numbers "
            f"({len(oos)} scored trades from {oos['signal_date'].min():%b %Y}).",
            "",
            f"- Walk-forward ROC-AUC: logistic regression {meta['auc']['logreg']:.2f}, "
            f"gradient boosting {meta['auc']['hgb']:.2f} (0.50 = coin flip; the filter is only "
            f"switched on at ≥ {MIN_AUC}).",
        ]
        if meta["validated"]:
            t = meta["threshold"]
            L += [f"- **Validated.** BUY threshold: P(profit) ≥ {t:.3f}", "", *PERF_HEADER,
                  _fmt_perf("All scored trades (no filter)", perf(oos)),
                  _fmt_perf("Model says BUY", perf(oos[oos["p"] >= t])),
                  _fmt_perf("Model says SKIP", perf(oos[oos["p"] < t]))]
            for name, g in oos.groupby("scanner_name"):
                L.append(_fmt_perf(f"{name} · BUY", perf(g[g["p"] >= t])))
                L.append(_fmt_perf(f"{name} · SKIP", perf(g[g["p"] < t])))
        else:
            L += ["- **Not validated: the model could not tell winning triggers from losing ones "
                  "out of sample**, so it is *not* used to filter. `predict` lists every setup with its "
                  "levels and says the filter is off. Training re-checks this every run, so the filter "
                  "switches itself on if enough new history makes it work."]
        L += ["", "### Out-of-sample return by probability quintile", "",
              "| Quintile | P(profit) range | Trades | Win rate | Avg return |", "|---|---|---|---|---|"]
        q = pd.qcut(oos["p"].rank(method="first"), 5, labels=[f"Q{i}" for i in range(1, 6)])
        for label, g in oos.groupby(q, observed=True):
            L.append(f"| {label} | {g['p'].min():.2f}–{g['p'].max():.2f} | {len(g)} | "
                     f"{(g['ret_pct'] > 0).mean():.0%} | {g['ret_pct'].mean():+.2f}% |")
        L += ["", "Returns should rise steadily from Q1 to Q5 if the model has found something real. "
                  "When validated, the threshold is picked on these same predictions, so the BUY row "
                  "is slightly optimistic; the quintiles are the fairer check."]

    L += ["", "## Caveats", "",
          "- Only ~8 months of history for the two daily scanners, all in one market phase. "
          "Treat every number here as provisional and re-run training as more signals accumulate.",
          "- Yahoo Finance data: symbols it doesn't carry are skipped (survivorship bias), and "
          "daily candles can't tell whether the stop or the target came first inside a day "
          "(handled pessimistically).",
          "- Chartink's backtest list is the scanner's output as of today's definition; if the "
          "scan was edited, past hits reflect the new version, not what you would have seen live.",
          "- Not investment advice. Size positions so a stop-out costs a small, fixed fraction of capital."]
    return "\n".join(L)


def train() -> int:
    rule = bs.DEFAULT_RULE
    signals, paths = load_dataset()
    bench = load_benchmark()
    bench_name, bench_series = bench if bench else (None, None)
    sim = simulate_all(signals, paths, rule)
    trades = add_benchmark(closed_trades(sim), bench_series)
    print(f"{len(signals)} signals -> {len(trades)} closed trades")

    rule_comparison = {}
    for rule_name, alt in COMPARE_RULES.items():
        alt_trades = add_benchmark(closed_trades(simulate_all(signals, paths, alt)), bench_series)
        rule_comparison[rule_name] = {name: perf(g) for name, g in alt_trades.groupby("scanner_name")}

    aucs, probas = {}, {}
    for kind in ("logreg", "hgb"):
        probas[kind] = walk_forward(trades, kind)
        scored = probas[kind].notna()
        aucs[kind] = (roc_auc_score(trades.loc[scored, "win"], probas[kind][scored])
                      if scored.sum() > 20 and trades.loc[scored, "win"].nunique() == 2 else float("nan"))
        print(f"  walk-forward AUC {kind}: {aucs[kind]:.3f} on {int(scored.sum())} trades")

    kind = max(aucs, key=lambda k: -1 if math.isnan(aucs[k]) else aucs[k])
    oos = trades.assign(p=probas[kind]).dropna(subset=["p"])
    threshold = pick_threshold(trades, probas[kind]) if not oos.empty else None
    validated = bool(threshold is not None and aucs[kind] >= MIN_AUC)
    print(f"  model {kind}: {'validated' if validated else 'NOT validated'} (threshold {threshold})")

    meta = {
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model_kind": kind,
        "auc": aucs,
        "validated": validated,
        "threshold": threshold if validated else None,
        "benchmark": bench_name,
        "train_trades": len(trades),
        "rule": rule.__dict__,
        "entry_window": {"daily": bs.DAILY_ENTRY_WINDOW, "weekly": bs.WEEKLY_ENTRY_WINDOW},
        "features": bs.FEATURE_COLUMNS + MODEL_CATEGORICALS,
        "raw_performance": {name: perf(g) for name, g in trades.groupby("scanner_name")},
        "rule_comparison": rule_comparison,
        "oos_buy_performance": perf(oos[oos["p"] >= threshold]) if validated else {},
    }
    final = make_model(kind).fit(trades[bs.FEATURE_COLUMNS + MODEL_CATEGORICALS], trades["win"])
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_bytes(pickle.dumps(final))
    META_PATH.write_text(json.dumps(meta, indent=2, default=str))
    sim = sim.merge(trades[["hit_id", "bench_ret", "excess_pct"]], on="hit_id", how="left") \
        if "excess_pct" in trades else sim
    sim_cols = ["scanner_name", "hit_date", "symbol", "signal_date", "status", "trigger", "entry_date",
                "entry_price", "stop", "target", "exit_date", "exit_price", "exit_reason", "ret_pct",
                "r_multiple", "bench_ret", "excess_pct"]
    sim[[c for c in sim_cols if c in sim]].to_csv(MODEL_DIR / "trades.csv", index=False, float_format="%.3f")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(sim, trades, oos, meta, signals, rule), encoding="utf-8")
    print(f"Wrote {REPORT_PATH}, {MODEL_PATH}")
    return 0


# ---------------------------------------------------------------------------
# Predict
# ---------------------------------------------------------------------------

def _read_input(path: Path, scanner: str | None, date: str | None) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame({
        "symbol": df["Symbol"].astype(str).str.strip().str.upper(),
        "marketcap": df.get("Marketcapname", pd.Series("", index=df.index)).fillna("").astype(str),
        "sector": df.get("Sector", pd.Series("", index=df.index)).fillna("").astype(str),
    })
    if "Date" in df.columns and date is None:
        out["hit_date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    else:
        out["hit_date"] = pd.to_datetime(date, format="%d-%m-%Y") if date else pd.NaT
    out["scanner_name"] = scanner or path.stem
    if out["scanner_name"].iloc[0] not in _known_scanners():
        print(f"WARNING: scanner '{out['scanner_name'].iloc[0]}' wasn't in the training data; "
              "pass --scanner with one of: " + ", ".join(sorted(_known_scanners())))
    return out


def _known_scanners() -> set[str]:
    return {p.stem for p in (ROOT / "data" / "backtest").glob("*.csv")}


def _backtest_metadata() -> dict[str, tuple[str, str]]:
    """symbol -> (market-cap tier, sector) from the latest backtest row."""
    from build_dataset import load_hits
    hits = load_hits().sort_values("hit_date")
    return {r.symbol: (r.marketcap, r.sector) for r in hits.itertuples()}


def _latest_db_scan() -> pd.DataFrame:
    import db
    conn = db.connect()
    run_id = conn.execute("SELECT MAX(id) FROM runs").fetchone()[0]
    rows = conn.execute("SELECT scanner_name, symbol FROM results WHERE run_id = ?", (run_id,)).fetchall()
    conn.close()
    meta = _backtest_metadata()
    return pd.DataFrame([{"scanner_name": s, "symbol": sym, "hit_date": pd.NaT,
                          "marketcap": meta.get(sym, ("", ""))[0],
                          "sector": meta.get(sym, ("", ""))[1]} for s, sym in rows])


def score_signals(new: pd.DataFrame, prices: dict[str, pd.DataFrame], nifty: pd.DataFrame | None) -> pd.DataFrame:
    """Levels + P(profit) + action for each new scanner result. A blank
    hit_date means "latest session in the price data". Action is BUY/SKIP
    when the model passed walk-forward validation; otherwise every valid
    setup is SETUP (the filter is off), since an unvalidated probability
    shouldn't decide anything."""
    from build_dataset import load_hits

    model = pickle.loads(MODEL_PATH.read_bytes())
    meta = json.loads(META_PATH.read_text())
    rule = bs.ExitRule(**meta["rule"])

    rows = []
    for _, r in new.iterrows():
        out = r.to_dict()
        df = prices.get(r["symbol"])
        if df is None or df.empty:
            rows.append({**out, "action": "NO DATA"})
            continue
        hit_date = r["hit_date"] if pd.notna(r["hit_date"]) else df.index[-1]
        weekly = bs.is_weekly(r["scanner_name"])
        if not weekly and hit_date not in df.index:
            hit_date = df.index[df.index <= hit_date][-1]
        sig = bs.signal_bar(df, hit_date, weekly, require_complete=False)
        if sig is None:
            rows.append({**out, "action": "NO DATA"})
            continue
        feats = bs.indicator_frame(df).iloc[sig["end_pos"]].to_dict()
        feats.update(bs.bar_features(sig))
        feats.update(bs.market_features(nifty, sig["signal_date"]))
        stop, target = bs.stop_and_target(sig["trigger"], sig["bar_low"], rule)
        after = df.iloc[sig["end_pos"] + 1:]
        out.update(feats, hit_date=hit_date, signal_date=sig["signal_date"], trigger=sig["trigger"],
                   stop=stop, target=target, last_close=float(df["Close"].iloc[-1]),
                   sessions_since=len(after), crossed=bool((after["High"] > sig["trigger"]).any()))
        rows.append(out)

    res = pd.DataFrame(rows)
    ok = res["trigger"].notna() if "trigger" in res else pd.Series(False, index=res.index)
    if ok.any():
        hist = load_hits()
        hist["signal_date"] = hist.apply(
            lambda h: h["hit_date"] + pd.Timedelta(days=4 - h["hit_date"].weekday())
            if bs.is_weekly(h["scanner_name"]) else h["hit_date"], axis=1)
        combined = pd.concat([hist, res.loc[ok, ["scanner_name", "symbol", "signal_date"]]], keys=["h", "n"])
        counts = bs.history_features(combined.reset_index(drop=True)).iloc[len(hist):]
        counts.index = res.index[ok]
        res.loc[ok, counts.columns] = counts
        X = res.loc[ok, bs.FEATURE_COLUMNS + MODEL_CATEGORICALS].copy()
        X[bs.FEATURE_COLUMNS] = X[bs.FEATURE_COLUMNS].astype(float)
        res.loc[ok, "p_profit"] = model.predict_proba(X)[:, 1]
        if meta.get("validated"):
            res.loc[ok, "action"] = np.where(res.loc[ok, "p_profit"] >= meta["threshold"], "BUY", "SKIP")
        else:
            res.loc[ok, "action"] = "SETUP"
        window = res["scanner_name"].map(bs.entry_window_for)
        res.loc[ok & res["crossed"].astype(bool), "action"] = "TRIGGERED"  # stop-buy already filled
        res.loc[ok & ~res["crossed"].astype(bool) & (res["sessions_since"] >= window), "action"] = "EXPIRED"
        res.loc[ok & (res["last_close"] > res["target"]), "action"] = "MISSED"  # ran past the target
    return res


def format_predictions(res: pd.DataFrame, window: dict) -> str:
    lines = []
    for action in ("BUY", "SETUP", "SKIP", "TRIGGERED", "MISSED", "EXPIRED", "NO DATA"):
        g = res[res["action"] == action]
        if g.empty:
            continue
        lines.append(f"{action} ({len(g)})")
        for _, r in g.sort_values("p_profit", ascending=False, na_position="last").iterrows():
            if action in ("NO DATA", "EXPIRED"):
                lines.append(f"  {r['symbol']:<12} [{r['scanner_name']}]")
                continue
            w = window["weekly" if bs.is_weekly(r["scanner_name"]) else "daily"]
            lines.append(f"  {r['symbol']:<12} P={r['p_profit']:.2f}  buy above {r['trigger']:.2f}  "
                         f"SL {r['stop']:.2f}  TGT {r['target']:.2f}  (valid {w} sessions after "
                         f"{pd.Timestamp(r['signal_date']):%d-%b}) [{r['scanner_name']}]")
    return "\n".join(lines)


def predict(args) -> int:
    from market_data import NIFTY_TICKER, fetch_daily

    if args.from_db:
        new = _latest_db_scan()
    elif args.symbols:
        if not args.scanner:
            print("--symbols needs --scanner (one of: " + ", ".join(sorted(_known_scanners())) + ")")
            return 2
        syms = [x.strip().upper() for x in args.symbols.replace(" ", ",").split(",") if x.strip()]
        hit = pd.to_datetime(args.date, format="%d-%m-%Y") if args.date else pd.NaT
        meta_lookup = _backtest_metadata()
        new = pd.DataFrame([{"scanner_name": args.scanner, "symbol": x, "hit_date": hit,
                             "marketcap": meta_lookup.get(x, ("", ""))[0],
                             "sector": meta_lookup.get(x, ("", ""))[1]} for x in syms])
    else:
        new = pd.concat([_read_input(Path(p), args.scanner, args.date) for p in args.input], ignore_index=True)
    if new.empty:
        print("No scanner results to score.")
        return 1
    start = (datetime.now() - timedelta(days=420)).date().isoformat()
    prices = fetch_daily(sorted(new["symbol"].unique()), start)
    nifty = fetch_daily([NIFTY_TICKER], start).get(NIFTY_TICKER)
    res = score_signals(new, prices, nifty)
    meta = json.loads(META_PATH.read_text())
    header = (f"Model filter ON: BUY = P(profit) >= {meta['threshold']:.2f} (walk-forward validated)"
              if meta.get("validated") else
              "Model filter OFF: it did not beat taking every trigger in walk-forward testing, so all "
              "setups are listed. P is shown for information only.")
    text = format_predictions(res, meta["entry_window"])
    print(header + "\n\n" + text)
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    cols = ["scanner_name", "symbol", "signal_date", "action", "p_profit", "trigger", "stop", "target",
            "last_close", "marketcap", "sector"]
    res[[c for c in cols if c in res]].to_csv(PREDICTIONS_PATH, index=False, float_format="%.3f")
    print(f"\nSaved {PREDICTIONS_PATH}")
    if args.telegram:
        import html
        from notify import send_telegram_message
        send_telegram_message(f"<b>🎯 Scanner setups</b>\n{html.escape(header)}\n\n<pre>{html.escape(text)}</pre>")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("train")
    p = sub.add_parser("predict")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", nargs="+", help="Chartink CSV export(s) of today's results")
    src.add_argument("--from-db", action="store_true", help="score the latest scraped run in data/chartink.db")
    src.add_argument("--symbols", help="comma-separated symbols (needs --scanner)")
    p.add_argument("--scanner", help="scanner name (for --symbols, or if it isn't the CSV's file name)")
    p.add_argument("--date", help="signal date DD-MM-YYYY if the CSV has no Date column (default: latest session)")
    p.add_argument("--telegram", action="store_true", help="also send the list to Telegram")
    args = ap.parse_args()
    return train() if args.cmd == "train" else predict(args)


if __name__ == "__main__":
    sys.exit(main())
