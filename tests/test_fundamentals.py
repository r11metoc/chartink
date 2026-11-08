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
    assert c["verdict"] == "Shortlist" and c["source"] == "Screener"
    assert "Valuepick" in fundamentals.label(c)
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
    monkeypatch.setattr(fundamentals, "UPLOADS", tmp_path / "uploads")
    monkeypatch.setattr(fundamentals, "_export", None)
    c = fundamentals.check("GOODCO", fundamentals.FILE)
    assert c and c["source"] == "Yahoo" and c["verdict"] == "Shortlist"


def test_uploads_newest_wins_and_yahoo_fills_gaps(tmp_path, monkeypatch):
    from datetime import date
    up = tmp_path / "uploads"
    up.mkdir()
    today = date.today().isoformat()
    (up / f"{today}_090000.csv").write_text("Name,NSE Code,Promoter holding,Price to Earning\nOld,GOODCO,40,99\nOther,OTHCO,70,10\n")
    (up / f"{today}_100000.csv").write_text("Name,NSE Code,BSE Code,Promoter holding\nNew,GOODCO,500001,65\n")
    (up / "2000-01-01_000000.csv").write_text("Name,NSE Code\nAncient,OLDCO\n")
    monkeypatch.setattr(fundamentals, "FILE", tmp_path / "none.csv")
    monkeypatch.setattr(fundamentals, "UPLOADS", up)
    monkeypatch.setattr(fundamentals, "_export", None)
    rows = fundamentals.export_rows(fundamentals.FILE)
    assert rows["GOODCO"]["Name"] == "New" and rows["500001"]["Name"] == "New"
    assert "OTHCO" in rows and "OLDCO" not in rows and rows["_asof"] == today
    fundamentals._yahoo.clear()
    monkeypatch.setattr(fundamentals, "_yahoo_row", lambda s: {**ROW, "Price to Earning": "12"} if s == "GOODCO" else None)
    c = fundamentals.check("GOODCO", fundamentals.FILE)
    assert c["source"] == "Screener + Yahoo" and c["promoter"] == 65 and c["pe"] == 12



SCREEN_OK = {"Current Price": "95", "High price": "100", "Market Capitalization": "2000",
             "Return on capital employed": "22", "OPM": "14", "Debt to equity": "0.3",
             "Pledged percentage": "0", "Promoter holding": "62", "Profit growth": "45",
             "YOY Quarterly profit growth": "", "Debtor days": "60", "Price to Earning": "15"}


def test_main_screen_pass_and_fail_reasons():
    import main_screen as ms
    r = ms.evaluate(SCREEN_OK)
    assert r["ok"] and r["passed"] == 10 and not r["unknown"]
    bad = ms.evaluate({**SCREEN_OK, "Price to Earning": "44", "Market Capitalization": "51593",
                       "Profit growth": "12", "YOY Quarterly profit growth": "150"})
    assert not bad["ok"] and len(bad["fails"]) == 2          # quarterly growth > 100 rescues profit growth
    assert any(f.startswith("P/E 44") for f in bad["fails"])
    assert ms.label(bad).startswith("Your screen ✗ 2 fail")


def test_main_screen_missing_pledge_not_a_fail():
    import main_screen as ms
    r = ms.evaluate({**SCREEN_OK, "Pledged percentage": ""})
    assert r["ok"] and r["unknown"] == ["Pledge"] and "pledge not checked" in ms.label(r)


def test_main_screen_needs_enough_data():
    import main_screen as ms
    r = ms.evaluate({"Market Capitalization": "2000", "Promoter holding": "70"})
    assert not r["ok"] and not r["fails"] and ms.label(r).startswith("Your screen ? only 2/")
