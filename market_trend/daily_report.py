"""
Swing Trading Daily Morning Report
====================================
Run this before 9:15 AM each day.
Gives: market bias, conviction, key levels, position sizing, and chart.

Designed for 2-10 day swing trades on Nifty / large-cap stocks.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as mlines
from scipy.signal import find_peaks
from sklearn.ensemble import GradientBoostingClassifier
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

from market_breadth import NIFTY_500_SAMPLE, EMA_PERIODS, compute_ema
from breadth_signals  import fetch_prices, fetch_index, compute_breadth
from breadth_signals  import find_tops_bottoms
from reversal_model   import (label_reversals, build_features, FEATURE_COLS,
                               walk_forward)

LOOKBACK_DAYS = 700
PLOT_DAYS     = 252    # 1 year on chart
PEAK_PROM     = 0.035
PEAK_DIST     = 20
MIN_TRAIN     = 100

# Swing-specific thresholds
STRONG_SIGNAL  = 0.60   # high conviction
MILD_SIGNAL    = 0.50   # mild conviction


# ---------------------------------------------------------------------------
# MODELS (same as reversal_model.py — trained fresh each run)
# ---------------------------------------------------------------------------

def train_models(features, top_label, bot_label):
    X = features[FEATURE_COLS]

    def fit(target):
        y = target.reindex(X.index).dropna()
        Xt = X.reindex(y.index)
        m = GradientBoostingClassifier(n_estimators=200, max_depth=3,
                                       learning_rate=0.05, subsample=0.8,
                                       min_samples_leaf=8, random_state=42)
        m.fit(Xt, y)
        return m

    return fit(top_label.reindex(X.index)), fit(bot_label.reindex(X.index))


# ---------------------------------------------------------------------------
# MORNING BRIEFING
# ---------------------------------------------------------------------------

def swing_bias(p_top, p_bot):
    if p_bot >= STRONG_SIGNAL:
        return "STRONG BUY BIAS",  "#1B5E20"
    elif p_bot >= MILD_SIGNAL:
        return "MILD BUY BIAS",    "#388E3C"
    elif p_top >= STRONG_SIGNAL:
        return "STRONG SELL BIAS", "#B71C1C"
    elif p_top >= MILD_SIGNAL:
        return "MILD SELL BIAS",   "#E53935"
    else:
        return "NEUTRAL",          "#37474F"


def position_size(p_top, p_bot, b50):
    """Returns suggested allocation as % of swing capital."""
    if p_bot >= STRONG_SIGNAL and b50 < 40:
        return 100, "Full size — oversold breadth + strong bottom signal"
    elif p_bot >= MILD_SIGNAL:
        return 75,  "3/4 size — buy bias, wait for price confirmation"
    elif p_top >= STRONG_SIGNAL and b50 > 55:
        return 0,   "No new longs — exit or hedge existing positions"
    elif p_top >= MILD_SIGNAL:
        return 25,  "1/4 size only — top risk is elevated"
    else:
        return 50,  "Half size — neutral zone, trade setups with trend"


def print_report(features, top_model, bot_model,
                 peaks, troughs, index_px, date_str):
    X_now  = features[FEATURE_COLS].iloc[[-1]]
    p_top  = top_model.predict_proba(X_now)[0][1]
    p_bot  = bot_model.predict_proba(X_now)[0][1]

    b10 = features["b10"].iloc[-1]
    b20 = features["b20"].iloc[-1]
    b50 = features["b50"].iloc[-1]

    bias_label, _ = swing_bias(p_top, p_bot)
    alloc, alloc_note = position_size(p_top, p_bot, b50)

    # nearest support (last bottom) and resistance (last top)
    last_bot = troughs.iloc[-1] if len(troughs) else None
    last_top = peaks.iloc[-1]   if len(peaks)   else None
    cur_px   = index_px.iloc[-1]

    dist_res = ((last_top - cur_px) / cur_px * 100) if last_top else None
    dist_sup = ((cur_px - last_bot) / cur_px * 100) if last_bot else None

    # 5-day and 10-day trailing return
    ret5  = (cur_px / index_px.iloc[-6]  - 1) * 100 if len(index_px) > 5  else 0
    ret10 = (cur_px / index_px.iloc[-11] - 1) * 100 if len(index_px) > 10 else 0

    # breadth zone
    if b50 > 60 and b20 > 60:
        breadth_zone = "OVERBOUGHT — broad participation high"
    elif b50 < 35 and b20 < 35:
        breadth_zone = "OVERSOLD   — broad capitulation"
    elif b50 > 50:
        breadth_zone = "BULLISH    — majority above medium trend"
    elif b50 < 45:
        breadth_zone = "BEARISH    — majority below medium trend"
    else:
        breadth_zone = "NEUTRAL    — mixed participation"

    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  SWING TRADING MORNING REPORT  |  {date_str}")
    print(sep)
    print(f"  Nifty 50      : {int(cur_px):>8,}  "
          f"(5d {ret5:+.1f}%  |  10d {ret10:+.1f}%)")
    print(f"  Resistance    : {int(last_top):>8,}  ({dist_res:+.1f}% away)" if dist_res else "")
    print(f"  Support       : {int(last_bot):>8,}  ({dist_sup:.1f}% below)" if dist_sup else "")
    print(f"\n  {'-'*58}")
    print(f"  BIAS          : {bias_label}")
    print(f"  P(TOP)        : {p_top:.0%}   {'*** HIGH RISK ***' if p_top >= STRONG_SIGNAL else ''}")
    print(f"  P(BOTTOM)     : {p_bot:.0%}   {'*** STRONG SETUP ***' if p_bot >= STRONG_SIGNAL else ''}")
    print(f"  {'-'*58}")
    print(f"  BREADTH ZONE  : {breadth_zone}")
    print(f"  EMA10 breadth : {b10:.0f}%  |  EMA20: {b20:.0f}%  |  EMA50: {b50:.0f}%")
    print(f"  {'-'*58}")
    print(f"  POSITION SIZE : {alloc}% of swing capital")
    print(f"  NOTE          : {alloc_note}")
    print(sep)

    # actionable swing rules
    print(f"\n  SWING PLAYBOOK FOR TODAY:")
    if "BUY" in bias_label:
        print(f"  - Look for LONG setups: stocks near support, reversing up")
        print(f"  - Confirm with: price above yesterday's high + volume")
        print(f"  - Target: last resistance ({int(last_top):,})" if last_top else "")
        print(f"  - Stop : below today's low or last swing low")
        if b50 < 40:
            print(f"  - Breadth is OVERSOLD — high-probability bounce zone")
    elif "SELL" in bias_label:
        print(f"  - Avoid new longs. Exit existing if near resistance")
        print(f"  - Look for SHORT setups: stocks failing at resistance")
        print(f"  - Confirm with: price below yesterday's low + volume")
        print(f"  - Support target: {int(last_bot):,}" if last_bot else "")
        if b50 > 55:
            print(f"  - Breadth is OVERBOUGHT — high-probability pullback zone")
    else:
        print(f"  - No strong edge. Trade only the best setups.")
        print(f"  - Keep size small (50%). Wait for a clearer signal.")
        print(f"  - Range: support {int(last_bot):,} — resistance {int(last_top):,}" if last_bot and last_top else "")

    print()


# ---------------------------------------------------------------------------
# CHART
# ---------------------------------------------------------------------------

def plot_chart(index_px, wf_top, wf_bot, peaks, troughs,
               breadth, p_top_today, p_bot_today):

    # drive the date range from actual price data, not wf frames
    idx       = index_px.dropna().tail(PLOT_DAYS)
    bd        = breadth.reindex(idx.index).ffill().dropna()
    start     = idx.index[0]
    peaks_p   = peaks[peaks.index     >= start]
    troughs_p = troughs[troughs.index >= start]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                   gridspec_kw={"height_ratios": [2.5, 1.5]})

    today_str = index_px.index[-1].strftime("%d %b %Y")
    bias_label, bias_color = swing_bias(p_top_today, p_bot_today)
    fig.suptitle(f"Swing Report  |  {today_str}  |  Bias: {bias_label}",
                 fontsize=13, fontweight="bold", color=bias_color)

    # ── Nifty 50 panel ────────────────────────────────────────────────────
    y_rng = idx.max() - idx.min()
    ax1.plot(idx.index, idx.values, color="#212121", linewidth=1.5,
             label="Nifty 50", zorder=4)

    for dt, price in peaks_p.items():
        ax1.scatter(dt, price, marker="v", color="#D32F2F", s=130, zorder=6)
        ax1.text(dt, price + y_rng * 0.028,
                 f"TOP\n{int(price):,}",
                 ha="center", va="bottom", fontsize=8,
                 color="#D32F2F", fontweight="bold", zorder=6)

    for dt, price in troughs_p.items():
        ax1.scatter(dt, price, marker="^", color="#2E7D32", s=130, zorder=6)
        ax1.text(dt, price - y_rng * 0.028,
                 f"BOT\n{int(price):,}",
                 ha="center", va="top", fontsize=8,
                 color="#2E7D32", fontweight="bold", zorder=6)

    # horizontal support / resistance lines from last confirmed levels
    if len(peaks_p):
        ax1.axhline(peaks_p.iloc[-1], color="#D32F2F", linewidth=0.9,
                    linestyle="--", alpha=0.6, label=f"Resistance {int(peaks_p.iloc[-1]):,}")
    if len(troughs_p):
        ax1.axhline(troughs_p.iloc[-1], color="#2E7D32", linewidth=0.9,
                    linestyle="--", alpha=0.6, label=f"Support {int(troughs_p.iloc[-1]):,}")

    ax1.set_ylim(idx.min() - y_rng * 0.10, idx.max() + y_rng * 0.14)
    ax1.set_ylabel("Nifty 50", fontsize=9)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, linestyle="--", alpha=0.3)

    # ── EMA Breadth panel ─────────────────────────────────────────────────
    ax2.plot(bd.index, bd["b10"], color="#2196F3", linewidth=1.4, label="10 EMA")
    ax2.plot(bd.index, bd["b20"], color="#FF9800", linewidth=1.4, label="20 EMA")
    ax2.plot(bd.index, bd["b50"], color="#4CAF50", linewidth=1.8, label="50 EMA")

    ax2.axhline(70, color="#4CAF50", linewidth=0.7, linestyle=":", alpha=0.7)
    ax2.axhline(50, color="gray",    linewidth=0.7, linestyle="--", alpha=0.6)
    ax2.axhline(30, color="#F44336", linewidth=0.7, linestyle=":", alpha=0.7)
    ax2.axhspan(70, 100, alpha=0.06, color="green")
    ax2.axhspan(0,  30,  alpha=0.06, color="red")

    # annotate today's breadth values on right edge
    last_dt = bd.index[-1]
    for col, color, label in [("b10","#2196F3","b10"), ("b20","#FF9800","b20"), ("b50","#4CAF50","b50")]:
        val = bd[col].iloc[-1]
        ax2.annotate(f"{label}={val:.0f}%", xy=(last_dt, val),
                     xytext=(6, 0), textcoords="offset points",
                     color=color, fontsize=8, va="center", fontweight="bold")

    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% Stocks Above EMA", fontsize=9)
    ax2.set_xlabel("Date", fontsize=9)
    ax2.legend(loc="upper left", fontsize=8, ncol=3)
    ax2.grid(True, linestyle="--", alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    out = "swing_report.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  Chart saved: {out}\n")
    plt.show()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("Fetching data ...")
    prices   = fetch_prices(NIFTY_500_SAMPLE, LOOKBACK_DAYS)
    valid    = prices.columns[prices.notna().sum() >= max(EMA_PERIODS)].tolist()
    prices   = prices[valid]
    index_px = fetch_index(LOOKBACK_DAYS)

    breadth  = compute_breadth(prices)
    features = build_features(breadth, index_px)
    aligned  = index_px.reindex(features.index).ffill()

    top_label, bot_label, peaks, troughs = label_reversals(
        aligned, window=5, prominence=PEAK_PROM, distance=PEAK_DIST)

    print("Training models ...")
    top_model, bot_model = train_models(features, top_label, bot_label)

    X_now = features[FEATURE_COLS].iloc[[-1]]
    p_top = top_model.predict_proba(X_now)[0][1]
    p_bot = bot_model.predict_proba(X_now)[0][1]

    date_str = features.index[-1].strftime("%A, %d %b %Y")
    print_report(features, top_model, bot_model,
                 peaks, troughs, aligned, date_str)

    # build minimal wf-like frames just to satisfy plot signature
    wf_dummy = pd.DataFrame({"proba": [0.5]}, index=[aligned.index[-1]])
    plot_chart(aligned, wf_dummy, wf_dummy,
               peaks, troughs, breadth, p_top, p_bot)


if __name__ == "__main__":
    main()
