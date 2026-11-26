"""Learn short-term trading on one stock, tested honestly (walk-forward).

Usage: python stock_learn.py ENGINERSIN [years=8]

Long-only daily swing trading, bought and sold at the next open, 0.25% costs
a round trip. Four families of rules, each with a few settings:

  trend      : hold while the fast EMA is above the slow EMA
  breakout   : buy a close above the N-day high, sell a close below the M-day low
  dip        : buy when RSI(2) is very low (short-term oversold), sell when the
               close gets back above the 5-day average or after 10 days
  ml         : logistic regression on 18 price/volume facts, hold while it
               says the next 5 days are likelier up than down

Walk-forward: learn on 2 years, trade the next 6 months with what was
learned, slide 6 months, repeat. Only the traded (unseen) 6-month stretches
count. "Auto" picks, each time, the family and setting that did best in the
2 years before. Everything is compared with buy-and-hold over the same days.

Writes reports/learn_<SYMBOL>.md and prints it.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import breakout_sim as bs

ROOT = Path(__file__).resolve().parent.parent
COST = bs.COST_PCT / 100      # per round trip
TRAIN, TEST = 504, 126        # sessions: 2 years learn, 6 months trade


def _rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def positions(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Every rule's wanted position (1 = hold) decided at each close."""
    c = df["Close"]
    out = {}
    for f in (5, 10, 20):
        for s in (20, 30, 50):
            if f < s:
                out[f"trend EMA{f}/{s}"] = (c.ewm(span=f, adjust=False).mean() > c.ewm(span=s, adjust=False).mean()).astype(float)
    for n in (10, 20, 55):
        hi = df["High"].rolling(n).max().shift(1)
        for m in (5, 10, 20):
            lo = df["Low"].rolling(m).min().shift(1)
            pos, p = [], 0.0
            for cc, h, lw in zip(c, hi, lo):
                if p == 0 and cc > h:
                    p = 1.0
                elif p == 1 and cc < lw:
                    p = 0.0
                pos.append(p)
            out[f"breakout {n}/{m}"] = pd.Series(pos, index=df.index)
    r2, sma5 = _rsi(c, 2), c.rolling(5).mean()
    for x in (5, 10, 20):
        pos, p, held = [], 0.0, 0
        for cc, r, m5 in zip(c, r2, sma5):
            if p == 0 and r < x:
                p, held = 1.0, 0
            elif p == 1:
                held += 1
                if cc > m5 or held >= 10:
                    p = 0.0
            pos.append(p)
        out[f"dip RSI2<{x}"] = pd.Series(pos, index=df.index)
    return out


