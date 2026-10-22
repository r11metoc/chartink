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


def test_52_week_high_filter():
    idx = pd.bdate_range("2025-01-01", periods=260)
    high = [200.0] + [110.0] * 259                 # old peak at 200, then a range near 100-110
    df = pd.DataFrame({"Open": 100.0, "High": high, "Low": 95.0, "Close": 100.0}, index=idx)
    dist = dz.dist_52w_high(df, 259)               # peak 259 sessions back: just outside 252
    assert dist == round((100 / 110 - 1) * 100, 2)
    assert dz.passes_filter("63_30_daily", dist)               # 9% off -> kept
    assert not dz.passes_filter("63_30_daily", dz.dist_52w_high(df, 200))   # 50% off the 200 peak
    assert dz.passes_filter("Bullish_Scanner", -50.0)          # no filter on other scanners
    assert dz.passes_filter("63_30_daily", None)               # not enough history: keep
    assert dz.dist_52w_high(df, 50) is None


def test_tags_in_alert_text():
    s = {"confirmed_by": ["Bullish_Scanner"], "dist_52w_high": -4.2}
    assert "⭐ also on Bullish_Scanner" in dz._tags(s) and "4% off 52w high" in dz._tags(s)


def test_summary_ignores_duplicates():
    states = [{"scanner": "A", "symbol": "X", "status": "holding", "ret": 1.0},
              {"scanner": "A", "symbol": "X", "status": "duplicate"}]
    row = dz.summary(states)["rows"][0]
    assert row["signals"] == 1 and row["holding"] == 1
