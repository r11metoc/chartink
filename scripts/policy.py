"""The learned trading setup (written by learn.py), as used at run time:
take or skip a signal, and the exit rule to trade it with. Lightweight on
purpose: the scan job imports it without pandas' modelling stack."""

from __future__ import annotations

import json
from pathlib import Path

import breakout_sim as bs
import track_record

POLICY_PATH = Path(__file__).resolve().parent.parent / "data" / "model" / "policy.json"


def load(path: Path = POLICY_PATH) -> dict:
    return json.loads(path.read_text()) if path.exists() else {"history": []}


_doc: dict | None = None


def current() -> dict:
    """policy.json, read once per process."""
    global _doc
    if _doc is None:
        _doc = load()
    return _doc


def rule_from_dict(d: dict) -> bs.ExitRule:
    return bs.ExitRule(**d)


def describe(rule: bs.ExitRule) -> str:
    if rule.min_risk_pct == rule.max_risk_pct:
        stop = f"{rule.max_risk_pct:g}% stop"
    else:
        stop = f"stop at candle low ({rule.min_risk_pct:g}-{rule.max_risk_pct:g}%)"
    parts = [stop, f"target {rule.target_r:g}x risk" if rule.target_r else "no target"]
    if rule.trail_pct:
        parts.append(f"trail {rule.trail_pct:g}% below the high close")
    parts.append(f"out after {rule.max_hold} days")
    return ", ".join(parts)


def in_force(doc: dict, day: str | None = None) -> dict | None:
    """The setup that was current on `day` (ISO date; None = latest)."""
    hist = [h for h in doc.get("history", []) if day is None or h["from"] <= day]
    return hist[-1] if hist else None


def decide(entry: dict | None, scanner: str, tier: str | None, regime: str | None) -> dict | None:
    """{"take": bool, "rule": ExitRule, "why": str, "status": proven / not proven}
    or None while the scanner is still learning."""
    s = (entry or {}).get("scanners", {}).get(scanner)
    if not s or "rule" not in s:
        return None
    for g in s["skip"]:
        if g["tier"] == tier and g["regime"] == regime:
            return {"take": False, "rule": rule_from_dict(s["rule"]), "status": s["status"],
                    "why": f"{tier} in a {regime} market lost {g['avg']:+.1f}% a trade ({g['n']} trades)"}
    rule = rule_from_dict(s["rule"])
    why = "base rule - nothing learned beats it yet" if s["status"] == "not better" else describe(rule)
    return {"take": True, "rule": rule, "status": s["status"], "why": why}


def verdict(conn, scanner: str, symbol: str, day: str, mcap_cr: float | None = None) -> dict | None:
    """The current learned call on a signal, for alerts and the dashboard:
    {"take", "why", "status"}, or None while there's nothing learned."""
    d = decide(in_force(current()), scanner, track_record.tier_of(conn, symbol, mcap_cr),
               track_record.regime_on(conn, day))
    return {k: d[k] for k in ("take", "why", "status")} if d else None
