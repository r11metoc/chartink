import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import fundamentals  # noqa: E402
import valuepick_score as vp  # noqa: E402

ROW = {"Name": "Good Co", "NSE Code": "GOODCO", "Industry": "Chemicals", "Current Price": "100",
       "Market Capitalization": "2500", "Price to Earning": "15", "Return on capital employed": "28",
       "Debt to equity": "0.1", "Promoter holding": "65", "Sales growth 3Years": "30",
       "Profit growth 3Years": "40", "Profit after tax": "100", "CFO": "90", "High price": "130"}


def test_good_company_shortlisted():
    r = vp.score_row(ROW)
    assert r["score"] >= 65 and r["verdict"] == "Shortlist" and r["entry"] == "dip zone"


def test_low_promoter_rejected_and_flags():
    r = vp.score_row({**ROW, "Promoter holding": "20", "CFO": "-5"})
    assert r["verdict"].startswith("Reject") and "negative CFO" in r["flags"]


def test_check_reads_export(tmp_path):
    f = tmp_path / "latest.csv"
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ROW)); w.writeheader(); w.writerow(ROW)
    c = fundamentals.check("goodco", f)
    assert c["verdict"] == "Shortlist" and fundamentals.label(c).startswith("Fundamentals")
    assert fundamentals.check("MISSING", f) is None


def test_yahoo_mapping_and_score():
    import pandas as pd
    import yahoo_fundamentals as yfu
    cols = pd.to_datetime(["2026-03-31", "2025-03-31", "2024-03-31", "2023-03-31"])
    inc = pd.DataFrame({c: v for c, v in zip(cols, [[2e10, 3e9, 4e9], [1.6e10, 2.4e9, 3.2e9],
                                                     [1.3e10, 1.8e9, 2.5e9], [1e10, 1.2e9, 2e9]])},
                       index=["Total Revenue", "Net Income", "EBIT"])
    bal = pd.DataFrame({c: v for c, v in zip(cols, [[3e10, 8e9, 2e9, 3e9]] * 4)},
                       index=["Total Assets", "Current Liabilities", "Total Debt", "Accounts Receivable"])
    cf = pd.DataFrame({c: [2.8e9] for c in cols}, index=["Operating Cash Flow"])
    info = {"longName": "Good Co", "industry": "Chemicals", "currentPrice": 100, "marketCap": 2.5e10,
            "trailingPE": 15, "returnOnEquity": 0.25, "debtToEquity": 10, "heldPercentInsiders": 0.65,
            "fiftyTwoWeekHigh": 130}
    row = yfu.to_screener("GOODCO", info, inc, bal, cf)
    assert row["Market Capitalization"] == 2500.0 and row["Debt to equity"] == 0.1
    assert row["Sales growth 3Years"] == 26.0 and row["Promoter holding"] == 65.0
    assert row["Return on capital employed"] == round(4e9 / 2.2e10 * 100, 1)
    r = vp.score_row(row)
    assert r["verdict"] == "Shortlist" and r["score"] >= 65


def test_check_uses_yahoo_cache(tmp_path, monkeypatch):
    import db
    import yahoo_fundamentals as yfu
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    conn = db.connect()
    yfu._ensure(conn)
    conn.execute("INSERT INTO fundamentals VALUES (?, ?, ?)", ("GOODCO", "2026-11-08T00:00:00+00:00", __import__("json").dumps(ROW)))
    conn.commit(); conn.close()
    fundamentals._yahoo.clear()
    monkeypatch.setattr(fundamentals, "FILE", tmp_path / "none.csv")
    monkeypatch.setattr(fundamentals, "_cache", None)
    c = fundamentals.check("GOODCO", fundamentals.FILE)
    assert c and c["source"] == "Yahoo" and c["verdict"] == "Shortlist"
