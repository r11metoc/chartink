"""How similar past setups did, from the backtest trades (data/model/trades.csv,
written by signal_model.py train).

A setup is scanner x market-cap tier x market regime (Nifty 50 above or below
its 50-day average when the signal fired). The most specific group with at
least MIN_TRADES closed trades is used, falling back to scanner x tier, then
the scanner alone, so every number rests on a reasonable sample.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRADES = ROOT / "data" / "model" / "trades.csv"
SIGNALS = ROOT / "data" / "model" / "signals.csv"
MIN_TRADES = 20
NIFTY = "^NSEI"
# Approximate AMFI cut-offs (rank 100 / 250) in crores, only for stocks the
# backtest exports never listed; Chartink's own tier is used when known.
LARGECAP_CR, MIDCAP_CR = 100_000, 30_000


def _regime(dist_sma50) -> str | None:
    try:
        d = float(dist_sma50)
    except (TypeError, ValueError):
        return None
    return None if d != d else ("strong" if d > 0 else "weak")


def load_trades() -> list[dict]:
    if not TRADES.exists() or not SIGNALS.exists():
        return []
    signals = {(r["scanner_name"], r["hit_date"], r["symbol"]): r for r in csv.DictReader(SIGNALS.open())}
    out = []
    for t in csv.DictReader(TRADES.open()):
        if t["status"] != "triggered":
            continue
        s = signals.get((t["scanner_name"], t["hit_date"], t["symbol"]), {})
        out.append({
            "scanner": t["scanner_name"],
            "tier": s.get("marketcap") or None,
            "regime": _regime(s.get("nifty_dist_sma50")),
            "ret": float(t["ret_pct"]),
            "excess": float(t["excess_pct"]) if t["excess_pct"] else None,
        })
    return out


class TrackRecord:
    def __init__(self, trades: list[dict] | None = None):
        self.trades = load_trades() if trades is None else trades

    def lookup(self, scanner: str, tier: str | None, regime: str | None) -> dict | None:
        levels = ([(tier, regime)] if tier and regime else []) + ([(tier, None)] if tier else []) + [(None, None)]
        for want_tier, want_regime in levels:
            rows = [t for t in self.trades if t["scanner"] == scanner
                    and (want_tier is None or t["tier"] == want_tier)
                    and (want_regime is None or t["regime"] == want_regime)]
            if len(rows) >= MIN_TRADES:
                excess = [t["excess"] for t in rows if t["excess"] is not None]
                label = " · ".join(filter(None, [want_tier, {"strong": "strong market", "weak": "weak market"}.get(want_regime)]))
                return {
                    "group": label or "all setups",
                    "n": len(rows),
                    "win": round(100 * sum(t["ret"] > 0 for t in rows) / len(rows)),
                    "avg": round(sum(t["ret"] for t in rows) / len(rows), 2),
                    "vs_index": round(sum(excess) / len(excess), 2) if excess else None,
                }
        return None


def tier_of(conn, symbol: str, mcap_cr: float | None = None) -> str | None:
    row = conn.execute(
        "SELECT marketcap FROM backtest_hits WHERE symbol = ? AND marketcap != '' ORDER BY hit_date DESC LIMIT 1",
        (symbol,)).fetchone()
    if row:
        return row[0]
    if mcap_cr is None:
        return None
    return "Largecap" if mcap_cr >= LARGECAP_CR else "Midcap" if mcap_cr >= MIDCAP_CR else "Smallcap"


def regime_on(conn, day: str) -> str | None:
    """'strong' if the Nifty 50 closed above its 50-day average on `day`
    (or the last session before it), 'weak' if below."""
    closes = [c for (c,) in conn.execute(
        "SELECT close FROM daily_prices WHERE symbol = ? AND date <= ? ORDER BY date DESC LIMIT 50", (NIFTY, day))]
    if len(closes) < 50:
        return None
    return _regime((closes[0] / (sum(closes) / 50) - 1) * 100)
