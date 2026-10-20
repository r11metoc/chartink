"""
Market Breadth Analysis using 10 EMA, 20 EMA, and 50 EMA

Measures what percentage of stocks in an index are trading above
each EMA threshold — a proxy for the overall health of the market.

Data source : yfinance (NSE-listed stocks via Yahoo Finance suffix ".NS")
Default universe: Nifty 500 constituents (configurable)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Default symbol list — replace with your preferred universe.
# Format: Yahoo Finance tickers (e.g. "RELIANCE.NS" for NSE)
# A small representative sample is provided; extend as needed.
NIFTY_500_SAMPLE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ULTRACEMCO.NS", "ONGC.NS",
    "NTPC.NS", "POWERGRID.NS", "TECHM.NS", "HCLTECH.NS", "NESTLEIND.NS",
    "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS", "BPCL.NS", "COALINDIA.NS",
    "M&M.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "ADANIENT.NS", "ADANIPORTS.NS", "GRASIM.NS", "BRITANNIA.NS", "PIDILITIND.NS",
    "HAVELLS.NS", "VOLTAS.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS",
    "INDUSINDBK.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "PNB.NS",
    "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS", "MOTHERSON.NS", "BOSCHLTD.NS",
    "EICHERMOT.NS", "TATACONSUM.NS", "UPL.NS", "PIIND.NS", "DMART.NS",
    "NAUKRI.NS", "PAYTM.NS", "ETERNAL.NS", "POLICYBZR.NS", "IRCTC.NS",
    "MUTHOOTFIN.NS", "CHOLAFIN.NS", "SBICARD.NS", "BAJAJFINSV.NS", "LICHSGFIN.NS",
    "RECLTD.NS", "PFC.NS", "IRFC.NS", "NHPC.NS", "SJVN.NS",
    "TATAPOWER.NS", "ADANIGREEN.NS", "TORNTPOWER.NS", "CESC.NS", "JINDALSTEL.NS",
    "SAIL.NS", "HINDALCO.NS", "VEDL.NS", "NATIONALUM.NS", "MOIL.NS",
    "APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "METROPOLIS.NS", "LAURUSLABS.NS",
    "BIOCON.NS", "AUROPHARMA.NS", "ALKEM.NS", "TORNTPHARM.NS", "IPCALAB.NS",
    "PAGEIND.NS", "UNITDSPR.NS", "RADICO.NS", "TRENT.NS", "APLAPOLLO.NS",
]

EMA_PERIODS = [10, 20, 50]
LOOKBACK_DAYS = 120       # trading days of history to download
PLOT_DAYS = 60            # days to show on the breadth chart
INDEX_TICKER = "^NSEI"   # Nifty 50 as the benchmark index


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def download_prices(tickers: list[str], lookback: int) -> pd.DataFrame:
    """Download adjusted close prices for all tickers."""
    end = datetime.today()
    start = end - timedelta(days=int(lookback * 1.5))  # buffer for weekends/holidays
    print(f"Downloading {len(tickers)} tickers from {start.date()} to {end.date()} ...")
    raw = yf.download(
        tickers,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]]
    prices = prices.dropna(how="all").tail(lookback)
    return prices


def compute_breadth(prices: pd.DataFrame, ema_periods: list[int]) -> pd.DataFrame:
    """
    For each trading day, compute the % of stocks whose Close > EMA(n).
    Returns a DataFrame with columns like 'pct_above_ema10', etc.
    """
    records = {}
    for period in ema_periods:
        ema_df = prices.apply(lambda col: compute_ema(col.dropna(), period)
                              .reindex(prices.index))
        above = (prices > ema_df).sum(axis=1)
        total = prices.notna().sum(axis=1)
        pct = (above / total * 100).round(2)
        records[f"pct_above_ema{period}"] = pct

    breadth = pd.DataFrame(records).dropna(how="all")
    return breadth


def classify_market(row: pd.Series) -> str:
    """Simple regime classifier based on breadth thresholds."""
    e10, e20, e50 = row["pct_above_ema10"], row["pct_above_ema20"], row["pct_above_ema50"]
    if e10 >= 70 and e20 >= 60 and e50 >= 55:
        return "Strong Bull"
    elif e10 >= 55 and e50 >= 45:
        return "Moderate Bull"
    elif e10 <= 30 and e20 <= 35 and e50 <= 40:
        return "Strong Bear"
    elif e10 <= 45 and e50 <= 45:
        return "Moderate Bear"
    else:
        return "Neutral / Choppy"


def print_summary(breadth: pd.DataFrame) -> None:
    latest = breadth.iloc[-1]
    prev   = breadth.iloc[-2] if len(breadth) > 1 else latest
    regime = classify_market(latest)

    print("\n" + "=" * 60)
    print(f"  MARKET BREADTH REPORT  —  {breadth.index[-1].date()}")
    print("=" * 60)
    print(f"  {'EMA':<10} {'Above %':>10}  {'Change':>8}")
    print(f"  {'-'*10} {'-'*10}  {'-'*8}")
    for col in breadth.columns:
        label = col.replace("pct_above_", "").upper()
        val   = latest[col]
        chg   = val - prev[col]
        arrow = "^" if chg > 0 else ("v" if chg < 0 else "-")
        print(f"  {label:<10} {val:>9.1f}%  {arrow}{abs(chg):>6.1f}%")
    print(f"\n  Market Regime : {regime}")
    print("=" * 60 + "\n")


# ---------------------------------------------------------------------------
# PLOTTING
# ---------------------------------------------------------------------------

COLORS = {
    "pct_above_ema10": "#2196F3",   # blue
    "pct_above_ema20": "#FF9800",   # orange
    "pct_above_ema50": "#4CAF50",   # green
}

ZONE_ALPHA = 0.08


def plot_breadth(breadth: pd.DataFrame, index_prices: pd.DataFrame, plot_days: int) -> None:
    df = breadth.tail(plot_days)
    idx_df = index_prices.tail(plot_days)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 9),
        gridspec_kw={"height_ratios": [1, 2]},
        sharex=True,
    )
    fig.suptitle("Market Breadth Analysis  ·  % Stocks Above EMA", fontsize=14, fontweight="bold")

    # --- top panel: benchmark index ---
    if not idx_df.empty:
        ax1.plot(idx_df.index, idx_df["Close"], color="#37474F", linewidth=1.5, label="Nifty 50")
        ax1.set_ylabel("Nifty 50", fontsize=9)
        ax1.yaxis.set_label_position("right")
        ax1.yaxis.tick_right()
        ax1.legend(loc="upper left", fontsize=8)
        ax1.grid(True, linestyle="--", alpha=0.4)

    # --- bottom panel: breadth lines ---
    labels = {"pct_above_ema10": "10 EMA", "pct_above_ema20": "20 EMA", "pct_above_ema50": "50 EMA"}
    for col, color in COLORS.items():
        if col in df.columns:
            ax2.plot(df.index, df[col], color=color, linewidth=1.8, label=labels[col])

    # Overbought / oversold zones
    ax2.axhspan(70, 100, alpha=ZONE_ALPHA, color="green", label="Overbought (>70%)")
    ax2.axhspan(0,  30,  alpha=ZONE_ALPHA, color="red",   label="Oversold  (<30%)")
    ax2.axhline(50, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)

    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% Stocks Above EMA", fontsize=9)
    ax2.set_xlabel("Date", fontsize=9)
    ax2.legend(loc="upper left", fontsize=8, ncol=3)
    ax2.grid(True, linestyle="--", alpha=0.4)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    # Annotate latest values on the right edge
    last_date = df.index[-1]
    for col, color in COLORS.items():
        if col in df.columns:
            ax2.annotate(
                f"{df[col].iloc[-1]:.1f}%",
                xy=(last_date, df[col].iloc[-1]),
                xytext=(6, 0), textcoords="offset points",
                color=color, fontsize=8, va="center",
            )

    plt.tight_layout()

    out_path = "market_breadth.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved: {out_path}")
    plt.show()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(tickers: list[str] | None = None) -> pd.DataFrame:
    symbols = tickers or NIFTY_500_SAMPLE

    # Download stock prices
    prices = download_prices(symbols, LOOKBACK_DAYS)
    valid = prices.columns[prices.notna().sum() >= max(EMA_PERIODS)].tolist()
    print(f"  Valid symbols with enough history: {len(valid)} / {len(symbols)}")
    prices = prices[valid]

    # Download index for reference panel
    end = datetime.today()
    start = end - timedelta(days=int(LOOKBACK_DAYS * 1.5))
    index_raw = yf.download(
        INDEX_TICKER,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )
    if isinstance(index_raw.columns, pd.MultiIndex):
        close = index_raw["Close"]
        # MultiIndex download for single ticker gives a DataFrame with one column
        index_prices = close.iloc[:, 0].to_frame(name="Close") if isinstance(close, pd.DataFrame) else close.to_frame(name="Close")
    else:
        index_prices = index_raw[["Close"]]

    # Compute breadth
    breadth = compute_breadth(prices, EMA_PERIODS)

    # Add regime column
    breadth["regime"] = breadth.apply(classify_market, axis=1)

    # Console summary
    print_summary(breadth.drop(columns="regime"))

    # Rolling 5-day averages (smoothed breadth)
    for col in [f"pct_above_ema{p}" for p in EMA_PERIODS]:
        breadth[f"{col}_5d"] = breadth[col].rolling(5).mean().round(2)

    # Save to CSV
    csv_path = "market_breadth.csv"
    breadth.to_csv(csv_path)
    print(f"Data saved:  {csv_path}")

    # Plot
    plot_breadth(breadth[[f"pct_above_ema{p}" for p in EMA_PERIODS]], index_prices, PLOT_DAYS)

    return breadth


if __name__ == "__main__":
    result = main()
