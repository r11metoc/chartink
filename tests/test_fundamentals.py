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
