"""
Market Breadth Predictive Model
================================
Uses EMA10/20/50 breadth features to predict whether Nifty 50 will be
UP or DOWN over the next N trading days.

Features (all derived from breadth — no price leakage):
  - b10, b20, b50            : current breadth levels
  - roc1, roc5               : 1-day and 5-day rate of change of each breadth
  - spread_10_50             : b10 - b50  (fast vs slow divergence)
  - spread_10_20             : b10 - b20
  - b50_above_50             : binary flag, b50 > 50
  - b10_in_red               : binary flag, b10 < 30  (oversold)
  - b10_in_green             : binary flag, b10 > 70  (overbought)

Model    : Random Forest (interpretable, no scaling needed)
Validation: Walk-forward — trains on past, predicts unseen future only
Horizons : 5-day, 10-day, 20-day forward returns
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

from market_breadth import NIFTY_500_SAMPLE, EMA_PERIODS, compute_ema
from breadth_signals import fetch_prices, fetch_index, compute_breadth, find_tops_bottoms, _shade_signals, _legend_patches, SIG_COLOR

LOOKBACK_DAYS   = 500
INDEX_TICKER    = "^NSEI"
HORIZONS        = [5, 10, 20]       # forecast horizons in trading days
TRAIN_WINDOW    = 120               # walk-forward training window size
MIN_TRAIN       = 80                # minimum rows before first prediction


# ---------------------------------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------------------------------

def build_features(breadth: pd.DataFrame) -> pd.DataFrame:
    df = breadth.copy()

    for col in ["b10", "b20", "b50"]:
        df[f"{col}_roc1"] = df[col].diff(1)
        df[f"{col}_roc5"] = df[col].diff(5)
        df[f"{col}_ma5"]  = df[col].rolling(5).mean()

    df["spread_10_50"] = df["b10"] - df["b50"]
    df["spread_10_20"] = df["b10"] - df["b20"]
    df["spread_20_50"] = df["b20"] - df["b50"]

    df["b50_above_50"] = (df["b50"] > 50).astype(int)
    df["b10_in_red"]   = (df["b10"] < 30).astype(int)
    df["b10_in_green"] = (df["b10"] > 70).astype(int)
    df["all_above_50"] = ((df["b10"] > 50) & (df["b20"] > 50) & (df["b50"] > 50)).astype(int)
    df["all_below_40"] = ((df["b10"] < 40) & (df["b20"] < 40) & (df["b50"] < 40)).astype(int)

    # compression: all three lines close together = indecision
    df["breadth_range"] = df[["b10", "b20", "b50"]].max(axis=1) - df[["b10", "b20", "b50"]].min(axis=1)

    return df.dropna()


FEATURE_COLS = [
    "b10", "b20", "b50",
    "b10_roc1", "b20_roc1", "b50_roc1",
    "b10_roc5", "b20_roc5", "b50_roc5",
    "b10_ma5",  "b20_ma5",  "b50_ma5",
    "spread_10_50", "spread_10_20", "spread_20_50",
    "b50_above_50", "b10_in_red", "b10_in_green",
    "all_above_50", "all_below_40", "breadth_range",
]


# ---------------------------------------------------------------------------
# TARGETS
# ---------------------------------------------------------------------------

def build_targets(index_prices: pd.Series, features: pd.DataFrame, horizon: int) -> pd.Series:
    """1 = market UP after `horizon` days, 0 = DOWN."""
    fwd_ret = index_prices.pct_change(horizon).shift(-horizon)
    aligned = fwd_ret.reindex(features.index)
    return (aligned > 0).astype(int).rename(f"target_{horizon}d")


# ---------------------------------------------------------------------------
# WALK-FORWARD VALIDATION
# ---------------------------------------------------------------------------

def walk_forward(features: pd.DataFrame, target: pd.Series,
                 train_window: int, min_train: int) -> pd.DataFrame:
    """
    Expanding-window walk-forward.
    At each step: train on all past data, predict the next bar only.
    Returns a DataFrame with columns: actual, predicted, proba_up.
    """
    X = features[FEATURE_COLS]
    y = target.reindex(X.index).dropna()
    X = X.reindex(y.index)

    results = []
    model   = RandomForestClassifier(n_estimators=200, max_depth=5,
                                     min_samples_leaf=10, random_state=42)

    for i in range(min_train, len(X)):
        X_train = X.iloc[:i]
        y_train = y.iloc[:i]
        X_test  = X.iloc[[i]]

        if y_train.nunique() < 2:
            continue

        model.fit(X_train, y_train)
        pred  = model.predict(X_test)[0]
        proba = model.predict_proba(X_test)[0][1]   # P(UP)

        results.append({
            "date"      : X.index[i],
            "actual"    : int(y.iloc[i]),
            "predicted" : int(pred),
            "proba_up"  : round(proba, 3),
        })

    return pd.DataFrame(results).set_index("date")


# ---------------------------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------------------------

def train_full_model(features: pd.DataFrame, target: pd.Series) -> RandomForestClassifier:
    X = features[FEATURE_COLS].reindex(target.index).dropna()
    y = target.reindex(X.index).dropna()
    X = X.reindex(y.index)
    model = RandomForestClassifier(n_estimators=300, max_depth=5,
                                   min_samples_leaf=10, random_state=42)
    model.fit(X, y)
    return model


def print_importance(model: RandomForestClassifier, top_n: int = 10) -> None:
    imp = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print(f"\n  TOP {top_n} FEATURES")
    print(f"  {'-'*30}")
    for feat, val in imp.head(top_n).items():
        bar = "#" * int(val * 100)
        print(f"  {feat:<20} {val:.3f}  {bar}")


# ---------------------------------------------------------------------------
# CURRENT PREDICTION
# ---------------------------------------------------------------------------

def predict_now(model: RandomForestClassifier, features: pd.DataFrame) -> None:
    X_latest = features[FEATURE_COLS].iloc[[-1]]
    proba    = model.predict_proba(X_latest)[0][1]
    pred     = "UP" if proba >= 0.5 else "DOWN"
    conf     = max(proba, 1 - proba) * 100

    print("\n" + "=" * 50)
    print(f"  TODAY'S PREDICTION  ({features.index[-1].date()})")
    print("=" * 50)
    for h in HORIZONS:
        print(f"  {h:>2}d horizon : {pred}  (confidence {conf:.1f}%)")
    print(f"\n  P(Market UP) = {proba:.1%}")
    print(f"  b10={features['b10'].iloc[-1]:.0f}%  "
          f"b20={features['b20'].iloc[-1]:.0f}%  "
          f"b50={features['b50'].iloc[-1]:.0f}%")
    print("=" * 50)


# ---------------------------------------------------------------------------
# PLOT
# ---------------------------------------------------------------------------

def plot_model(bt_index: pd.Series, wf_results: dict, breadth: pd.DataFrame) -> None:
    n = len(wf_results)
    fig, axes = plt.subplots(n + 1, 1, figsize=(16, 4 * (n + 1)), sharex=True)
    fig.suptitle("Breadth Prediction Model — Walk-Forward Results", fontsize=13, fontweight="bold")

    # ── Nifty 50 panel ────────────────────────────────────────────────────
    ax0 = axes[0]
    ax0.plot(bt_index.index, bt_index.values, color="#37474F", linewidth=1.3, label="Nifty 50")

    tops, bottoms = find_tops_bottoms(bt_index, prominence=0.035, distance=20)
    for dt, price in tops.items():
        ax0.annotate("TOP", xy=(dt, price), xytext=(0, 12), textcoords="offset points",
                     ha="center", fontsize=7, color="#B71C1C", fontweight="bold",
                     arrowprops=dict(arrowstyle="-|>", color="#B71C1C", lw=1.0))
    for dt, price in bottoms.items():
        ax0.annotate("BOT", xy=(dt, price), xytext=(0, -16), textcoords="offset points",
                     ha="center", fontsize=7, color="#1B5E20", fontweight="bold",
                     arrowprops=dict(arrowstyle="-|>", color="#1B5E20", lw=1.0))

    ax0.set_ylabel("Nifty 50", fontsize=9)
    ax0.set_ylim(bt_index.min() * 0.96, bt_index.max() * 1.05)
    ax0.legend(loc="upper left", fontsize=8)
    ax0.grid(True, linestyle="--", alpha=0.35)

    # ── one panel per horizon ─────────────────────────────────────────────
    for i, (horizon, wf) in enumerate(wf_results.items(), start=1):
        ax = axes[i]
        acc = accuracy_score(wf["actual"], wf["predicted"])

        # shade correct / incorrect predictions
        correct = wf["proba_up"].copy()
        correct[wf["actual"] != wf["predicted"]] = np.nan

        ax.fill_between(wf.index, 0.5, wf["proba_up"],
                        where=wf["proba_up"] >= 0.5,
                        alpha=0.25, color="#4CAF50", label="P(UP)")
        ax.fill_between(wf.index, wf["proba_up"], 0.5,
                        where=wf["proba_up"] < 0.5,
                        alpha=0.25, color="#F44336", label="P(DOWN)")

        ax.plot(wf.index, wf["proba_up"], color="#1565C0", linewidth=1.0)
        ax.axhline(0.5, color="gray", linewidth=0.8, linestyle="--")
        ax.axhline(0.65, color="#4CAF50", linewidth=0.6, linestyle=":", alpha=0.7)
        ax.axhline(0.35, color="#F44336", linewidth=0.6, linestyle=":", alpha=0.7)

        ax.set_ylim(0, 1)
        ax.set_ylabel(f"P(UP) — {horizon}d", fontsize=9)
        ax.set_title(f"{horizon}-day Horizon  |  Accuracy: {acc:.1%}", fontsize=9, loc="left")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.35)

        # mark actual UP/DOWN as dots on the probability line
        up_mask   = wf["actual"] == 1
        down_mask = wf["actual"] == 0
        ax.scatter(wf.index[up_mask],   wf["proba_up"][up_mask],
                   color="#4CAF50", s=6, zorder=4, alpha=0.5)
        ax.scatter(wf.index[down_mask], wf["proba_up"][down_mask],
                   color="#F44336", s=6, zorder=4, alpha=0.5)

    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    out = "breadth_model.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nChart saved: breadth_model.png")
    plt.show()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Download data
    prices = fetch_prices(NIFTY_500_SAMPLE, LOOKBACK_DAYS)
    valid  = prices.columns[prices.notna().sum() >= max(EMA_PERIODS)].tolist()
    prices = prices[valid]
    print(f"Stocks: {len(valid)} valid")

    index_px = fetch_index(LOOKBACK_DAYS)

    # 2. Breadth + features
    breadth  = compute_breadth(prices)
    features = build_features(breadth)

    aligned_idx = index_px.reindex(features.index).ffill()

    # 3. Walk-forward for each horizon
    wf_results = {}
    for h in HORIZONS:
        target = build_targets(aligned_idx, features, h)
        wf     = walk_forward(features, target, TRAIN_WINDOW, MIN_TRAIN)
        acc    = accuracy_score(wf["actual"], wf["predicted"])
        print(f"\n  {h}-day horizon accuracy: {acc:.1%}")
        print(classification_report(wf["actual"], wf["predicted"],
                                    target_names=["DOWN", "UP"], zero_division=0))
        wf_results[h] = wf

    # 4. Full model for feature importance + today's prediction
    target_10d = build_targets(aligned_idx, features, 10)
    full_model = train_full_model(features, target_10d)
    print_importance(full_model)
    predict_now(full_model, features)

    # 5. Save predictions
    for h, wf in wf_results.items():
        wf.to_csv(f"breadth_pred_{h}d.csv")
    print("\nPrediction CSVs saved.")

    # 6. Plot
    plot_model(aligned_idx, wf_results, breadth)

    return wf_results, full_model, features


if __name__ == "__main__":
    wf_results, model, features = main()
