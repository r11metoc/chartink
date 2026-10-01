"""Learn which trades to take and how to exit them, from the scanners' own
history, and prove it out of sample before trusting it.

For each scanner it tries a fixed grid of exit rules (stop width, profit
target, trailing stop, max holding period) on every past signal, plus a
setup filter that skips market-cap tier x market regime groups that lost
money. The choice is walk-forward tested: for every month it picks the rule
and filter using only trades that had closed before that month began, then
trades that month with them. The out-of-sample result is compared with the
base rule (breakout_sim.DEFAULT_RULE on every signal):

  - the filter is kept only if it improved the walk-forward result,
  - the learned setup is "proven" only if it beat the base rule there.

Writes data/model/policy.json (the current choice plus every earlier one,
so the paper book can apply what was known at each signal's date) and
reports/learning_report.md. Run weekly by signal_model.yml after the
dataset is rebuilt (which includes the bot's own live triggers), so the
choice keeps updating as new trades close.

Usage: python learn.py
"""

from __future__ import annotations

import itertools
import json
import math
from datetime import datetime, timezone

import pandas as pd

import breakout_sim as bs
import signal_model as sm
from policy import POLICY_PATH, describe, rule_from_dict
from track_record import _regime

REPORT_PATH = sm.ROOT / "reports" / "learning_report.md"
MIN_TRAIN = 60       # closed trades a scanner needs before it is traded out of sample
MIN_GROUP = 20       # trades a setup group needs before it can be skipped
PROVEN_T = 1.65      # gain over the base rule must be this many standard errors above 0

# (min, max) % below entry for the stop; equal values = fixed % stop.
STOPS = [(2, 8), (2, 12), (4, 4), (6, 6), (8, 8), (12, 12)]
TARGETS = [0, 1.5, 2, 3]       # x risk; 0 = no target
TRAILS = [0, 8]                # % below the highest close; 0 = none
HOLDS = [10, 20, 40]           # sessions after entry
GRID = [bs.ExitRule(min_risk_pct=lo, max_risk_pct=hi, target_r=t, trail_pct=tr, max_hold=h)
        for (lo, hi), t, tr, h in itertools.product(STOPS, TARGETS, TRAILS, HOLDS)]


def _rule_key(rule: bs.ExitRule) -> str:
    return f"{rule.min_risk_pct:g}-{rule.max_risk_pct:g}|{rule.target_r:g}|{rule.trail_pct:g}|{rule.max_hold}"


def simulate_grid(signals: pd.DataFrame, paths: dict, bench) -> dict[str, pd.DataFrame]:
    """Closed trades of every signal under every rule in GRID (plus the
    base rule), keyed by rule. Entry doesn't depend on the exit rule, so
    each rule sees the same signals."""
    sig = signals[signals["data_status"] == "ok"].copy()
    sig["tier"] = sig["marketcap"].fillna("")
    sig["regime"] = sig["nifty_dist_sma50"].map(_regime)
    out = {}
    for rule in [bs.DEFAULT_RULE] + GRID:
        key = _rule_key(rule)
        if key in out:
            continue
        sim = sm.simulate_all(sig, paths, rule)
        # Entered trades, the ones still open at the end of the data marked to the last close,
        # so every rule is judged on the same signals.
        t = sm.add_benchmark(sim[sim["entry_offset"].notna()].reset_index(drop=True), bench)
        t["closed"] = t["status"] == "triggered"
        out[key] = t[["hit_id", "scanner_name", "signal_date", "entry_date", "exit_date", "tier", "regime",
                      "closed", "ret_pct"] + (["excess_pct"] if "excess_pct" in t else [])].set_index("hit_id")
    return out


def choose(trades: dict[str, pd.DataFrame], scanner: str, cutoff: pd.Timestamp | None) -> dict | None:
    """Best rule and loss-making groups for `scanner`, from trades that had
    closed before `cutoff` (None = all of them)."""
    best = None
    for key, t in trades.items():
        t = t[t["scanner_name"] == scanner]
        t = t[t["closed"]] if cutoff is None else t[t["closed"] & (t["exit_date"] < cutoff)]
        if len(t) < MIN_TRAIN:
            return None
        avg = t["ret_pct"].mean()
        if best is None or avg > best[1]:
            best = (key, avg, t)
    key, _, t = best
    groups = t.groupby(["tier", "regime"])["ret_pct"].agg(["mean", "count"])
    skip = [{"tier": tier, "regime": regime, "avg": round(float(g["mean"]), 2), "n": int(g["count"])}
            for (tier, regime), g in groups.iterrows() if g["count"] >= MIN_GROUP and g["mean"] < 0]
    return {"rule": key, "train_n": len(t), "train_avg": round(float(t["ret_pct"].mean()), 2), "skip": skip}


