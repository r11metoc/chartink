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
    pf = dz.portfolio(t, capital=200_000, stake=100_000, max_pos=2)
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
