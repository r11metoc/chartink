import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dipzone as dz  # noqa: E402


def _t(sym, entry, exit_, ret, scanner="Bullish_Scanner"):
    return {"scanner": scanner, "symbol": sym, "cap": "Largecap", "status": "target" if ret > 0 else "stop",
            "ret": ret, "entry_date": pd.Timestamp(entry), "exit_date": pd.Timestamp(exit_), "days": 5}


def test_portfolio_limits_slots_and_books_pnl():
    t = pd.DataFrame([_t("A", "2024-01-01", "2024-01-10", 8.0), _t("B", "2024-01-02", "2024-01-05", -12.0),
                      _t("C", "2024-01-03", "2024-01-08", 8.0)])
    pf = dz.portfolio(t, capital=200_000, max_pos=2)
    assert pf["skipped"] == 1 and len(pf["taken"]) == 2          # C had no free slot
    assert round(pf["equity"].iloc[-1]) == 200_000 + 8_000 - 12_000


def test_portfolio_one_position_per_stock():
    t = pd.DataFrame([_t("A", "2024-01-01", "2024-01-10", 8.0), _t("A", "2024-01-02", "2024-01-09", 8.0, "63_30_daily")])
    assert dz.portfolio(t)["skipped"] == 1


def test_performance_vs_bench():
    t = pd.DataFrame([_t("A", "2024-01-01", "2024-02-01", 8.0), _t("B", "2024-03-01", "2024-04-01", 8.0, "63_30_daily")])
    bench = pd.Series([100.0, 104.0, 110.0], index=pd.to_datetime(["2024-01-01", "2024-03-01", "2024-04-01"]))
    perf = dz.performance(t, bench)
    assert perf["start"] == "2024-03-01"                          # when both scanners have data
    assert perf["portfolio"]["taken"] == 1 and perf["bench"]["name"] == "Nifty 500"
    assert dz.performance_section(perf)[1].startswith("## If I had bought")


def _df(closes):
    idx = pd.bdate_range("2024-01-01", periods=len(closes))
    c = pd.Series(closes, index=idx, dtype=float)
    return pd.DataFrame({"Open": c, "High": c * 1.001, "Low": c * 0.999, "Close": c})


def test_trailing_stop_rides_then_exits():
    up = [100 + i for i in range(30)] + [129 * 0.85] * 5   # +29%, then a 15% drop
    x = dz.ride(_df(up), 0, "Bullish_Scanner", "trail10")
    assert x["why"] == "stop" and x["ret"] == 9.4  # gapped below the trail: sold at the open


def test_ma_exit_sells_next_open():
    c = [100.0] * 25 + [110.0] * 5 + [90.0] * 3
    x = dz.ride(_df(c), 21, "Bullish_Scanner", "ma20")
    assert x["why"] == "average" and x["exit_date"] == _df(c).index[31]


def test_open_trade_returns_none():
    assert dz.ride(_df([100 + i for i in range(30)]), 0, "Bullish_Scanner", "trail15") is None


def test_lock_rule_ignores_average_until_plus_8():
    c = [100.0] * 25 + [99.0, 98.0, 99.0] + [109.0] * 3 + [90.0] * 3
    x = dz.ride(_df(c), 21, "Bullish_Scanner", "lock8_ma20")
    assert x["why"] == "stop" and x["ret"] < 0.5   # armed at +8%, then gapped below cost: sold at the open


def test_ride_uses_given_entry_price():
    c = [100.0] * 60 + [101.0 + i for i in range(10)] + [95.0] * 3
    x = dz.ride(_df(c), 60, "Bullish_Scanner", "ma50", ep=100.5)
    assert x["why"] == "average" and abs(x["ret"] - ((95 / 100.5 - 1) * 100 - 0.25)) < 0.02
