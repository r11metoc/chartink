"""
Reversal Detection Model
========================
Detects probability of a TOP or BOTTOM reversal at each bar.

Two separate classifiers:
  TOP model    → P(market is forming a top right now)
  BOTTOM model → P(market is forming a bottom right now)

Labels are derived from actual price peaks/troughs (scipy find_peaks).
A bar is labeled as TOP if it falls within ±LABEL_WINDOW days of a detected peak.
Same for BOTTOM.

Features (no lookahead — all past data only):
  Breadth levels, smoothed breadth, rate-of-change, spreads,
  trailing index returns, distance from recent high/low.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import find_peaks
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

from market_breadth import NIFTY_500_SAMPLE, EMA_PERIODS, compute_ema
from breadth_signals import fetch_prices, fetch_index, compute_breadth

LOOKBACK_DAYS  = 700
LABEL_WINDOW   = 5       # bars on each side of a peak/trough to label as reversal
PEAK_PROM      = 0.035   # minimum prominence for a significant peak (3.5%)
PEAK_DIST      = 20      # minimum bars between two peaks
MIN_TRAIN      = 100     # minimum training samples before first walk-forward prediction


# ---------------------------------------------------------------------------
# LABELS FROM ACTUAL PEAKS / TROUGHS
# ---------------------------------------------------------------------------

def label_reversals(index_prices: pd.Series, window: int, prominence: float, distance: int):
    """
    Returns two binary Series aligned to index_prices:
      top_label    : 1 within `window` bars of a price peak
      bottom_label : 1 within `window` bars of a price trough
    """
    arr = index_prices.values
    prom = prominence * arr.mean()

    peak_idx,   _ = find_peaks( arr, prominence=prom, distance=distance)
    trough_idx, _ = find_peaks(-arr, prominence=prom, distance=distance)

    top_label    = np.zeros(len(arr), dtype=int)
    bottom_label = np.zeros(len(arr), dtype=int)

    for i in peak_idx:
        lo, hi = max(0, i - window), min(len(arr), i + window + 1)
        top_label[lo:hi] = 1

    for i in trough_idx:
        lo, hi = max(0, i - window), min(len(arr), i + window + 1)
        bottom_label[lo:hi] = 1

    top_ser    = pd.Series(top_label,    index=index_prices.index, name="top_label")
    bottom_ser = pd.Series(bottom_label, index=index_prices.index, name="bottom_label")

    # store exact peak/trough dates for annotation
    peaks   = index_prices.iloc[peak_idx]
    troughs = index_prices.iloc[trough_idx]

    return top_ser, bottom_ser, peaks, troughs


# ---------------------------------------------------------------------------
# FEATURES
# ---------------------------------------------------------------------------

def build_features(breadth: pd.DataFrame, index_prices: pd.Series) -> pd.DataFrame:
    df = breadth.copy()

    # smoothed breadth
    for col in ["b10", "b20", "b50"]:
        df[f"{col}_ma3"]  = df[col].rolling(3).mean()
        df[f"{col}_ma5"]  = df[col].rolling(5).mean()
        df[f"{col}_roc1"] = df[col].diff(1)
        df[f"{col}_roc3"] = df[col].diff(3)
        df[f"{col}_roc5"] = df[col].diff(5)

    # spreads (divergence between fast and slow)
    df["spread_10_50"] = df["b10"] - df["b50"]
    df["spread_10_20"] = df["b10"] - df["b20"]
    df["spread_20_50"] = df["b20"] - df["b50"]

    # compression (all three lines close = indecision before move)
    df["breadth_range"] = (df[["b10","b20","b50"]].max(axis=1)
                         - df[["b10","b20","b50"]].min(axis=1))

    # zone flags
    df["b10_overbought"] = (df["b10"] > 70).astype(int)
    df["b10_oversold"]   = (df["b10"] < 30).astype(int)
    df["b50_above_50"]   = (df["b50"] > 50).astype(int)
    df["all_overbought"] = ((df["b10"] > 65) & (df["b20"] > 60) & (df["b50"] > 55)).astype(int)
    df["all_oversold"]   = ((df["b10"] < 35) & (df["b20"] < 40) & (df["b50"] < 45)).astype(int)

    # price-based features (trailing — no lookahead)
    idx = index_prices.reindex(df.index).ffill()
    df["ret_5d"]   = idx.pct_change(5)
    df["ret_10d"]  = idx.pct_change(10)
    df["ret_20d"]  = idx.pct_change(20)
    df["hi20_pct"] = idx / idx.rolling(20).max() - 1   # distance from 20d high (<=0)
    df["lo20_pct"] = idx / idx.rolling(20).min() - 1   # distance from 20d low  (>=0)

    # divergence: price near high but breadth not confirming
    df["top_divergence"] = df["hi20_pct"].abs() * (100 - df["b50"])   # high price + low b50
    df["bot_divergence"] = df["lo20_pct"]       * df["b50"]            # low price + low b50

    return df.dropna()


FEATURE_COLS = [
    "b10", "b20", "b50",
    "b10_ma3", "b20_ma3", "b50_ma3",
    "b10_ma5", "b20_ma5", "b50_ma5",
    "b10_roc1", "b20_roc1", "b50_roc1",
    "b10_roc3", "b20_roc3", "b50_roc3",
    "b10_roc5", "b20_roc5", "b50_roc5",
    "spread_10_50", "spread_10_20", "spread_20_50",
    "breadth_range",
    "b10_overbought", "b10_oversold", "b50_above_50",
    "all_overbought", "all_oversold",
    "ret_5d", "ret_10d", "ret_20d",
    "hi20_pct", "lo20_pct",
    "top_divergence", "bot_divergence",
]


# ---------------------------------------------------------------------------
# WALK-FORWARD
# ---------------------------------------------------------------------------

def walk_forward(features: pd.DataFrame, target: pd.Series,
                 min_train: int, label: str) -> pd.DataFrame:
    X = features[FEATURE_COLS]
    y = target.reindex(X.index).dropna()
    X = X.reindex(y.index)

    model   = GradientBoostingClassifier(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        subsample=0.8, min_samples_leaf=8, random_state=42
    )
    results = []

    for i in range(min_train, len(X)):
        X_train, y_train = X.iloc[:i], y.iloc[:i]
        if y_train.nunique() < 2:
            continue
        model.fit(X_train, y_train)
        proba = model.predict_proba(X.iloc[[i]])[0][1]
        results.append({"date": X.index[i], "actual": int(y.iloc[i]), "proba": round(proba, 3)})

    df = pd.DataFrame(results).set_index("date")
    df["predicted"] = (df["proba"] >= 0.5).astype(int)
    return df


# ---------------------------------------------------------------------------
# STATS
# ---------------------------------------------------------------------------

def print_stats(wf: pd.DataFrame, label: str) -> None:
    acc  = accuracy_score(wf["actual"], wf["predicted"])
    prec = precision_score(wf["actual"], wf["predicted"], zero_division=0)
    rec  = recall_score(wf["actual"], wf["predicted"], zero_division=0)
    f1   = f1_score(wf["actual"], wf["predicted"], zero_division=0)
    n_ev = wf["actual"].sum()
    print(f"  {label:<8}  acc={acc:.1%}  prec={prec:.1%}  recall={rec:.1%}  "
          f"f1={f1:.2f}  events={n_ev}")


# ---------------------------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------------------------

def print_importance(model, top_n: int = 8, label: str = "") -> None:
    imp = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print(f"\n  Top features [{label}]:")
    for feat, val in imp.head(top_n).items():
        bar = "#" * int(val * 150)
        print(f"    {feat:<22} {val:.3f}  {bar}")


# ---------------------------------------------------------------------------
# TODAY'S PREDICTION
# ---------------------------------------------------------------------------

def predict_today(top_model, bot_model, features: pd.DataFrame) -> None:
    X_now  = features[FEATURE_COLS].iloc[[-1]]
    p_top  = top_model.predict_proba(X_now)[0][1]
    p_bot  = bot_model.predict_proba(X_now)[0][1]

    state = "NEUTRAL"
    if p_top > 0.55:
        state = "TOP forming — consider reducing longs"
    elif p_bot > 0.55:
        state = "BOTTOM forming — consider adding longs"

    print("\n" + "=" * 56)
    print(f"  REVERSAL RADAR  ({features.index[-1].date()})")
    print("=" * 56)
    print(f"  P(TOP reversal)    = {p_top:.1%}  {'<<' if p_top > 0.55 else ''}")
    print(f"  P(BOTTOM reversal) = {p_bot:.1%}  {'<<' if p_bot > 0.55 else ''}")
    print(f"\n  Signal : {state}")
    print(f"\n  b10={features['b10'].iloc[-1]:.0f}%  "
          f"b20={features['b20'].iloc[-1]:.0f}%  "
          f"b50={features['b50'].iloc[-1]:.0f}%")
    print("=" * 56)


# ---------------------------------------------------------------------------
# PLOT
# ---------------------------------------------------------------------------

def plot_reversals(index_prices: pd.Series, wf_top: pd.DataFrame,
                   wf_bot: pd.DataFrame, peaks: pd.Series,
                   troughs: pd.Series, breadth: pd.DataFrame,
                   plot_days: int = 252) -> None:

    # ── trim everything to the last `plot_days` bars ──────────────────────
    wf_top  = wf_top.tail(plot_days)
    wf_bot  = wf_bot.tail(plot_days)
    idx     = index_prices.reindex(wf_top.index).ffill()
    bd      = breadth.reindex(wf_top.index).ffill()
    start   = wf_top.index[0]
    peaks   = peaks[peaks.index >= start]
    troughs = troughs[troughs.index >= start]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                   gridspec_kw={"height_ratios": [2.5, 1.5]})
    fig.suptitle("Nifty 50 — Reversal Inference & EMA Breadth (1 Year)",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Nifty 50 + reversal markers ─────────────────────────────
    ax1.plot(idx.index, idx.values, color="#212121", linewidth=1.5,
             label="Nifty 50", zorder=4)

    y_rng = idx.max() - idx.min()

    for dt, price in peaks.items():
        # red downward triangle on the price line
        ax1.scatter(dt, price, marker="v", color="#D32F2F", s=120, zorder=6)
        ax1.text(dt, price + y_rng * 0.025,
                 f"TOP\n{int(price):,}",
                 ha="center", va="bottom", fontsize=8,
                 color="#D32F2F", fontweight="bold", zorder=6)

    for dt, price in troughs.items():
        # green upward triangle on the price line
        ax1.scatter(dt, price, marker="^", color="#2E7D32", s=120, zorder=6)
        ax1.text(dt, price - y_rng * 0.025,
                 f"BOT\n{int(price):,}",
                 ha="center", va="top", fontsize=8,
                 color="#2E7D32", fontweight="bold", zorder=6)

    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches
    legend_h = [
        mlines.Line2D([], [], color="#212121", linewidth=1.5, label="Nifty 50"),
        mlines.Line2D([], [], marker="v", color="#D32F2F", linewidth=0,
                      markersize=8, label="TOP — sell / reduce"),
        mlines.Line2D([], [], marker="^", color="#2E7D32", linewidth=0,
                      markersize=8, label="BOT — buy / add"),
    ]
    ax1.legend(handles=legend_h, loc="upper left", fontsize=8)
    ax1.set_ylim(idx.min() - y_rng * 0.08, idx.max() + y_rng * 0.12)
    ax1.set_ylabel("Nifty 50", fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.3, zorder=1)

    # ── Panel 2: EMA 10 / 20 / 50 breadth ────────────────────────────────
    ax2.plot(bd.index, bd["b10"], color="#2196F3", linewidth=1.4, label="10 EMA breadth")
    ax2.plot(bd.index, bd["b20"], color="#FF9800", linewidth=1.4, label="20 EMA breadth")
    ax2.plot(bd.index, bd["b50"], color="#4CAF50", linewidth=1.8, label="50 EMA breadth")

    ax2.axhline(70, color="#4CAF50", linewidth=0.7, linestyle=":", alpha=0.8)
    ax2.axhline(50, color="gray",    linewidth=0.7, linestyle="--", alpha=0.6)
    ax2.axhline(30, color="#F44336", linewidth=0.7, linestyle=":", alpha=0.8)
    ax2.axhspan(70, 100, alpha=0.06, color="green")
    ax2.axhspan(0,  30,  alpha=0.06, color="red")

    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% Stocks Above EMA", fontsize=9)
    ax2.set_xlabel("Date", fontsize=9)
    ax2.legend(loc="upper left", fontsize=8, ncol=3)
    ax2.grid(True, linestyle="--", alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    plt.savefig("reversal_model.png", dpi=150, bbox_inches="tight")
    print("Chart saved: reversal_model.png")
    plt.show()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Download
    prices   = fetch_prices(NIFTY_500_SAMPLE, LOOKBACK_DAYS)
    valid    = prices.columns[prices.notna().sum() >= max(EMA_PERIODS)].tolist()
    prices   = prices[valid]
    index_px = fetch_index(LOOKBACK_DAYS)
    print(f"Stocks: {len(valid)} valid  |  Index bars: {len(index_px)}")

    # 2. Breadth + features
    breadth  = compute_breadth(prices)
    features = build_features(breadth, index_px)

    aligned_idx = index_px.reindex(features.index).ffill()

    # 3. Labels from actual peaks/troughs
    top_label, bot_label, peaks, troughs = label_reversals(
        aligned_idx, window=LABEL_WINDOW,
        prominence=PEAK_PROM, distance=PEAK_DIST
    )
    print(f"\nDetected  {len(peaks)} tops  |  {len(troughs)} bottoms")
    print(f"TOP  label: {top_label.sum()} bars flagged")
    print(f"BOT  label: {bot_label.sum()} bars flagged")

    # 4. Walk-forward for both classifiers
    print("\nRunning walk-forward (this takes ~30s) ...")
    print("=" * 56)
    wf_top = walk_forward(features, top_label.reindex(features.index),
                          MIN_TRAIN, "TOP")
    wf_bot = walk_forward(features, bot_label.reindex(features.index),
                          MIN_TRAIN, "BOTTOM")

    print_stats(wf_top, "TOP")
    print_stats(wf_bot, "BOTTOM")

    # 5. Full model for importance + today
    from sklearn.ensemble import GradientBoostingClassifier
    X_all = features[FEATURE_COLS]

    def fit_full(target):
        y = target.reindex(X_all.index).dropna()
        X = X_all.reindex(y.index)
        m = GradientBoostingClassifier(n_estimators=200, max_depth=3,
                                       learning_rate=0.05, subsample=0.8,
                                       min_samples_leaf=8, random_state=42)
        m.fit(X, y)
        return m

    top_model = fit_full(top_label.reindex(features.index))
    bot_model = fit_full(bot_label.reindex(features.index))

    print_importance(top_model, label="TOP")
    print_importance(bot_model, label="BOTTOM")

    predict_today(top_model, bot_model, features)

    # 6. Save
    wf_top.to_csv("reversal_top.csv")
    wf_bot.to_csv("reversal_bot.csv")
    print("\nCSVs saved: reversal_top.csv, reversal_bot.csv")

    # 7. Plot
    plot_reversals(aligned_idx, wf_top, wf_bot, peaks, troughs, breadth)

    return wf_top, wf_bot, top_model, bot_model, features


if __name__ == "__main__":
    wf_top, wf_bot, top_model, bot_model, features = main()