def _skipped(trades: pd.DataFrame, skip: list[dict]) -> pd.Series:
    mask = pd.Series(False, index=trades.index)
    for s in skip:
        mask |= (trades["tier"] == s["tier"]) & (trades["regime"] == s["regime"])
    return mask


def walk_forward(trades: dict[str, pd.DataFrame], scanner: str) -> pd.DataFrame:
    """Month by month: choose on what had closed before the month began,
    then trade that month's signals with the choice. One row per signal
    traded out of sample: its return under the base rule and the learned
    rule, and whether the learned filter would have skipped it."""
    base_key = _rule_key(bs.DEFAULT_RULE)
    base_all = trades[base_key][trades[base_key]["scanner_name"] == scanner]
    rows = []
    if base_all.empty:
        return pd.DataFrame()
    months = pd.date_range(base_all["signal_date"].min().to_period("M").to_timestamp(),
                           base_all["signal_date"].max(), freq="MS")
    for start in months:
        pick = choose(trades, scanner, start)
        if pick is None:
            continue
        end = start + pd.offsets.MonthBegin(1)
        base = base_all[(base_all["signal_date"] >= start) & (base_all["signal_date"] < end)]
        learned = trades[pick["rule"]].reindex(base.index)
        rows.append(pd.DataFrame({
            "base": base["ret_pct"], "base_x": base.get("excess_pct"),
            "rule": learned["ret_pct"], "rule_x": learned.get("excess_pct"),
            "skipped": _skipped(base, pick["skip"]),
        }))
    return pd.concat(rows) if rows else pd.DataFrame()


def _stats(ret: pd.Series, excess: pd.Series | None, base: pd.Series) -> dict:
    """Out-of-sample result of a setup, and its gain over the base rule on
    the same signals (a skipped signal earns 0)."""
    taken = ret.dropna()
    if taken.empty:
        return {"n": 0, "win": None, "avg": None, "vs_index": None, "total": 0.0, "gain": None, "t": None}
    gain = ret.fillna(0) - base
    sd = gain.std()
    ex = excess.dropna() if excess is not None else pd.Series(dtype=float)
    return {
        "n": len(taken),
        "win": round(100 * float((taken > 0).mean())),
        "avg": round(float(taken.mean()), 2),
        "vs_index": round(float(ex.mean()), 2) if len(ex) else None,
        # Sum of % returns x 1000 = rupees at Rs 1L a trade; fair to setups that trade less.
        "total": round(float(taken.sum()), 1),
        "gain": round(float(gain.mean()), 2),
        "t": round(float(gain.mean() / (sd / math.sqrt(len(gain)))), 2) if sd > 0 else None,
    }


def learn() -> dict:
    signals, paths = sm.load_dataset()
    bench = sm.load_benchmark()
    trades = simulate_grid(signals, paths, bench[1] if bench else None)
    base_rule = {k: getattr(bs.DEFAULT_RULE, k) for k in rule_dict(_rule_key(bs.DEFAULT_RULE))}
    scanners = {}
    for scanner in sorted(signals["scanner_name"].unique()):
        pick = choose(trades, scanner, None)
        wf = walk_forward(trades, scanner)
        if pick is None or wf.empty:
            scanners[scanner] = {"status": "learning", "walk_forward": {}}
            continue
        filt = wf["rule"].where(~wf["skipped"])
        res = {
            "base": _stats(wf["base"], wf["base_x"], wf["base"]),
            "rule": _stats(wf["rule"], wf["rule_x"], wf["base"]),
            "rule+filter": _stats(filt, wf["rule_x"].where(~wf["skipped"]), wf["base"]),
        }
        use_filter = (res["rule+filter"]["gain"] or 0) > (res["rule"]["gain"] or 0)
        best = res["rule+filter"] if use_filter else res["rule"]
        gain, t = best["gain"] or 0, best["t"] or 0
        status = "proven" if gain > 0 and t >= PROVEN_T else "promising" if gain > 0 else "not better"
        scanners[scanner] = {
            "status": status,
            # Not better out of sample: stay with the base rule on every signal.
            "rule": rule_dict(pick["rule"]) if status != "not better" else base_rule,
            "skip": pick["skip"] if use_filter and status != "not better" else [],
            "candidate": rule_dict(pick["rule"]),
            "train": {"n": pick["train_n"], "avg": pick["train_avg"]},
            "walk_forward": res,
        }
    return scanners


