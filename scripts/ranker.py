"""ML signal ranker: which signals get the free slots.

The rule takes far more signals than 15 slots can hold (the backtest bought
about 1 in 8), so on a day with more buys than free slots the order matters.
The fixed order is mid caps, then large, then small. The ranker replaces that
order only after it has proved itself on years it never saw:

- **Model**: logistic regression on 25 facts known at the signal close
  (returns over 1/5/20/60 days, distance from the 20/50/200-day averages and
  the 52-week high, RSI, ATR, volume vs its average, turnover, the signal
  candle's shape, the Nifty's last 20 days, scanner, market cap). Simple on
  purpose: gradient-boosted trees did worse out of sample (13 Nov 2026 test).
- **Label**: did the trade make money under the live rule.
- **Walk-forward**: each year is scored by a model trained only on trades
  that had closed before 1 January of that year.
- **Gate** (switched on only if all hold): the ₹10L/15-slot portfolio ranked
  by the model beats the fixed order in the first half and the second half of
  the test years, its worst fall is no more than 1 point worse, and the
  model's top half beat its bottom half in at least two thirds of the years.

Retrained every Saturday (stock_outcomes.py). The model is stored as plain
numbers in data/model/ranker.json, so scoring needs only numpy.
It never adds or skips a trade: the rule decides what to buy; the ranker only
decides who gets a slot first.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT / "data" / "model" / "ranker.json"

SCANNERS = ["63_30_daily", "Bullish_Scanner", "Wkly_upswing"]
CAPS = ["Largecap", "Midcap", "Smallcap"]
NUMERIC = list(bs.FEATURE_COLUMNS)
FEATURES = NUMERIC + [f"sc_{s}" for s in SCANNERS] + [f"cap_{c}" for c in CAPS]
C = 0.1                # regularisation (results were the same for 0.01-1.0)
FIRST_TEST_YEAR = 2020  # 2019 has too little history to train on
MIN_TRAIN = 300
LABELS = {
    "ret_1d": "move on the signal day", "ret_5d": "last 5 days' return", "ret_20d": "last 20 days' return",
    "ret_60d": "last 60 days' return", "dist_sma20": "distance above the 20-day average",
    "dist_sma50": "distance above the 50-day average", "dist_sma200": "distance above the 200-day average",
    "rsi14": "RSI(14)", "atr_pct": "daily range (ATR %)", "vol_ratio": "volume vs its 20-day average",
    "dist_52w_high": "nearness to the 52-week high", "log_turnover": "traded value (size/liquidity)",
    "up_days_10": "up days in the last 10", "bar_range_pct": "signal candle range",
    "close_pos_in_bar": "close near the candle's high", "trigger_gap_pct": "trigger above the close",
    "bar_risk_pct": "candle depth", "nifty_ret_20d": "Nifty's last 20 days",
    "nifty_dist_sma50": "Nifty vs its 50-day average",
    **{f"sc_{s}": f"scanner {s}" for s in SCANNERS}, **{f"cap_{c}": c.lower() for c in CAPS},
}


# ------------------------------------------------------------------ features

def signal_features(df: pd.DataFrame, sig: dict, nifty: pd.DataFrame | None, ind: pd.DataFrame | None = None) -> dict:
    """The numeric facts at the signal close (only bars up to the signal bar)."""
    ind = bs.indicator_frame(df) if ind is None else ind
    f = ind.iloc[sig["end_pos"]].to_dict()
    f.update(bs.bar_features(sig))
    f.update(bs.market_features(nifty, sig["signal_date"]))
    vol = pd.to_numeric(df["Volume"], errors="coerce") if "Volume" in df else pd.Series(dtype=float)
    if vol.iloc[max(0, sig["end_pos"] - 20):sig["end_pos"] + 1].isna().any() or vol.empty:
        f["vol_ratio"] = f["log_turnover"] = None  # volume not stored yet: the model uses its median
    return {k: (None if pd.isna(f.get(k)) else float(f[k])) for k in NUMERIC}


def matrix(rows: pd.DataFrame) -> np.ndarray:
    X = rows.reindex(columns=NUMERIC).astype(float).copy()
    for s in SCANNERS:
        X[f"sc_{s}"] = (rows["scanner"] == s).astype(float)
    known = rows["cap"].isin(CAPS)
    for c in CAPS:  # unknown market cap: NaN, filled with the average mix in predict()
        X[f"cap_{c}"] = np.where(known, (rows["cap"] == c).astype(float), np.nan)
    return X[FEATURES].to_numpy(dtype=float)


# --------------------------------------------------------------------- model

def fit(rows: pd.DataFrame) -> dict:
    """Logistic regression (median-imputed, standardised) as plain numbers."""
    from sklearn.linear_model import LogisticRegression
    X = matrix(rows)
    y = (rows["ret"] > 0).astype(int).to_numpy()
    med = np.nanmedian(X, axis=0)
    med = np.where(np.isnan(med), 0.0, med)
    cap = np.array([f.startswith("cap_") for f in FEATURES])
    X = np.where(np.isnan(X), np.where(cap, np.nan_to_num(np.nanmean(X, axis=0)), med), X)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    m = LogisticRegression(C=C, max_iter=1000).fit((X - mu) / sd, y)
    return {"median": med.tolist(), "mean": mu.tolist(), "std": sd.tolist(),
            "coef": m.coef_[0].tolist(), "intercept": float(m.intercept_[0])}


def predict(params: dict, rows: pd.DataFrame) -> np.ndarray:
    X = matrix(rows)
    fill = np.array([params["mean"][i] if f.startswith("cap_") else params["median"][i] for i, f in enumerate(FEATURES)])
    X = np.where(np.isnan(X), fill, X)
    z = ((X - np.array(params["mean"])) / np.array(params["std"])) @ np.array(params["coef"]) + params["intercept"]
    return 1 / (1 + np.exp(-z))


def walk_forward(trades: pd.DataFrame) -> pd.Series:
    """Out-of-sample score of every trade from FIRST_TEST_YEAR (NaN before)."""
    out = pd.Series(np.nan, index=trades.index)
    for y in range(FIRST_TEST_YEAR, int(trades["entry_date"].dt.year.max()) + 1):
        train = trades[trades["exit_date"] < pd.Timestamp(f"{y}-01-01")]
        test = trades["entry_date"].dt.year == y
        if len(train) < MIN_TRAIN or not test.any():
            continue
        out[test] = predict(fit(train), trades[test])
    return out


# -------------------------------------------------------------------- checks

def _auc(y: np.ndarray, s: np.ndarray) -> float:
    r = pd.Series(s).rank().to_numpy()
    pos = y == 1
    n1, n0 = pos.sum(), (~pos).sum()
    return float((r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else float("nan")


def _cagr(eq: pd.Series, a=None, b=None) -> float:
    x = eq[(eq.index >= pd.Timestamp(a or eq.index[0])) & (eq.index < pd.Timestamp(b or "2100-01-01"))]
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    return round(((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100, 1) if yrs > 0 else float("nan")


def _dd(eq: pd.Series) -> float:
    return round(float((eq / eq.cummax() - 1).min() * 100), 1)


def evaluate(trades: pd.DataFrame, oos: pd.Series) -> dict:
    """How the walk-forward scores did, and whether the ranker passes the gate."""
    import dipzone
    ok = oos.notna()
    t, s = trades[ok], oos[ok]
    years = sorted(t["entry_date"].dt.year.unique())
    per_year = []
    for y in years:
        m = t["entry_date"].dt.year == y
        hi = s[m] >= s[m].median()
        per_year.append({"year": int(y), "trades": int(m.sum()),
                         "top": round(float(t.loc[m & hi, "ret"].mean()), 2),
                         "bottom": round(float(t.loc[m & ~hi, "ret"].mean()), 2)})
    q = pd.qcut(s.rank(method="first"), 5, labels=False)
    quint = [round(float(t["ret"][q == i].mean()), 2) for i in range(5)]
    fixed = dipzone.portfolio(trades)["equity"]
    ranked = dipzone.portfolio(trades.assign(ml=oos))["equity"]
    start = pd.Timestamp(f"{years[0]}-01-01")
    mid = pd.Timestamp(f"{years[0] + (years[-1] - years[0] + 1) // 2}-01-01")
    halves = [(start, mid), (mid, None)]
    port = {}
    for name, eq in (("fixed", fixed), ("ml", ranked)):
        e = eq[eq.index >= start]
        port[name] = {"cagr": _cagr(e), "max_dd": _dd(e),
                      "halves": [_cagr(e, a, b) for a, b in halves]}
    wins = sum(p["top"] > p["bottom"] for p in per_year)
    checks = {
        "beats in first half": bool(port["ml"]["halves"][0] > port["fixed"]["halves"][0]),
        "beats in second half": bool(port["ml"]["halves"][1] > port["fixed"]["halves"][1]),
        "worst fall no more than 1 pt worse": bool(port["ml"]["max_dd"] >= port["fixed"]["max_dd"] - 1),
        "top half beat bottom half in 2/3 of years": bool(wins * 3 >= len(per_year) * 2),
    }
    return {"auc": round(_auc((t["ret"] > 0).astype(int).to_numpy(), s.to_numpy()), 3),
            "trades": int(ok.sum()), "years": per_year, "quintiles": quint,
            "halves": [f"{a.year}-{(b or pd.Timestamp(f'{years[-1] + 1}-01-01')).year - 1}" for a, b in halves],
            "portfolio": port, "checks": checks, "passed": all(checks.values())}


# ------------------------------------------------------------------ training

def train(trades: pd.DataFrame, path: Path = MODEL_PATH) -> tuple[dict, pd.Series]:
    """Walk-forward test, then a final model on every closed trade. Returns
    the saved model and the out-of-sample scores (for the official backtest)."""
    trades = trades.dropna(subset=["ret"]).copy()
    oos = walk_forward(trades)
    ev = evaluate(trades, oos)
    params = fit(trades)
    full = predict(params, trades)
    w = pd.Series(np.array(params["coef"]), index=FEATURES)
    model = {
        "on": ev["passed"],
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "trained_on": len(trades), "from": trades["entry_date"].min().date().isoformat(),
        "to": trades["exit_date"].max().date().isoformat(),
        "params": params, "features": FEATURES,
        "quantiles": np.quantile(full, np.linspace(0, 1, 101)).round(5).tolist(),
        "weights": [{"feature": LABELS.get(k, k), "w": round(float(v), 3)}
                    for k, v in w.reindex(w.abs().sort_values(ascending=False).index).items()][:10],
        "test": ev,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_clean(model), allow_nan=False), encoding="utf-8")
    return model, oos


def _clean(x):
    """JSON-safe: numpy scalars to Python, NaN to None."""
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else float(x)
    return x


def load(path: Path = MODEL_PATH) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def rank(model: dict | None, scanner: str, cap: str | None, feats: dict) -> int | None:
    """0-100: where this signal sits among the trades the model was trained
    on (100 = most likely to work). None without a model."""
    if not model:
        return None
    p = predict(model["params"], pd.DataFrame([{**feats, "scanner": scanner, "cap": cap}]))[0]
    return int(np.searchsorted(np.array(model["quantiles"]), p, side="right")) - 1 if np.isfinite(p) else None


def report(model: dict) -> str:
    ev = model["test"]
    f, m = ev["portfolio"]["fixed"], ev["portfolio"]["ml"]
    L = ["# ML signal ranker", "",
         f"Trained {model['trained_at'][:10]} on {model['trained_on']:,} closed trades "
         f"({model['from']} to {model['to']}) by `scripts/ranker.py`.", "",
         f"**Status: {'ON' if model['on'] else 'OFF'}**: "
         + ("it decides which signals get a free slot first." if model["on"]
            else "the fixed order (mid, large, small caps) stays; the ranker is shown for information."), "",
         "## Walk-forward test (each year scored by a model trained only on earlier years)", "",
         f"{ev['trades']:,} trades. AUC {ev['auc']:.3f} (0.5 = coin toss). Average return per trade by score, "
         f"lowest fifth to highest: {', '.join(f'{x:+.1f}%' for x in ev['quintiles'])}.", "",
         "| ₹10L, 15 slots | Fixed order | ML order |", "|---|---|---|",
         f"| Per year | {f['cagr']}% | {m['cagr']}% |",
         f"| {ev['halves'][0]} | {f['halves'][0]}% | {m['halves'][0]}% |",
         f"| {ev['halves'][1]} | {f['halves'][1]}% | {m['halves'][1]}% |",
         f"| Worst fall | {f['max_dd']}% | {m['max_dd']}% |", "",
         "| Year | Trades | Top half | Bottom half |", "|---|---|---|---|"]
    L += [f"| {y['year']} | {y['trades']} | {y['top']:+.2f}% | {y['bottom']:+.2f}% |" for y in ev["years"]]
    L += ["", "## Checks", ""] + [f"- {'✓' if v else '✗'} {k}" for k, v in ev["checks"].items()]
    L += ["", "## What it leans on (standardised weights; + = more likely to work)", ""]
    L += [f"- {w['feature']}: {w['w']:+.2f}" for w in model["weights"]]
    L += ["", "Tested 13 Nov 2026 and rejected: gradient-boosted trees (AUC 0.48-0.49, worse "
          "portfolios), the repeat/confluence counts (no gain). With 60 random orders the "
          "portfolio ranged 21-30% a year (median 25%), so a few points either way can be luck: "
          "the ranker must win in both halves, every week it retrains."]
    return "\n".join(L) + "\n"
