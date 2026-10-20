"""Offline tests for the trigger-price stop with re-entry (stock_outcomes.py)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import breakout_sim as bs  # noqa: E402
from stock_outcomes import simulate_reentry  # noqa: E402

COST = 1 - bs.COST_PCT / 100


def bars(rows):
    o, h, l, c = (np.array(col, dtype=float) for col in zip(*rows))
    return o, h, l, c


def test_rides_winner_with_no_limit():
    # crosses 100, then rises for good: one buy, still holding at the last close
    o, h, l, c = bars([(99, 101, 98, 100.5)] + [(100 + k, 102 + k, 100 + k, 101 + k) for k in range(1, 200)])
    r = simulate_reentry(o, h, l, c, 100.0, "close")
    assert len(r["legs"]) == 1 and r["legs"][0][4] == "holding"
    assert abs(r["total_ret"] - ((c[-1] / 100) * COST - 1) * 100) < 1e-9


def test_close_stop_then_reentry():
    rows = [(99, 101, 98, 100.5),   # buy at 100
            (100, 100.5, 96, 97),   # close below -> sell next open
            (96, 97, 95, 96),       # sold at 96, stays below
            (99, 103, 98, 102),     # back above -> buy at 100
            (102, 110, 101, 109)]
    r = simulate_reentry(*bars(rows), 100.0, "close")
    assert [(lg[2], lg[3], lg[4]) for lg in r["legs"]] == [(100.0, 96.0, "stop"), (100.0, 109.0, "holding")]


def test_intraday_stop_at_trigger_and_gap_down():
    rows = [(99, 101, 98, 100.5),   # buy at 100 (crossed up, no same-bar stop)
            (100.5, 101, 99, 100),  # trades below 100 -> out at 100
            (101, 104, 100.5, 103), # gap above -> buy at the open 101
            (95, 96, 94, 95)]       # gap-down -> out at the open 95
    r = simulate_reentry(*bars(rows), 100.0, "intraday")
    assert [(lg[2], lg[3]) for lg in r["legs"]] == [(100.0, 100.0), (101.0, 95.0)]


def test_no_new_buys_after_the_window():
    rows = [(99, 101, 98, 100.5), (99, 99.5, 97, 98), (97, 98, 96, 97)] + [(97, 99, 96, 98)] * 70 + [(101, 105, 100.5, 104)]
    r = simulate_reentry(*bars(rows), 100.0, "close", window=63)
    assert len(r["legs"]) == 1 and r["legs"][0][4] == "stop"


def test_never_crosses():
    r = simulate_reentry(*bars([(90, 95, 89, 94)] * 10), 100.0, "close")
    assert r["legs"] == [] and np.isnan(r["total_ret"])
