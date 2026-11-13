"""Offline tests for the signal candle and features (no network needed).

Run: python -m pytest tests/
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import breakout_sim as bs  # noqa: E402


def _frame(rows, start="2026-03-02"):
    idx = pd.bdate_range(start, periods=len(rows))
    return pd.DataFrame(rows, columns=["Open", "High", "Low", "Close"], index=idx).assign(Volume=1000)


def test_weekly_signal_uses_whole_week_and_is_known_only_at_week_end():
    # Mon 2 Mar .. Fri 6 Mar, then the next Monday.
    df = _frame([[100, 101, 99, 100], [100, 103, 99, 102], [102, 108, 101, 107],
                 [107, 110, 105, 109], [109, 111, 104, 110], [110, 112, 109, 111]])
    sig = bs.signal_bar(df, pd.Timestamp("2026-03-02"), weekly=True)
    assert sig["signal_date"] == pd.Timestamp("2026-03-06")
    assert sig["trigger"] == 111 and sig["bar_low"] == 99 and sig["bar_close"] == 110
    # Mid-week the weekly bar isn't complete yet.
    assert bs.signal_bar(df.iloc[:3], pd.Timestamp("2026-03-02"), weekly=True) is None
    assert bs.signal_bar(df.iloc[:3], pd.Timestamp("2026-03-02"), weekly=True, require_complete=False) is not None


def test_daily_signal_bar():
    df = _frame([[100, 105, 98, 104], [104, 106, 103, 105]])
    sig = bs.signal_bar(df, pd.Timestamp("2026-03-02"), weekly=False)
    assert sig["end_pos"] == 0 and sig["trigger"] == 105 and sig["bar_low"] == 98
    assert bs.signal_bar(df, pd.Timestamp("2026-03-07"), weekly=False) is None  # Saturday


def test_indicator_frame_has_no_infinities_on_zero_volume():
    import numpy as np
    idx = pd.bdate_range("2024-01-01", periods=60)
    df = pd.DataFrame({"Open": 10.0, "High": 11.0, "Low": 9.0, "Close": 10.0, "Volume": 0.0}, index=idx)
    df.loc[idx[-1], "Volume"] = 1000.0  # after 20 zero-volume days: v / 0
    f = bs.indicator_frame(df)
    assert not np.isinf(f.to_numpy(dtype=float)).any()
