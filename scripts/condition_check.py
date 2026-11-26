"""Which scan conditions actually help? Split a scan's trades by a condition.

Usage: python condition_check.py "<Chartink backtest export.csv>"

For every hit it fetches prices (Yahoo), trades it two ways (the bot's live
rule, and buy at the next open with a +5% target / 15% stop), then splits the
trades by conditions measured on the signal day:

- the conditions removed from Bullish_Scanner_x on 15 Nov 2026 (price above
  ₹2,000, close below EMA50, EMA10 below EMA20, close more than 10% above EMA10,
  index funds),
- weekly RSI(14) > 65 measured honestly (this week only up to the signal day)
  vs as a backtest sees it (the whole week, including days after the signal):
  the gap shows how much a weekly condition flatters a backtest,
- daily RSI(14) bands, distance from the 52-week high, market cap.

A condition worth having shows a clearly better average trade on its "yes"
side, with enough trades on both sides. Writes reports/conditions_<file>.md.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs
import dipzone
import scan_quality as sq

ROOT = Path(__file__).resolve().parent.parent


def _rsi(c: pd.Series, n: int = 14) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def weekly_rsi(df: pd.DataFrame, pos: int) -> tuple[float, float]:
    """(honest, full-week) weekly RSI(14) at daily bar `pos`."""
    c = df["Close"]
    day = df.index[pos]
    wk = c.resample("W-FRI").last().dropna()
    this_week = wk.index[wk.index >= day][0] if (wk.index >= day).any() else None
    done = wk[wk.index < (this_week if this_week is not None else day + pd.Timedelta(days=7))]
    honest = pd.concat([done, pd.Series([c.iloc[pos]], index=[day])])
    full = wk[wk.index <= this_week] if this_week is not None else honest
    h, f = _rsi(honest).iloc[-1], _rsi(full).iloc[-1]
    return float(h), float(f)


def features(hits: pd.DataFrame, prices: dict) -> pd.DataFrame:
    rows = []
    for _, h in hits.iterrows():
        df = prices.get(h["symbol"])
        sig = bs.signal_bar(df, h["hit_date"], False) if df is not None else None
        if sig is None or sig["end_pos"] < 60:
            continue
        p = sig["end_pos"]
        c = df["Close"]
        e10 = c.ewm(span=10, adjust=False).mean().iloc[p]
        e20 = c.ewm(span=20, adjust=False).mean().iloc[p]
        e50 = c.ewm(span=50, adjust=False).mean().iloc[p]
        wr_h, wr_f = weekly_rsi(df.iloc[:min(len(df), p + 6)], p)
        close = float(c.iloc[p])
        rows.append({"symbol": h["symbol"], "hit_date": pd.Timestamp(h["hit_date"]),
                     "price>2000": close > 2000, "close<EMA50": close < e50, "EMA10<EMA20": e10 < e20,
                     "close>1.1xEMA10": close > 1.1 * e10, "index fund": h["sector"].lower() == "indices",
                     "weekly RSI>65 (honest)": wr_h > 65, "weekly RSI>65 (full week, as backtest)": wr_f > 65,
                     "daily RSI": float(_rsi(c).iloc[p]),
                     "off 52w high %": dipzone.dist_52w_high(df, p) or 0.0})
    return pd.DataFrame(rows)


def split_table(t: pd.DataFrame, col: str, label: str) -> str:
    a, b = t[t[col]], t[~t[col]]
    f = lambda x, k: "–" if x.empty else f"{len(x)} · {(x[k] > 0).mean() * 100:.0f}% · {x[k].mean():+.2f}%"  # noqa: E731
    return f"| {label} | {f(a, 'ret')} | {f(b, 'ret')} | {f(a, 'ret5')} | {f(b, 'ret5')} |"


def report(name: str, hits: pd.DataFrame, prices: dict) -> str:
    live = dipzone.backtest_trades(hits.assign(scanner_name="Bullish_Scanner"), prices)
    quick = sq.other_exits(hits, prices, False)["t5w"]
    feats = features(hits, prices)
    live = live.merge(feats, on=["symbol", "hit_date"], how="inner")
    quick = quick.assign(hit_key=1)
    q = hits[["symbol", "hit_date"]].merge(feats, on=["symbol", "hit_date"])
    # match the quick-exit trades to hits by symbol and entry = next session after the hit
    qt = []
    for _, r in quick.iterrows():
        cand = q[(q["symbol"] == r["symbol"]) & (q["hit_date"] < r["entry_date"]) &
                 (q["hit_date"] >= r["entry_date"] - pd.Timedelta(days=7))]
        if not cand.empty:
            qt.append({**cand.iloc[-1].to_dict(), "ret5": r["ret"]})
    qt = pd.DataFrame(qt)
    t = live.merge(qt[["symbol", "hit_date", "ret5"]], on=["symbol", "hit_date"], how="left")
    t["ret5"] = t["ret5"].fillna(t["ret5"].mean())
    t["daily RSI 65-75"] = t["daily RSI"].between(65, 75)
    t["daily RSI > 75"] = t["daily RSI"] > 75
    t["within 5% of 52w high"] = t["off 52w high %"] >= -5
    L = [f"# Which conditions help: {name}", "",
         f"{len(t):,} closed trades with prices. Each cell: trades · won · average trade. "
         "'Live rule' = the bot's buy-stop and 30-day EMA exit; '+5%/15%' = buy at the next open, "
         "+5% target, 15% stop.", "",
         "| Condition on the signal day | Yes: live rule | No: live rule | Yes: +5%/15% | No: +5%/15% |",
         "|---|---|---|---|---|"]
    for col in ["price>2000", "close<EMA50", "EMA10<EMA20", "close>1.1xEMA10", "index fund",
                "weekly RSI>65 (honest)", "weekly RSI>65 (full week, as backtest)",
                "daily RSI 65-75", "daily RSI > 75", "within 5% of 52w high"]:
        L.append(split_table(t, col, col))
    L += ["", "| Market cap | Live rule | +5%/15% |", "|---|---|---|"]
    caps = hits.drop_duplicates("symbol").set_index("symbol")["marketcap"]
    t["cap"] = t["symbol"].map(caps)
    for k, g in t.groupby("cap"):
        L.append(f"| {k or 'blank'} | {len(g)} · {(g['ret'] > 0).mean() * 100:.0f}% · {g['ret'].mean():+.2f}% | "
                 f"{(g['ret5'] > 0).mean() * 100:.0f}% · {g['ret5'].mean():+.2f}% |")
    rep = t["weekly RSI>65 (full week, as backtest)"] & ~t["weekly RSI>65 (honest)"]
    L += ["", f"Repaint check: {rep.mean() * 100:.0f}% of these trades pass weekly RSI > 65 only when the "
          "whole week is counted (days after the signal). A backtest with a weekly condition includes them; "
          "live trading would not have had them."]
    return "\n".join(L) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    path = Path(sys.argv[1])
    hits = sq.load(path)
    start = (hits["hit_date"].min() - timedelta(days=dipzone.HISTORY_DAYS)).date().isoformat()
    prices = fetch_daily(sorted(hits["symbol"].unique()), start)
    text = report(path.stem, hits, prices)
    out = ROOT / "reports" / f"conditions_{path.stem.replace(' ', '_')}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
