"""Scanner hits: every row of the Chartink backtest exports
(data/backtest/<scanner>.csv) plus every trigger the bot caught live
(data/chartink.db), one per scanner, stock and day (one per week for the
weekly scanner)."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

import breakout_sim as bs
import db
from live_signals import live_hit_date

ROOT = Path(__file__).resolve().parent.parent
BACKTEST_DIR = ROOT / "data" / "backtest"


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
