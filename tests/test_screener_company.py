import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import screener_company as sc  # noqa: E402

PAGE = (Path(__file__).parent / "fixtures" / "screener_company_demo.html").read_text()


def test_parse_maps_to_screener_columns():
    r = sc.parse(PAGE)
    assert r["Name"] == "Demo Industries Ltd" and r["Industry"] == "Industrial Products"
    assert (r["Market Capitalization"], r["Current Price"], r["High price"], r["Price to Earning"]) == (1234, 450, 500, 15.5)
    assert r["Return on capital employed"] == 22.4 and r["Return on equity"] == 18.0
    assert r["OPM"] == 16  # last full year, not TTM
    assert r["Profit growth"] == 50.0 and r["Sales growth"] == 20.0  # Mar 2026 vs Mar 2025
    assert r["YOY Quarterly profit growth"] == 150.0  # Sep 2026 vs Sep 2025
    assert r["Debt to equity"] == 0.30 and r["Debt"] == 90 and r["Debt Change"] == 30
    assert r["Promoter holding"] == 60.9  # latest quarter
    assert r["Debtor days"] == 82 and r["Debtor Days Ch"] == 12
    assert r["Sales growth 3Years"] == 25 and r["Profit growth 3Years"] == 35
    assert r["CFO"] == 48 and r["Profit after tax"] == 60 and r["Pledged percentage"] == ""


class Resp:
    def __init__(self, code, text=""):
        self.status_code, self.text = code, text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


def test_refresh_caches_and_backs_off(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "CACHE", tmp_path / "c.json")
    monkeypatch.setattr(sc, "_mem", None)
    urls = []

    def get(url):
        urls.append(url)
        return Resp(404) if "NOPE" in url else Resp(403) if "BLOCK" in url else Resp(200, PAGE)
    assert sc.refresh(["GOOD", "NOPE"], get=get, sleep=lambda s: None) == 1
    assert urls[0].endswith("/company/GOOD/consolidated/")
    assert sc.cached("GOOD")["Market Capitalization"] == 1234 and sc.cached("GOOD")["NSE Code"] == "GOOD"
    urls.clear()
    assert sc.refresh(["GOOD"], get=get, sleep=lambda s: None) == 0 and not urls  # fresh, not refetched
    n = sc.refresh([f"BLOCK{i}" for i in range(9)], get=get, sleep=lambda s: None)
    assert n == 0 and len(urls) == sc.MAX_FAILS  # stops after MAX_FAILS failures in a row
    assert "GOOD" in json.loads((tmp_path / "c.json").read_text())
