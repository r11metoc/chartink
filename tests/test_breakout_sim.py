"""Offline tests for the trade simulation (no network needed).

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


def test_entry_fills_at_trigger_or_gap_open_and_expires():
    rule = bs.ExitRule(max_risk_pct=5, min_risk_pct=5, target_r=2, max_hold=3)
    # Never crosses 100 in the 3-session window.
    path = _frame([[95, 99, 94, 98], [98, 99.5, 97, 99], [99, 100, 98, 99], [99, 120, 99, 119]])
    assert bs.simulate_trade(path, 100, 90, 3, rule)["status"] == "not_triggered"
    # Gap up: filled at the open, not the trigger.
    path = _frame([[103, 104, 102.5, 103.5], [103.5, 104, 103, 103.8], [103.8, 104, 103, 103.9], [104, 104, 103, 104]])
    res = bs.simulate_trade(path, 100, 90, 3, rule)
    assert res["entry_price"] == 103 and res["gap_entry"] and res["exit_reason"] == "time"


def test_stop_and_target_are_pessimistic():
    rule = bs.ExitRule(max_risk_pct=5, min_risk_pct=5, target_r=2, max_hold=10)
    # Entry day touches both the trigger and the stop -> stopped out same day.
    path = _frame([[99, 101, 94, 95], [95, 120, 95, 118]])
    res = bs.simulate_trade(path, 100, 90, 3, rule)
    assert res["exit_reason"] == "stop" and res["exit_offset"] == 0
    assert np.isclose(res["exit_price"], 95) and np.isclose(res["r_multiple"], -1)
    # Clean run to the target (100 * 1.10).
    path = _frame([[99, 101, 99, 100.5], [100.5, 111, 100, 110]])
    res = bs.simulate_trade(path, 100, 90, 3, rule)
    assert res["exit_reason"] == "target" and np.isclose(res["r_multiple"], 2)
    # Gap down through the stop fills at the open, worse than the stop.
    path = _frame([[99, 101, 99, 100.5], [90, 91, 89, 90]])
    res = bs.simulate_trade(path, 100, 90, 3, rule)
    assert res["exit_reason"] == "stop_gap" and res["exit_price"] == 90


def test_history_features_ignore_future_hits():
    hits = pd.DataFrame({
        "scanner_name": ["A", "A", "B", "A"],
        "symbol": ["X", "X", "X", "X"],
        "signal_date": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-02-05", "2026-03-01"]),
    })
    f = bs.history_features(hits)
    assert list(f["prior_hits_same_scanner_180d"]) == [0, 1, 0, 2]
    assert list(f["other_scanner_hits_10d"]) == [0, 0, 1, 0]


def test_end_to_end_on_synthetic_prices(tmp_path, monkeypatch):
    import build_dataset
    import signal_model

    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2024-06-03", "2026-09-25")
    symbols = [f"S{i}" for i in range(40)]
    prices = {}
    for s in symbols:
        close = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, len(idx))))
        opn = close * (1 + rng.normal(0, 0.005, len(idx)))
        high = np.maximum(opn, close) * (1 + np.abs(rng.normal(0, 0.01, len(idx))))
        low = np.minimum(opn, close) * (1 - np.abs(rng.normal(0, 0.01, len(idx))))
        prices[s] = pd.DataFrame({"Open": opn, "High": high, "Low": low, "Close": close,
                                  "Volume": rng.integers(1e4, 1e6, len(idx))}, index=idx)
    nifty = prices["S0"]

    days = idx[(idx >= "2025-06-01") & (idx <= "2026-09-20")]
    rows = []
    for scanner in ("63_30_daily", "Bullish_Scanner", "Wkly_upswing"):
        for d in rng.choice(days, 250):
            d = pd.Timestamp(d)
            if scanner == "Wkly_upswing":
                d = d - pd.Timedelta(days=d.weekday())
            rows.append({"scanner_name": scanner, "hit_date": d, "symbol": rng.choice(symbols),
                         "marketcap": rng.choice(["Smallcap", "Midcap", "Largecap"]), "sector": "X"})
    hits = pd.DataFrame(rows).drop_duplicates(["scanner_name", "hit_date", "symbol"]).reset_index(drop=True)

    signals, paths = build_dataset.build(hits, prices, nifty)
    assert (signals["data_status"] == "ok").mean() > 0.9

    monkeypatch.setattr(signal_model, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(signal_model, "MODEL_PATH", tmp_path / "m.pkl")
    monkeypatch.setattr(signal_model, "META_PATH", tmp_path / "m.json")
    monkeypatch.setattr(signal_model, "REPORT_PATH", tmp_path / "report.md")
    signals.to_csv(tmp_path / "signals.csv", index=False)
    paths.to_csv(tmp_path / "paths.csv.gz", index=False)
    assert signal_model.train() == 0
    assert "Does buying every trigger make money" in (tmp_path / "report.md").read_text()

    import horizon_returns
    horizon_df = horizon_returns.horizon_rows(signals, signal_model.load_dataset()[1], None)
    assert len(horizon_df) > 0 and "ret_12w" in horizon_df
    first = horizon_df.dropna(subset=["ret_2w"]).iloc[0]
    assert np.isclose(first["ret_2w"], (first["price_2w"] / first["entry_price"] - 1) * 100)

    new = pd.DataFrame({"scanner_name": ["63_30_daily", "Wkly_upswing", "63_30_daily"],
                        "symbol": ["S1", "S2", "NOPE"], "hit_date": [pd.NaT] * 3,
                        "marketcap": ["Midcap"] * 3, "sector": ["X"] * 3})
    monkeypatch.setattr(build_dataset, "load_hits", lambda *a, **k: hits.copy())
    res = signal_model.score_signals(new, prices, nifty)
    assert set(res["action"]) <= {"BUY", "SETUP", "SKIP", "TRIGGERED", "MISSED", "EXPIRED", "NO DATA"}
    assert res.loc[2, "action"] == "NO DATA"
    assert (res.loc[:1, "stop"] < res.loc[:1, "trigger"]).all()
