"""
Market Breadth Signal Generator + Backtester
=============================================
Answers: "When should one be LONG and when SHORT based on breadth history?"

Signal logic (all based on % of stocks above each EMA):
  LONG  : EMA50 breadth crosses above 50%  AND  EMA20 breadth > 45%
  SHORT : EMA50 breadth crosses below 45%  AND  EMA10 breadth < 40%
  CASH  : everything in between (no clear edge)

Backtest: applies signals to Nifty 50 daily returns.
Outputs  : console stats table + 4-panel chart + CSV of all signals.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from scipy.signal import find_peaks
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── re-use the universe and EMA logic from market_breadth.py ──────────────
from market_breadth import NIFTY_500_SAMPLE, EMA_PERIODS, compute_ema

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
LOOKBACK_DAYS   = 500          # trading days of stock history
INDEX_TICKER    = "^NSEI"
INITIAL_CAPITAL = 100_000      # INR, for equity-curve calculation

# Signal thresholds — tune these to your preference
LONG_EMA50_THRESH  = 50        # EMA50 breadth must cross ABOVE this to go long
LONG_EMA20_THRESH  = 45        # EMA20 breadth must also be above this
SHORT_EMA50_THRESH = 45        # EMA50 breadth must cross BELOW this to go short
SHORT_EMA10_THRESH = 40        # EMA10 breadth must also be below this


# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------

def fetch_prices(tickers, lookback):
    end   = datetime.today()
    start = end - timedelta(days=int(lookback * 1.6))
    print(f"Downloading {len(tickers)} stocks ({lookback} day window) ...")
    raw = yf.download(tickers, start=start.strftime("%Y-%m-%d"),
                      end=end.strftime("%Y-%m-%d"),
                      auto_adjust=True, progress=False, threads=True)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    return prices.dropna(how="all").tail(lookback)


def fetch_index(lookback):
    end   = datetime.today()
    start = end - timedelta(days=int(lookback * 1.6))
    raw   = yf.download(INDEX_TICKER, start=start.strftime("%Y-%m-%d"),
                        end=end.strftime("%Y-%m-%d"),
                        auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
        return (close.iloc[:, 0] if isinstance(close, pd.DataFrame) else close).tail(lookback)
    return raw["Close"].tail(lookback)


def compute_breadth(prices):
    out = {}
    for p in EMA_PERIODS:
        ema_df = prices.apply(lambda c: compute_ema(c.dropna(), p).reindex(prices.index))
        above  = (prices > ema_df).sum(axis=1)
        total  = prices.notna().sum(axis=1)
        out[f"b{p}"] = (above / total * 100).round(2)
    return pd.DataFrame(out).dropna()


# ---------------------------------------------------------------------------
# SIGNALS
# ---------------------------------------------------------------------------

def generate_signals(breadth: pd.DataFrame) -> pd.Series:
    """
    Returns a Series with values:
      +1  LONG
       0  CASH (flat)
      -1  SHORT

    Entry rules:
      LONG  — b50 crosses above LONG_EMA50_THRESH  AND  b20 > LONG_EMA20_THRESH
      SHORT — b50 crosses below SHORT_EMA50_THRESH AND  b10 < SHORT_EMA10_THRESH

    Position is held until the OPPOSITE signal fires.
    """
    b10  = breadth["b10"]
    b20  = breadth["b20"]
    b50  = breadth["b50"]

    position  = pd.Series(0, index=breadth.index, dtype=int)
    current   = 0                           # current position: +1 / 0 / -1

    for i in range(1, len(breadth)):
        prev50 = b50.iloc[i - 1]
        cur50  = b50.iloc[i]
        cur20  = b20.iloc[i]
        cur10  = b10.iloc[i]

        long_trigger  = (prev50 <= LONG_EMA50_THRESH  and cur50 > LONG_EMA50_THRESH)  and cur20 > LONG_EMA20_THRESH
        short_trigger = (prev50 >= SHORT_EMA50_THRESH and cur50 < SHORT_EMA50_THRESH) and cur10 < SHORT_EMA10_THRESH

        # Additional confirmation: sustained pressure re-confirms existing position
        long_sustain  = cur50 > LONG_EMA50_THRESH  + 5 and cur20 > LONG_EMA20_THRESH  + 5
        short_sustain = cur50 < SHORT_EMA50_THRESH - 5 and cur10 < SHORT_EMA10_THRESH  - 5

        if long_trigger or (current != 1 and long_sustain and cur20 > 55):
            current = 1
        elif short_trigger or (current != -1 and short_sustain):
            current = -1

        # Exit rules (move to CASH from LONG or SHORT)
        if current == 1 and cur50 < SHORT_EMA50_THRESH and cur10 < 45:
            current = 0
        if current == -1 and cur50 > LONG_EMA50_THRESH and cur20 > LONG_EMA20_THRESH:
            current = 0

        position.iloc[i] = current

    return position


# ---------------------------------------------------------------------------
# BACKTEST
# ---------------------------------------------------------------------------

def backtest(index_prices: pd.Series, signals: pd.Series) -> pd.DataFrame:
    """
    Applies signals (shifted by 1 day — trade on next open) to index returns.
    Shorting = -1 * daily return.
    """
    df = pd.DataFrame({
        "close"   : index_prices,
        "signal"  : signals,
    }).dropna()

    df["ret"]          = df["close"].pct_change()
    df["signal_lag"]   = df["signal"].shift(1).fillna(0)          # execute next day
    df["strat_ret"]    = df["signal_lag"] * df["ret"]
    df["bnh_equity"]   = INITIAL_CAPITAL * (1 + df["ret"]).cumprod()
    df["strat_equity"] = INITIAL_CAPITAL * (1 + df["strat_ret"]).cumprod()
    return df


def compute_stats(bt: pd.DataFrame) -> dict:
    strat = bt["strat_ret"].dropna()
    bnh   = bt["ret"].dropna()

    def cagr(eq):
        years = len(eq) / 252
        return (eq.iloc[-1] / INITIAL_CAPITAL) ** (1 / years) - 1 if years > 0 else 0

    def max_dd(eq):
        roll_max = eq.cummax()
        dd = (eq - roll_max) / roll_max
        return dd.min()

    def sharpe(r):
        return (r.mean() / r.std()) * np.sqrt(252) if r.std() > 0 else 0

    trades = bt[bt["signal_lag"] != 0].copy()
    wins   = (trades["strat_ret"] > 0).sum()

    return {
        "Strategy CAGR %"    : round(cagr(bt["strat_equity"]) * 100, 2),
        "Buy & Hold CAGR %"  : round(cagr(bt["bnh_equity"])   * 100, 2),
        "Strategy Max DD %"  : round(max_dd(bt["strat_equity"]) * 100, 2),
        "B&H Max DD %"       : round(max_dd(bt["bnh_equity"])   * 100, 2),
        "Strategy Sharpe"    : round(sharpe(strat), 2),
        "B&H Sharpe"         : round(sharpe(bnh),   2),
        "Win Rate %"         : round(wins / len(trades) * 100, 1) if len(trades) else 0,
        "Days Long"          : int((bt["signal_lag"] == 1).sum()),
        "Days Short"         : int((bt["signal_lag"] == -1).sum()),
        "Days Cash"          : int((bt["signal_lag"] == 0).sum()),
    }


def print_stats(stats: dict, bt: pd.DataFrame) -> None:
    start = bt.index[0].date()
    end   = bt.index[-1].date()
    print("\n" + "=" * 58)
    print(f"  BACKTEST  {start} to {end}  (Nifty 50)")
    print("=" * 58)
    for k, v in stats.items():
        print(f"  {k:<22} {str(v):>10}")
    print("=" * 58)

    # Print recent signal history
    sig = bt[bt["signal"] != bt["signal"].shift(1)].tail(15)
    print("\n  RECENT SIGNAL CHANGES (last 15 transitions)")
    print(f"  {'Date':<14} {'Signal':<10} {'Breadth50':>10}")
    print(f"  {'-'*14} {'-'*10} {'-'*10}")
    for idx, row in sig.iterrows():
        label = {1: "LONG", -1: "SHORT", 0: "CASH"}[row["signal"]]
        print(f"  {str(idx.date()):<14} {label:<10}")
    print()


# ---------------------------------------------------------------------------
# CHART
# ---------------------------------------------------------------------------

SIG_COLOR = {1: "#4CAF50", -1: "#F44336", 0: "#9E9E9E"}
SIG_LABEL = {1: "LONG", -1: "SHORT", 0: "CASH"}


def find_tops_bottoms(prices: pd.Series, prominence: float = 0.04, distance: int = 15):
    """
    Detect significant peaks (tops) and troughs (bottoms) in a price series.
    prominence : minimum % move required to qualify (0.04 = 4%)
    distance   : minimum bars between two peaks/troughs
    """
    arr  = prices.values
    prom = prominence * arr.mean()

    peak_idx,   _ = find_peaks( arr, prominence=prom, distance=distance)
    trough_idx, _ = find_peaks(-arr, prominence=prom, distance=distance)

    tops    = prices.iloc[peak_idx]
    bottoms = prices.iloc[trough_idx]
    return tops, bottoms


def _annotate_extremes(ax, tops: pd.Series, bottoms: pd.Series,
                       breadth: pd.DataFrame, y_offset_frac: float = 0.02):
    """Draw TOP / BOTTOM labels with breadth values on the price panel."""
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    offset  = y_range * y_offset_frac

    for dt, price in tops.items():
        b50 = breadth["b50"].get(dt, float("nan"))
        label = f"TOP\n{int(price):,}\nb50={b50:.0f}%"
        ax.annotate(
            label, xy=(dt, price),
            xytext=(0, 18), textcoords="offset points",
            ha="center", va="bottom", fontsize=7, color="#B71C1C", fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="#B71C1C", lw=1.2),
        )

    for dt, price in bottoms.items():
        b50 = breadth["b50"].get(dt, float("nan"))
        label = f"BOT\n{int(price):,}\nb50={b50:.0f}%"
        ax.annotate(
            label, xy=(dt, price),
            xytext=(0, -24), textcoords="offset points",
            ha="center", va="top", fontsize=7, color="#1B5E20", fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color="#1B5E20", lw=1.2),
        )


def _mark_breadth_extremes(ax, tops: pd.Series, bottoms: pd.Series, breadth: pd.DataFrame):
    """Drop vertical dashed lines on the breadth panel at every top/bottom date."""
    for dt in tops.index:
        ax.axvline(dt, color="#B71C1C", linewidth=0.8, linestyle="--", alpha=0.6)
    for dt in bottoms.index:
        ax.axvline(dt, color="#1B5E20", linewidth=0.8, linestyle="--", alpha=0.6)


def plot_signals(bt: pd.DataFrame, breadth: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                   gridspec_kw={"height_ratios": [2, 1.5]})
    fig.suptitle("Market Breadth — Tops & Bottoms with EMA Breadth", fontsize=13, fontweight="bold")

    # ── detect tops & bottoms ─────────────────────────────────────────────
    tops, bottoms = find_tops_bottoms(bt["close"], prominence=0.035, distance=20)

    # ── Panel 1: Nifty 50 + signal shading + annotations ─────────────────
    ax1.plot(bt.index, bt["close"], color="#37474F", linewidth=1.4, label="Nifty 50", zorder=3)
    _shade_signals(ax1, bt)
    ax1.set_ylabel("Nifty 50", fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.35, zorder=1)

    # annotate after setting ylim so offset calculations are correct
    ax1.set_ylim(bt["close"].min() * 0.96, bt["close"].max() * 1.05)
    bd_aligned = breadth.reindex(bt.index).ffill()
    _annotate_extremes(ax1, tops, bottoms, bd_aligned)

    legend_h = _legend_patches() + [mpatches.Patch(color="#37474F", label="Nifty 50")]
    ax1.legend(handles=legend_h, loc="upper left", fontsize=8)

    # ── Panel 2: Breadth lines + vertical markers at tops/bottoms ─────────
    bd = breadth.reindex(bt.index)
    ax2.plot(bd.index, bd["b10"], color="#2196F3", linewidth=1.4, label="10 EMA breadth")
    ax2.plot(bd.index, bd["b20"], color="#FF9800", linewidth=1.4, label="20 EMA breadth")
    ax2.plot(bd.index, bd["b50"], color="#4CAF50", linewidth=1.8, label="50 EMA breadth")

    ax2.axhline(LONG_EMA50_THRESH,  color="#4CAF50", linestyle=":", linewidth=0.9, alpha=0.8)
    ax2.axhline(SHORT_EMA50_THRESH, color="#F44336", linestyle=":", linewidth=0.9, alpha=0.8)
    ax2.axhline(50, color="gray", linestyle="--", linewidth=0.7, alpha=0.5)
    ax2.axhspan(70, 100, alpha=0.06, color="green")
    ax2.axhspan(0,  30,  alpha=0.06, color="red")

    _mark_breadth_extremes(ax2, tops, bottoms, bd_aligned)

    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% Above EMA", fontsize=9)
    ax2.set_xlabel("Date", fontsize=9)
    ax2.legend(loc="upper left", fontsize=8, ncol=3)
    ax2.grid(True, linestyle="--", alpha=0.35)

    # ── x-axis formatting ─────────────────────────────────────────────────
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    out = "breadth_signals.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Chart saved: {out}")
    plt.show()


def _shade_signals(ax, bt):
    sig = bt["signal_lag"]
    prev_val, prev_idx = sig.iloc[0], bt.index[0]
    for i in range(1, len(sig)):
        if sig.iloc[i] != prev_val or i == len(sig) - 1:
            color = SIG_COLOR.get(prev_val, "#9E9E9E")
            ax.axvspan(prev_idx, bt.index[i], alpha=0.12, color=color)
            prev_val, prev_idx = sig.iloc[i], bt.index[i]


def _legend_patches():
    return [mpatches.Patch(color=SIG_COLOR[k], alpha=0.4, label=SIG_LABEL[k])
            for k in [1, 0, -1]]


# ---------------------------------------------------------------------------
# SIGNAL SUMMARY TABLE
# ---------------------------------------------------------------------------

def build_signal_table(bt: pd.DataFrame, breadth: pd.DataFrame) -> pd.DataFrame:
    """Extract all signal change events with context breadth values."""
    changes = bt[bt["signal"] != bt["signal"].shift(1)].copy()
    bd = breadth.reindex(changes.index)
    changes["b10"] = bd["b10"].values
    changes["b20"] = bd["b20"].values
    changes["b50"] = bd["b50"].values
    changes["label"] = changes["signal"].map(SIG_LABEL)
    out = changes[["label", "close", "b10", "b20", "b50"]].rename(
        columns={"label": "Signal", "close": "Nifty50_Close",
                 "b10": "EMA10_Breadth%", "b20": "EMA20_Breadth%", "b50": "EMA50_Breadth%"})
    return out


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    # 1. Download data
    prices      = fetch_prices(NIFTY_500_SAMPLE, LOOKBACK_DAYS)
    valid       = prices.columns[prices.notna().sum() >= max(EMA_PERIODS)].tolist()
    prices      = prices[valid]
    print(f"  Stocks with enough history: {len(valid)} / {len(NIFTY_500_SAMPLE)}")

    index_px    = fetch_index(LOOKBACK_DAYS)

    # 2. Compute breadth
    breadth     = compute_breadth(prices)

    # 3. Generate signals
    signals     = generate_signals(breadth)

    # 4. Backtest on index
    aligned_idx = index_px.reindex(breadth.index).ffill()
    bt          = backtest(aligned_idx, signals)

    # 5. Stats + console output
    stats       = compute_stats(bt)
    print_stats(stats, bt)

    # 6. Signal history table
    sig_table   = build_signal_table(bt, breadth)
    sig_table.to_csv("breadth_signals.csv")
    print("Signal log saved: breadth_signals.csv")
    print("\n  ALL SIGNAL TRANSITIONS:")
    print(sig_table.to_string())

    # 7. Chart
    plot_signals(bt, breadth)

    return bt, breadth, sig_table


if __name__ == "__main__":
    bt, breadth, signals = main()
