import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import db  # noqa: E402
import paper  # noqa: E402
import policy  # noqa: E402


@pytest.fixture()
def conn(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    monkeypatch.setattr(paper, "PAPER_START", "2026-09-01")
    c = db.connect()
    yield c
    c.close()


def bars(start: str, closes: list[float], spread: float = 1.0):
    """Weekday bars from `start`: open at the previous close, high/low =
    the larger/smaller of open and close +- spread."""
    out, d, prev = [], date.fromisoformat(start), closes[0]
    for c in closes:
        while d.weekday() >= 5:
            d += timedelta(days=1)
        out.append((d.isoformat(), prev, max(prev, c) + spread, min(prev, c) - spread, c))
        prev = c
        d += timedelta(days=1)
    return out


def add_hit(conn, scanner, day, symbol):
    conn.execute("INSERT INTO backtest_hits (scanner_name, hit_date, symbol, marketcap, sector) VALUES (?, ?, ?, '', '')",
                 (scanner, day, symbol))


def test_trade_hits_target(conn):
    # Signal Tue 1 Sep: high 101, low 99. Next day crosses 101 -> entry; then rallies past 2R.
    db.save_daily_prices(conn, "AAA", bars("2026-09-01", [100, 102, 104, 106, 108, 112, 115]))
    add_hit(conn, "63_30_daily", "2026-09-01", "AAA")
    (t,) = paper.paper_trades(conn)
    assert t["status"] == "closed" and t["exit_reason"] == "target"
    # Risk (101 - 99) / 101 is under the 2% floor, so stop/target use 2%.
    assert t["entry"] == 101.0 and t["target"] == 105.04 and t["exit"] == 105.04
    assert t["ret"] == pytest.approx(3.75, abs=0.01) and t["pnl"] == 3750
    summary = paper.summarize([t])
    assert summary[0]["closed"] == 1 and summary[0]["win"] == 100


def test_waiting_until_trigger_crossed(conn):
    # Price never crosses the 101 trigger within the 3-session window... yet (only 1 session after).
    db.save_daily_prices(conn, "BBB", bars("2026-09-01", [100, 99.5]))
    add_hit(conn, "63_30_daily", "2026-09-01", "BBB")
    (t,) = paper.paper_trades(conn)
    assert t["status"] == "waiting" and t["trigger"] == 101.0


def test_weekend_hit_uses_previous_session(conn):
    # Hit dated Sat 5 Sep -> signal bar is Fri 4 Sep (open 102, close 103, high 104).
    db.save_daily_prices(conn, "CCC", bars("2026-09-01", [100, 101, 102, 103, 105, 107]))
    add_hit(conn, "63_30_daily", "2026-09-05", "CCC")
    (t,) = paper.paper_trades(conn)
    assert t["trigger"] == 104.0 and t["entry_date"] == "2026-09-07"


def _policy(monkeypatch, scanners, start="2026-09-01"):
    monkeypatch.setattr(policy, "_doc", {"history": [{"from": start, "scanners": scanners}]})


def test_learned_book_uses_learned_rule(conn, monkeypatch):
    # Learned: fixed 6% stop, no target, out after 3 days -> exits on time, not at the 2R target.
    _policy(monkeypatch, {"63_30_daily": {"status": "promising", "skip": [], "rule": {
        "min_risk_pct": 6, "max_risk_pct": 6, "target_r": 0, "trail_pct": 0, "max_hold": 3}}})
    db.save_daily_prices(conn, "AAA", bars("2026-09-01", [100, 102, 104, 106, 108, 112, 115]))
    add_hit(conn, "63_30_daily", "2026-09-01", "AAA")
    (t,) = paper.paper_trades(conn, "learned")
    assert t["status"] == "closed" and t["exit_reason"] == "time"
    assert t["stop"] == pytest.approx(101 * 0.94, abs=0.01) and t["exit"] == 108.0
    assert t["rule"].startswith("6% stop")


def test_learned_book_skips_losing_setup(conn, monkeypatch):
    _policy(monkeypatch, {"63_30_daily": {"status": "proven", "rule": {
        "min_risk_pct": 2, "max_risk_pct": 8, "target_r": 2, "trail_pct": 0, "max_hold": 20},
        "skip": [{"tier": "Smallcap", "regime": None, "avg": -2.1, "n": 67}]}})
    db.save_daily_prices(conn, "AAA", bars("2026-09-01", [100, 102, 104]))
    conn.execute("INSERT INTO backtest_hits (scanner_name, hit_date, symbol, marketcap, sector) "
                 "VALUES ('63_30_daily', '2026-09-01', 'AAA', 'Smallcap', '')")
    (t,) = paper.paper_trades(conn, "learned")
    assert t["status"] == "skipped" and "Smallcap" in t["why"]
    assert paper.summarize([t])[0]["skipped"] == 1


def test_no_learned_book_before_first_learning(conn, monkeypatch):
    monkeypatch.setattr(policy, "_doc", {"history": []})
    add_hit(conn, "63_30_daily", "2026-09-01", "AAA")
    assert paper.paper_trades(conn, "learned") == []
