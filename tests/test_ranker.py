"""Offline tests for the ML signal ranker (scripts/ranker.py)."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import ranker  # noqa: E402


def _trades(n=1600, seed=1):
    """Synthetic trades 2019-2026 where a low 200-day distance helps a little."""
    rng = np.random.default_rng(seed)
    entry = pd.Timestamp("2019-02-01") + pd.to_timedelta(np.sort(rng.integers(0, 2800, n)), unit="D")
    entry = pd.DatetimeIndex(entry).map(lambda d: d - pd.offsets.BDay(0))
    t = pd.DataFrame({c: rng.normal(size=n) for c in ranker.NUMERIC})
    t["scanner"] = rng.choice(ranker.SCANNERS, n)
    t["cap"] = rng.choice(ranker.CAPS, n)
    t["symbol"] = [f"S{i}" for i in range(n)]
    t["entry_date"] = entry
    t["exit_date"] = entry + pd.Timedelta(days=30)
    t["days"] = 20
    t["ret"] = rng.normal(2, 10, n) - 4 * t["dist_sma200"]
    t.loc[::7, "vol_ratio"] = np.nan  # missing values are imputed
    return t


def test_walk_forward_never_sees_the_future():
    t = _trades()
    oos = ranker.walk_forward(t)
    assert oos[t["entry_date"].dt.year < ranker.FIRST_TEST_YEAR].isna().all()
    assert oos[t["entry_date"].dt.year >= 2021].notna().all()
    # A model trained on data up to 2020 scores a 2021 trade the same as walk_forward did.
    m = t["entry_date"].dt.year == 2021
    params = ranker.fit(t[t["exit_date"] < pd.Timestamp("2021-01-01")])
    assert np.allclose(ranker.predict(params, t[m]), oos[m])


def test_train_learns_signal_writes_json_and_ranks(tmp_path):
    t = _trades()
    model, oos = ranker.train(t, tmp_path / "r.json")
    saved = json.loads((tmp_path / "r.json").read_text())
    assert saved["on"] == model["on"] and isinstance(saved["on"], bool)
    assert model["test"]["auc"] > 0.6                     # the planted effect is found
    assert model["weights"][0]["feature"] == ranker.LABELS["dist_sma200"] and model["weights"][0]["w"] < 0
    good = {c: 0.0 for c in ranker.NUMERIC} | {"dist_sma200": -2.0}
    bad = good | {"dist_sma200": 2.0}
    assert ranker.rank(model, "63_30_daily", "Midcap", good) > ranker.rank(model, "63_30_daily", "Midcap", bad)
    assert ranker.rank(None, "63_30_daily", "Midcap", good) is None
    assert "Walk-forward" in ranker.report(model)


def test_noise_scores_like_a_coin_toss():
    t = _trades(seed=3)
    t["ret"] = np.random.default_rng(5).normal(2, 10, len(t))   # nothing to learn
    ev = ranker.evaluate(t, ranker.walk_forward(t))
    assert abs(ev["auc"] - 0.5) < 0.06
    assert set(ev["checks"]) == {"beats in first half", "beats in second half",
                                 "worst fall no more than 1 pt worse", "top half beat bottom half in 2/3 of years"}
