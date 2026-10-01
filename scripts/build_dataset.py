"""Turn Chartink backtest hits into a labeled trade dataset.

For every hit in data/backtest/*.csv, plus every live trigger the bot caught
(data/chartink.db), so the dataset keeps growing with forward data: fetch daily prices, find the signal
bar and trigger price (breakout_sim.py), compute point-in-time features,
and store the price path that followed. Writes:

  data/model/signals.csv    one row per hit: levels, features, data status
  data/model/paths.csv.gz   the FORWARD_DAYS sessions after each signal bar

Storing the raw forward path (instead of just one outcome) lets
signal_model.py try different entry windows / exit rules without
re-downloading prices, which matters because only GitHub Actions can reach
Yahoo Finance.

Usage: python build_dataset.py [backtest_dir]
"""

from __future__ import annotations

import csv
import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

import breakout_sim as bs
import db
from market_data import BENCHMARK_TICKERS, NIFTY_TICKER, fetch_daily
from paper import live_hit_date

ROOT = Path(__file__).resolve().parent.parent
BACKTEST_DIR = ROOT / "data" / "backtest"
MODEL_DIR = ROOT / "data" / "model"
HISTORY_DAYS = 400  # calendar days of lookback before the first hit (SMA200, 52w high)


def load_hits(backtest_dir: Path = BACKTEST_DIR) -> pd.DataFrame:
    rows = []
    for path in sorted(backtest_dir.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rows.append({
                    "scanner_name": path.stem,
                    "hit_date": pd.to_datetime(r["Date"], format="%d-%m-%Y"),
                    "symbol": r["Symbol"].strip().upper(),
                    "marketcap": r.get("Marketcapname", "").strip(),
                    "sector": r.get("Sector", "").strip(),
                })
    hits = pd.DataFrame(rows)
    hits["source"] = "backtest"
    live = live_hits()
    if not live.empty:
        hits = pd.concat([hits, live], ignore_index=True)
    # A weekly scanner's hit is the week, whatever day it was recorded on.
    hits["_key"] = [d - pd.Timedelta(days=d.weekday()) if bs.is_weekly(sc) else d
                    for sc, d in zip(hits["scanner_name"], hits["hit_date"])]
    hits = hits.drop_duplicates(["scanner_name", "_key", "symbol"]).drop(columns="_key")  # backtest rows win
    return hits.sort_values(["hit_date", "scanner_name", "symbol"]).reset_index(drop=True)


def live_hits() -> pd.DataFrame:
    """Triggers the bot caught live, dated to their session, with Chartink's
    market-cap tier and sector where its backtest exports know the stock."""
    if not db.DB_PATH.exists():
        return pd.DataFrame()
    conn = db.connect()
    rows = []
    for e in db.breakouts_since(conn, "2000-01-01"):
        known = conn.execute("SELECT marketcap, sector FROM backtest_hits WHERE symbol = ? AND marketcap != '' "
                             "ORDER BY hit_date DESC LIMIT 1", (e["symbol"],)).fetchone()
        rows.append({"scanner_name": e["scanner_name"], "hit_date": pd.Timestamp(live_hit_date(e["detected_at"])),
                     "symbol": e["symbol"], "marketcap": known[0] if known else "",
                     "sector": known[1] if known else "", "source": "live"})
    conn.close()
    return pd.DataFrame(rows)


def approx_signal_date(row) -> pd.Timestamp:
    """Signal availability date without price data (used for history
    features when a symbol has no prices): end of week for weekly hits."""
    if bs.is_weekly(row["scanner_name"]):
        return row["hit_date"] + pd.Timedelta(days=4 - row["hit_date"].weekday())
    return row["hit_date"]


def build(hits: pd.DataFrame, prices: dict[str, pd.DataFrame], nifty: pd.DataFrame | None):
    signal_rows, path_rows = [], []
    indicators = {s: bs.indicator_frame(df) for s, df in prices.items()}

    for i, hit in hits.iterrows():
        base = hit.to_dict()
        base["hit_id"] = i
        df = prices.get(hit["symbol"])
        sig = bs.signal_bar(df, hit["hit_date"], bs.is_weekly(hit["scanner_name"])) if df is not None else None
        if sig is None:
            base["data_status"] = "no_price_data" if df is None else "date_not_in_data"
            base["signal_date"] = approx_signal_date(hit)
            signal_rows.append(base)
            continue

        base.update(
            data_status="ok",
            signal_date=sig["signal_date"],
            trigger=sig["trigger"],
            bar_low=sig["bar_low"],
            bar_close=sig["bar_close"],
        )
        base.update(indicators[hit["symbol"]].iloc[sig["end_pos"]].to_dict())
        base.update(bs.bar_features(sig))
        base.update(bs.market_features(nifty, sig["signal_date"]))
        signal_rows.append(base)

        fwd = df.iloc[sig["end_pos"] + 1: sig["end_pos"] + 1 + bs.FORWARD_DAYS]
        for k, (d, bar) in enumerate(fwd.iterrows()):
            path_rows.append({"hit_id": i, "offset": k, "date": d.date().isoformat(),
                              "open": bar["Open"], "high": bar["High"],
                              "low": bar["Low"], "close": bar["Close"]})

    signals = pd.DataFrame(signal_rows)
    signals[["prior_hits_same_scanner_180d", "other_scanner_hits_10d"]] = bs.history_features(signals)
    return signals, pd.DataFrame(path_rows)


def main() -> int:
    backtest_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else BACKTEST_DIR
    hits = load_hits(backtest_dir)
    symbols = sorted(hits["symbol"].unique())
    start = (hits["hit_date"].min() - timedelta(days=HISTORY_DAYS)).date().isoformat()
    print(f"{len(hits)} hits, {len(symbols)} symbols, prices from {start}")

    prices = fetch_daily(symbols, start)
    indices = fetch_daily(BENCHMARK_TICKERS, start)
    nifty = indices.get(NIFTY_TICKER)
    if nifty is None:
        print("WARNING: Nifty index data unavailable; market features will be blank")

    signals, paths = build(hits, prices, nifty)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    signals.to_csv(MODEL_DIR / "signals.csv", index=False, float_format="%.4f")
    paths.to_csv(MODEL_DIR / "paths.csv.gz", index=False, float_format="%.4f")
    # Index closes, to judge trades against simply holding the market.
    pd.DataFrame({t: df["Close"] for t, df in indices.items()}).rename_axis("date").to_csv(
        MODEL_DIR / "index_closes.csv", float_format="%.2f")
    print(signals["data_status"].value_counts().to_string())
    print(f"Wrote {len(signals)} signals and {len(paths)} path rows to {MODEL_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
