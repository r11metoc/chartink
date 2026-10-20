"""Offline tests for the buy-the-dip rule (scripts/dipzone.py)."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import dipzone as dz  # noqa: E402


def frame(rows):
    idx = pd.bdate_range("2026-01-05", periods=len(rows))
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], index=idx)


BREAKOUT = [(99, 104, 98, 103), (103, 106, 102, 105)]  # trigger 100, high close 105


def test_dip_then_target():
    rows = BREAKOUT + [(104, 104, 101, 101.5),   # 3.3% below 105, above 95 -> buy next open
                       (101, 103, 100.5, 102),   # bought at 101
                       (102, 112, 101.5, 111)]   # target reached
    s = dz.simulate(frame(rows), 100.0, "63_30_daily")
    assert s["status"] == "target" and s["entry"] == 101.0
    assert abs(s["exit"] - 101 * (1 + dz.TARGET_PCT / 100)) < 1e-9
    assert s["ret"] == round(dz.TARGET_PCT - 0.25, 2)


def test_twelve_percent_stop():
    rows = BREAKOUT + [(104, 104, 101, 101.5), (101, 101.5, 99, 100), (99, 99.5, 88, 89)]  # stop 88.88
    s = dz.simulate(frame(rows), 100.0, "Bullish_Scanner")
    assert s["status"] == "stop" and abs(s["exit"] - 101 * 0.88) < 1e-9


def test_weekly_scanner_needs_five_percent():
    rows = BREAKOUT + [(104, 104, 101, 101.5)] + [(101.5, 102, 101, 101.5)] * 3
    assert dz.simulate(frame(rows), 100.0, "Wkly_upswing")["status"] == "watching for dip"
    rows = BREAKOUT + [(104, 104, 99, 99.5), (99.5, 100, 99, 99.6)]  # 5.2% below 105
    assert dz.simulate(frame(rows), 100.0, "Wkly_upswing")["status"] == "holding"


def test_dip_too_deep_below_trigger_is_not_a_buy():
    rows = BREAKOUT + [(100, 100, 93, 94)] + [(94, 95, 93, 94)] * 25   # close 94 < floor 95
    assert dz.simulate(frame(rows), 100.0, "63_30_daily")["status"] == "no dip"


def test_buy_zone_waits_for_next_open_and_time_exit():
    rows = BREAKOUT + [(104, 104, 101, 101.5)]
    assert dz.simulate(frame(rows), 100.0, "63_30_daily")["status"] == "buy zone"
    rows = rows + [(101, 102, 100, 101)] * (dz.MAX_HOLD + 1)
    s = dz.simulate(frame(rows), 100.0, "63_30_daily")
    assert s["status"] == "time" and s["ret"] == round(0 - 0.25, 2)


def test_alerts_only_once():
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect(":memory:")
    now = datetime(2026, 1, 9, 10, 0)
    rows = BREAKOUT + [(104, 104, 101, 101.5)]
    s = {"scanner": "63_30_daily", "symbol": "AAA", "date": "2026-01-02", **dz.simulate(frame(rows), 100.0, "63_30_daily")}
    first = dz.new_events(conn, [s], now)
    assert [k for _, _, k in first] == ["buy"] and "BUY ZONE" in dz.format_alerts(first)
    assert dz.new_events(conn, [s], now) == []