def ml_positions(df: pd.DataFrame, thresholds=(0.5, 0.55)) -> dict[str, pd.Series]:
    """Walk-forward logistic regression: each test block uses a model trained
    only on the TRAIN sessions before it (labels that were known by then)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    f = bs.indicator_frame(df).drop(columns=["log_turnover"], errors="ignore")
    f["rsi2"] = _rsi(df["Close"], 2)
    f["gap"] = (df["Open"] / df["Close"].shift(1) - 1) * 100
    y = (df["Open"].shift(-6) / df["Open"].shift(-1) > 1).astype(float)  # next 5 sessions, from the next open
    y[df.index[-6:]] = np.nan
    proba = pd.Series(np.nan, index=df.index)
    for start in range(TRAIN + 200, len(df), TEST):
        tr = slice(start - TRAIN, start - 6)  # the last 5 labels aren't known yet at `start`
        X, yy = f.iloc[tr], y.iloc[tr]
        ok = X.notna().all(axis=1) & yy.notna()
        if ok.sum() < 200 or yy[ok].nunique() < 2:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=500)).fit(X[ok], yy[ok])
        Xt = f.iloc[start:start + TEST]
        good = Xt.notna().all(axis=1)
        proba.loc[Xt.index[good]] = m.predict_proba(Xt[good])[:, 1]
    return {f"ml p>{t:.2f}": (proba > t).astype(float).where(proba.notna()) for t in thresholds}


def daily_returns(df: pd.DataFrame, pos: pd.Series) -> pd.Series:
    """Open-to-open returns: a decision at close t is traded at open t+1."""
    oo = df["Open"].shift(-1) / df["Open"] - 1
    held = pos.shift(1).fillna(0)
    trades = held.diff().abs().fillna(held.abs())
    return (held * oo - trades * COST / 2).fillna(0)


def stats(r: pd.Series, held: pd.Series | None = None) -> dict:
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    out = {"total": (eq.iloc[-1] - 1) * 100, "cagr": (eq.iloc[-1] ** (1 / yrs) - 1) * 100 if yrs > 0 else np.nan,
           "dd": (eq / eq.cummax() - 1).min() * 100,
           "sharpe": r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0.0}
    if held is not None:
        h = held.fillna(0)
        entries = ((h.diff() > 0) | ((h > 0) & (h.shift(1).isna()))).sum()
        out["trades"] = int(entries)
        out["in"] = h.mean() * 100
    return out


def walk_forward(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], pd.Series]:
    rules = {**positions(df), **ml_positions(df)}
    rets = {k: daily_returns(df, p.fillna(0)) for k, p in rules.items()}
    first = TRAIN + 200  # 200 sessions of warm-up for the averages
    blocks, picks = [], []
    auto = pd.Series(0.0, index=df.index)
    auto_pos = pd.Series(0.0, index=df.index)
    for start in range(first, len(df) - 1, TEST):
        tr, te = slice(start - TRAIN, start), slice(start, min(start + TEST, len(df)))
        score = {k: stats(r.iloc[tr])["sharpe"] for k, r in rets.items() if rules[k].iloc[tr].notna().all()}
        best = max(score, key=score.get)
        picks.append(f"{df.index[start]:%b %Y}: {best} (learned Sharpe {score[best]:.2f})")
        auto.iloc[te] = rets[best].iloc[te]
        auto_pos.iloc[te] = rules[best].fillna(0).iloc[te]
        blocks.append(te)
    test_idx = df.index[first:]
    rows = []
    bh = (df["Open"].shift(-1) / df["Open"] - 1).fillna(0)
    rows.append({"rule": "Buy and hold", **stats(bh.loc[test_idx]), "trades": 1, "in": 100.0})
    rows.append({"rule": "AUTO (re-learned every 6 months)", **stats(auto.loc[test_idx], auto_pos.shift(1).loc[test_idx])})
    for k, r in rets.items():
        rows.append({"rule": k, **stats(r.loc[test_idx], rules[k].fillna(0).shift(1).loc[test_idx])})
    return pd.DataFrame(rows), picks, test_idx


def report(symbol: str, df: pd.DataFrame) -> str:
    if len(df) < TRAIN + 200 + TEST:
        return f"# {symbol}\n\nNot enough history ({len(df)} sessions; need {TRAIN + 200 + TEST}). Try more years.\n"
    res, picks, test_idx = walk_forward(df)
    bh = res.iloc[0]
    fixed = res.iloc[2:].sort_values("sharpe", ascending=False)
    L = [f"# Learning to swing-trade {symbol}", "",
         f"Prices {df.index[0]:%d %b %Y} to {df.index[-1]:%d %b %Y}. Traded (unseen) stretch: "
         f"{test_idx[0]:%d %b %Y} to {test_idx[-1]:%d %b %Y}, {len(test_idx) / 252:.1f} years. "
         "Long only, next-open fills, 0.25% costs a round trip, no taxes.", "",
         "| Rule | Return | Per year | Worst fall | Sharpe | Trades | Time in |", "|---|---|---|---|---|---|---|"]
    for _, r in pd.concat([res.iloc[:2], fixed]).iterrows():
        L.append(f"| {r['rule']} | {r['total']:+.0f}% | {r['cagr']:+.1f}% | {r['dd']:.0f}% | {r['sharpe']:.2f} | "
                 f"{int(r['trades'])} | {r['in']:.0f}% |")
    auto = res.iloc[1]
    beat = auto["cagr"] > bh["cagr"]
    safer = auto["dd"] > bh["dd"]
    L += ["", "## Verdict", "",
          f"- The honest number is **AUTO**: it only uses what could be known at the time. "
          f"{'It beat' if beat else 'It did not beat'} buy-and-hold on return ({auto['cagr']:+.1f}% vs {bh['cagr']:+.1f}% a year) "
          f"and its worst fall was {'smaller' if safer else 'not smaller'} ({auto['dd']:.0f}% vs {bh['dd']:.0f}%).",
          f"- The best single rule in hindsight ({fixed.iloc[0]['rule']}) is picked after the fact: expect less from it in future.",
          "- If AUTO keeps switching rule every 6 months, there is no stable pattern to learn in this stock.", "",
          "## What AUTO picked each time", ""] + [f"- {p}" for p in picks]
    return "\n".join(L) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    from market_data import fetch_daily
    symbol = sys.argv[1].strip().upper()
    years = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    df = fetch_daily([symbol], (date.today() - timedelta(days=int(365.25 * years))).isoformat()).get(symbol)
    if df is None or df.empty:
        print(f"No prices for {symbol} on Yahoo.")
        return 1
    text = report(symbol, df)
    out = ROOT / "reports" / f"learn_{symbol}.md"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
