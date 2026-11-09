import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import health  # noqa: E402


def test_health_flags_price_mismatch(monkeypatch):
    bars = {"AAA": [("2026-11-05", 100, 105, 99, 104), ("2026-11-06", 104, 110, 103, 108)]}
    monkeypatch.setattr(health.db, "daily_prices_since", lambda c, s, d: [b for b in bars[s] if b[0] >= d])
    good = {"symbol": "AAA", "entry_date": "2026-11-05", "entry": 101, "status": "holding",
            "last_close": 108, "last_date": "2026-11-06", "ret": round((108 / 101 - 1) * 100 - 0.25, 2)}
    scan = [{"rows": [{"symbol": "AAA"}]}]
    now = datetime.now(timezone.utc).isoformat()
    h = health.checks(None, [good], now, scan)
    assert all(c["ok"] for c in h["checks"][:3])
    bad = dict(good, entry=120)  # outside the day's range
    h = health.checks(None, [bad], now, scan)
    assert not h["ok"] and "AAA buy" in h["checks"][2]["text"]