def rule_dict(key: str) -> dict:
    stop, target, trail, hold = key.split("|")
    lo, hi = stop.split("-")
    return {"min_risk_pct": float(lo), "max_risk_pct": float(hi), "target_r": float(target),
            "trail_pct": float(trail), "max_hold": int(hold)}


def _row(label: str, s: dict, base: bool = False) -> str:
    if not s["n"]:
        return f"| {label} | 0 | - | - | - | - | - |"
    vs = f"{s['vs_index']:+.2f}%" if s["vs_index"] is not None else "-"
    gain = "" if base else f"{s['gain']:+.2f}% (t {s['t']:.1f})" if s["t"] is not None else f"{s['gain']:+.2f}%"
    return (f"| {label} | {s['n']} | {s['win']}% | {s['avg']:+.2f}% | {vs} | {s['total'] * 1000:+,.0f} | {gain} |")


def report(scanners: dict, learned_at: str) -> str:
    lines = [
        "# What the system learned", "",
        f"Updated {learned_at}. For each scanner {len(GRID)} exit rules were tried; the setup filter skips "
        f"market-cap x market-regime groups that lost money (at least {MIN_GROUP} trades).", "",
        "**Walk-forward test:** every month the rule and filter were picked using only trades that had "
        "already closed, then used on that month's signals. These are the only numbers that count; "
        "the in-sample best always looks better than it is. Trades still open are valued at the last close.", "",
        f"**Status:** *proven* = beat the base rule on the same signals by at least {PROVEN_T} standard errors "
        "(t); *promising* = ahead but could be luck; *not better* = the base rule is kept.", "",
    ]
    for scanner, s in scanners.items():
        lines += [f"## {scanner}", ""]
        if s["status"] == "learning":
            lines += [f"Not enough closed trades yet (needs {MIN_TRAIN}).", ""]
            continue
        if s["status"] == "not better":
            lines += [f"- **Best candidate:** {describe(rule_from_dict(s['candidate']))} - did worse on unseen months, "
                      f"so the base rule is kept: {describe(rule_from_dict(s['rule']))}"]
        else:
            lines += [f"- **Learned rule:** {describe(rule_from_dict(s['rule']))}"]
        lines += [
                  f"- **Skips:** " + (", ".join(f"{g['tier']} in a {g['regime']} market ({g['avg']:+.1f}%, {g['n']} trades)"
                                               for g in s["skip"]) or "nothing"),
                  f"- **Status:** {s['status']} (best candidate in sample: {s['train']['n']} trades, "
                  f"avg {s['train']['avg']:+.2f}%)", "",
                  "| Walk-forward | Trades | Won | Avg | vs Nifty 500 | ₹ on ₹1L a trade | Gain per signal vs base |",
                  "|---|---|---|---|---|---|---|",
                  _row("Base rule, every signal", s["walk_forward"]["base"], base=True),
                  _row("Learned rule", s["walk_forward"]["rule"]),
                  _row("Learned rule + filter", s["walk_forward"]["rule+filter"]), ""]
    return "\n".join(lines)


def main() -> int:
    learned_at = datetime.now(timezone.utc).date().isoformat()
    scanners = learn()
    doc = json.loads(POLICY_PATH.read_text()) if POLICY_PATH.exists() else {"history": []}
    entry = {"from": learned_at, "scanners": scanners}
    # Keep one entry per distinct choice; the paper book uses the one in force on each signal date.
    choice = lambda e: {k: (v.get("rule"), v.get("skip")) for k, v in e["scanners"].items()}
    if doc["history"] and choice(doc["history"][-1]) == choice(entry):
        doc["history"][-1]["scanners"] = scanners  # same choice, refresh the evidence
    else:
        doc["history"].append(entry)
    doc["updated"] = learned_at
    POLICY_PATH.write_text(json.dumps(doc, indent=1, allow_nan=False))
    REPORT_PATH.write_text(report(scanners, learned_at))
    for scanner, s in scanners.items():
        print(f"{scanner}: {s['status']}" + (f" - {describe(rule_from_dict(s['rule']))}" if "rule" in s else ""))
        for k, v in s["walk_forward"].items():
            print(f"   {k:12s} {v}")
    print(f"Wrote {POLICY_PATH} and {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
