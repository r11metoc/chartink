"""Offline tests for the pullback buy rules (scripts/pullback.py)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pullback as pb  # noqa: E402


def frame(rows):
    idx = pd.bdate_range("2024-01-01", periods=len(rows))
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], index=idx)


def test_retest_buys_next_open_after_dip_that_holds():
    rows = [(99, 103, 98, 102),      # breakout over 100
            (103, 106, 103, 105),       # stays well above: no retest yet
            (104, 104.5, 101.5, 101),  # low within 2% of 100, close above 100 -> buy next open
            (101.5, 106, 101, 105),    # bought at 101.5
            (105, 110, 104, 109)]
    legs = pb.run_rules(frame(rows), 100.0)["retest"]
    assert legs == [(3, 4, 101.5, 109.0, "holding")]


def test_buffer_stop_survives_small_dip_that_breaks_plain_stop():
    rows = [(99, 101, 98, 100.5), (100, 100.5, 97, 98), (98, 103, 97.5, 102), (102, 108, 101, 107)]
    out = pb.run_rules(frame(rows), 100.0)
    assert len(out["breakout"]) == 2          # stopped by the close at 98, bought again
    assert len(out["breakout5"]) == 1         # 98 is above the 95 stop: still holding
    assert out["breakout5"][0][4] == "holding"


def test_dip5_waits_for_five_percent_off_the_high():
    rows = [(99, 101, 98, 100.5), (101, 111, 100, 110), (109, 109.5, 104, 104.4),  # 5.1% off 110
            (104, 106, 103, 105), (105, 112, 104, 111)]
    legs = pb.run_rules(frame(rows), 100.0)["dip5"]
    assert legs[0][:3] == (3, 4, 104.0)


def test_facts_detect_retest():
    rows = [(99, 103, 98, 102)] + [(102, 104, 101.5, 103)] * 5 + [(102, 102, 100.5, 101)] + [(103, 105, 102, 104)] * 80
    f = pb.pullback_facts(frame(rows), 100.0)
    assert f["retested"] and f["days_to_retest"] == 1  # first bar after the breakout already within 2%
    assert not f["closed_below"]


def test_no_breakout_no_pullback_buys():
    out = pb.run_rules(frame([(90, 95, 89, 94)] * 10), 100.0)
    assert out["retest"] == [] and out["breakout"] == []
