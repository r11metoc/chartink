"""The pullback after a breakout: how it behaves, and ways to buy it.

Run from stock_outcomes.py (it shares the downloaded prices). For every
signal that crossed its trigger (the signal candle's high):

1. Pullback facts: did price come back to the trigger (within 2%) in the
   next 20 sessions, how deep the dip from the post-breakout high was, how
   long it took, and what happened next.
2. Why a stop "close to the buy price" still loses: every round trip of
   the trigger-stop rule split into entry above the trigger (gap-ups),
   exit below the trigger (selling at the next open after a close below
   it, gap-downs) and costs.
3. Buy rules compared on the same signals, all with no target and no time
   limit, new buys allowed for 3 months after the signal, every market cap:
   - breakout   : buy above the trigger, sell on a close below it (the rule
                  tested before), buy again above it
   - breakout5  : same, but the stop is a close 5% below the trigger
   - retest     : after the breakout, wait for a dip to within 2% of the
                  trigger that closes back above it; buy next open; stop on
                  a close 5% below the trigger; repeat on the next retest
   - dip5       : after the breakout, buy next open once the close is 5%
                  below the highest close since the breakout (and still
                  above the stop); stop on a close 5% below the trigger
   - ema20      : after the breakout, buy next open when the low touches the
                  20-day average and the close is back above it; stop on a
                  close 5% below the trigger
   Decisions are made on the daily close and filled at the next open
   (except the breakout rules, which fill when price crosses the trigger).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import breakout_sim as bs

WINDOW = 63          # sessions after the signal in which new buys are allowed
NEAR = 0.02          # "back at the trigger" = low within 2% of it
BUFFER = 0.05        # stop on a close 5% below the trigger
FACT_DAYS = 20       # sessions after the breakout for the pullback facts

RULES = {
    "breakout": "Buy above the trigger, sell on a close below it, buy again above it",
    "breakout5": "Same, stop on a close 5% below the trigger",
    "retest": "Buy the dip back to the trigger (within 2%) that closes above it; stop 5% below",
    "dip5": "Buy a 5% dip from the post-breakout high; stop 5% below the trigger",
    "ema20": "Buy the dip to the 20-day average that closes above it; stop 5% below the trigger",
}


def _close_stop_legs(o, h, l, c, entry_ok, trigger: float, stop: float, cross_fill: bool):
    """Generic long-only loop. `entry_ok(i)` says whether a buy signal is on
    at bar i; with `cross_fill` the buy fills on bar i at max(open, trigger)
    when the high crosses the trigger, otherwise at the open of bar i+1.
    Exit at the next open after a close below `stop`. Returns legs as
    (entry_i, exit_i, entry_px, exit_px, status)."""
    n = len(c)
    legs, pos, e_i, e_px = [], False, 0, 0.0
    sell, buy = False, False
    for i in range(n):
        if pos and sell:
            legs.append((e_i, i, e_px, float(o[i]), "stop"))
            pos, sell = False, False
        if not pos and buy:
            pos, buy, e_i, e_px = True, False, i, float(o[i])
        if not pos:
            if i < WINDOW and entry_ok(i):
                if cross_fill:
                    pos, e_i, e_px = True, i, max(float(o[i]), trigger)
                else:
                    buy = i + 1 < n
                    continue
            else:
                continue
        if c[i] < stop:
            sell = i + 1 < n
            if not sell:
                legs.append((e_i, i, e_px, float(c[i]), "stop"))
                pos = False
    if pos:
        legs.append((e_i, n - 1, e_px, float(c[-1]), "holding"))
    return legs


def _growth(legs) -> float:
    g = 1.0
    for _, _, a, b, _ in legs:
        g *= (b / a) * (1 - bs.COST_PCT / 100)
    return (g - 1) * 100


def run_rules(fwd: pd.DataFrame, trigger: float) -> dict[str, list]:
    o, h, l, c = (fwd[k].to_numpy(dtype=float) for k in ("Open", "High", "Low", "Close"))
    n = len(c)
    broke = np.flatnonzero(h[:WINDOW] > trigger)
    out = {}
    out["breakout"] = _close_stop_legs(o, h, l, c, lambda i: h[i] > trigger, trigger, trigger, True)
    out["breakout5"] = _close_stop_legs(o, h, l, c, lambda i: h[i] > trigger, trigger,
                                        trigger * (1 - BUFFER), True)
    if len(broke) == 0:
        for k in ("retest", "dip5", "ema20"):
            out[k] = []
        return out
    b0 = int(broke[0])
    stop = trigger * (1 - BUFFER)
    hi_close = pd.Series(c).where(np.arange(n) >= b0).cummax().to_numpy()
    ema = fwd["Close"].ewm(span=20, adjust=False).mean().to_numpy()
    out["retest"] = _close_stop_legs(
        o, h, l, c, lambda i: i > b0 and l[i] <= trigger * (1 + NEAR) and c[i] > trigger, trigger, stop, False)
    out["dip5"] = _close_stop_legs(
        o, h, l, c, lambda i: i > b0 and c[i] <= hi_close[i] * (1 - BUFFER) and c[i] > stop, trigger, stop, False)
    out["ema20"] = _close_stop_legs(
        o, h, l, c, lambda i: i > b0 and l[i] <= ema[i] and c[i] > ema[i] and c[i] > stop, trigger, stop, False)
    return out


def pullback_facts(fwd: pd.DataFrame, trigger: float) -> dict | None:
    h, l, c = (fwd[k].to_numpy(dtype=float) for k in ("High", "Low", "Close"))
    broke = np.flatnonzero(h[:WINDOW] > trigger)
    if len(broke) == 0:
        return None
    b0 = int(broke[0])
    seg = slice(b0 + 1, b0 + 1 + FACT_DAYS)
    if len(c[seg]) < FACT_DAYS:
        return None
    lows, highs = l[seg], h[seg]
    touch = np.flatnonzero(lows <= trigger * (1 + NEAR))
    run_hi = np.maximum.accumulate(np.concatenate([[h[b0]], highs]))[1:]
    depth = ((lows / run_hi) - 1).min() * 100
    res = {"retested": len(touch) > 0, "days_to_retest": int(touch[0]) + 1 if len(touch) else np.nan,
           "max_dip_pct": depth, "closed_below": bool((c[seg] < trigger).any()),
           "deep_below_5": bool((c[seg] < trigger * (1 - BUFFER)).any())}
    j = b0 + 63
    res["ret_3m_from_trigger"] = (c[j] / trigger - 1) * 100 if j < len(c) else np.nan
    return res


def analyse(hits: pd.DataFrame, prices: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rule_rows, fact_rows, leg_rows = [], [], []
    for _, hit in hits.iterrows():
        df = prices.get(hit["symbol"])
        sig = bs.signal_bar(df, hit["hit_date"], bs.is_weekly(hit["scanner_name"])) if df is not None else None
        if sig is None:
            continue
        fwd = df.iloc[sig["end_pos"] + 1:]
        if len(fwd) < 2:
            continue
        trig = sig["trigger"]
        base = {"scanner_name": hit["scanner_name"], "symbol": hit["symbol"], "marketcap": hit["marketcap"],
                "hit_date": hit["hit_date"].date()}
        facts = pullback_facts(fwd, trig)
        if facts:
            fact_rows.append({**base, **facts})
        for rule, legs in run_rules(fwd, trig).items():
            if not legs:
                rule_rows.append({**base, "rule": rule, "bought": False})
                continue
            rule_rows.append({**base, "rule": rule, "bought": True, "buys": len(legs),
                              "total_ret": _growth(legs), "days_invested": sum(x - e + 1 for e, x, *_ in legs),
                              "status": legs[-1][4]})
            if rule == "breakout":
                for e, x, a, b, st in legs:
                    leg_rows.append({**base, "status": st, "entry_vs_trigger": (a / trig - 1) * 100,
                                     "exit_vs_trigger": (b / trig - 1) * 100,
                                     "ret": ((b / a) * (1 - bs.COST_PCT / 100) - 1) * 100, "days": x - e + 1})
    return pd.DataFrame(rule_rows), pd.DataFrame(fact_rows), pd.DataFrame(leg_rows)


def _p(x: float) -> str:
    return "–" if pd.isna(x) else f"{x:+.1f}%"


def section(rules: pd.DataFrame, facts: pd.DataFrame, legs: pd.DataFrame) -> list[str]:
    L = ["", "## The pullback after the breakout", "",
         f"For every signal that crossed its trigger, the {FACT_DAYS} sessions after the first crossing. "
         f"**Back at the trigger** = the low came within {NEAR:.0%} of the trigger (or below).", ""]
    if not facts.empty:
        L += ["| Scanner | Breakouts | Back at the trigger | Median days to get there | Closed below the trigger | "
              f"Closed {BUFFER:.0%}+ below | Median dip from the high | 3 months later: retested / not |",
              "|---|---|---|---|---|---|---|---|"]
        for name, x in [(n, g) for n, g in facts.groupby("scanner_name")] + [("**All**", facts)]:
            r3 = x["ret_3m_from_trigger"]
            L.append(f"| {name} | {len(x)} | {x['retested'].mean():.0%} | {x['days_to_retest'].median():.0f} | "
                     f"{x['closed_below'].mean():.0%} | {x['deep_below_5'].mean():.0%} | {_p(x['max_dip_pct'].median())} | "
                     f"{_p(r3[x['retested']].mean())} / {_p(r3[~x['retested']].mean())} |")

    if not legs.empty:
        st = legs[legs["status"] == "stop"]
        L += ["", "## Why a stop at the buy price still loses", "",
              "Every round trip of the *breakout* rule (buy above the trigger, sell after a close below it). "
              "Entry and exit are shown against the trigger price.", "",
              "| Scanner | Stopped round trips | Avg bought above trigger | Avg sold below trigger | Costs | "
              "Avg loss per stop | Bought on a gap-up | Sold 3%+ below trigger | Avg days held |",
              "|---|---|---|---|---|---|---|---|---|"]
        for name, x in [(n, g) for n, g in st.groupby("scanner_name")] + [("**All**", st)]:
            L.append(f"| {name} | {len(x)} | {_p(x['entry_vs_trigger'].mean())} | {_p(x['exit_vs_trigger'].mean())} | "
                     f"-{bs.COST_PCT:.2f}% | {_p(x['ret'].mean())} | {(x['entry_vs_trigger'] > 0.5).mean():.0%} | "
                     f"{(x['exit_vs_trigger'] < -3).mean():.0%} | {x['days'].mean():.0f} |")
        per_signal = legs.groupby(["scanner_name", "symbol", "hit_date"]).size()
        k, loss = per_signal.mean(), st["ret"].mean()
        L += ["", f"Signals are bought {k:.1f} times on average under this rule, so the small loss per stop "
              f"({_p(loss)}) repeats: {k:.0f} stops in a row is about {_p(((1 + loss / 100) ** round(k) - 1) * 100)}.", ""]

    if not rules.empty:
        b = rules[rules["bought"]]
        L += ["", "## Buying the pullback: rules compared", "",
              "Same signals, every market cap, no target, no time limit, new buys for 3 months after the signal, "
              f"{bs.COST_PCT}% costs per round trip, open positions valued at the latest close.", ""]
        L += [f"- **{k}**: {v}" for k, v in RULES.items()]
        L += ["", "| Rule | Scanner | Signals bought | Buys per signal | Profitable | Avg return | Median | "
              "Worst 10% avg | Avg days invested |", "|---|---|---|---|---|---|---|---|---|"]
        for rule in RULES:
            for name, x in [(n, g) for n, g in b[b["rule"] == rule].groupby("scanner_name")] + \
                           [("**All**", b[b["rule"] == rule])]:
                if x.empty:
                    continue
                r = x["total_ret"]
                L.append(f"| {rule} | {name} | {len(x)} | {x['buys'].mean():.1f} | {(r > 0).mean():.0%} | "
                         f"{_p(r.mean())} | {_p(r.median())} | {_p(r[r <= r.quantile(0.1)].mean())} | "
                         f"{x['days_invested'].mean():.0f} |")
        L += ["", "| Rule | Cap | Signals bought | Profitable | Avg return | Median |", "|---|---|---|---|---|---|"]
        for (rule, cap), x in b.groupby(["rule", "marketcap"]):
            if len(x) < 30:
                continue
            r = x["total_ret"]
            L.append(f"| {rule} | {cap or 'Unknown'} | {len(x)} | {(r > 0).mean():.0%} | {_p(r.mean())} | {_p(r.median())} |")
    return L
