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


FRAG = """<ul class="list-links">
<li><a href="#"> Announcement under Regulation 30 (LODR)-Analyst / Investor Meet - Intimation
  <div class="ink-600 smaller"><time datetime="2026-11-07">7 Nov</time> - Intimation of conference call.</div></a></li>
<li><a href="#"> Board Meeting Intimation for Board Meeting To Be Held On 12Th November, 2026.
  <div class="ink-600 smaller"><time datetime="2026-10-27">27 Oct</time> - Board meets on 12 Nov 2026 to approve Q2 results.</div></a></li>
<li><a href="#"> Board Meeting Intimation for dividend <div><time>2 Oct</time> - meeting on 15/12/2026</div></a></li>
<li><a href="#"> Board Meeting Intimation for Financial Results For The Quarter Ended September 30, 2026.
  <div><time>5 Nov</time> - Board meets November 13, 2026 to approve Q2 results.</div></a></li>
<li><a href="#"> Grant Of Options <div><time>26 Oct</time> - granted on 24 October 2026.</div></a></li>
</ul>"""


def test_parse_events_reads_board_meeting_dates():
    ev = sc.parse_events(FRAG)
    assert ev == [{"date": "2026-11-12", "what": "results"}, {"date": "2026-12-15", "what": "board meeting"},
                  {"date": "2026-11-13", "what": "results"}]


def test_refresh_events_uses_company_id(tmp_path, monkeypatch):
    import json
    cache = tmp_path / "c.json"
    cache.write_text(json.dumps({"ALICON": {"fetched_at": "2026-11-09T00:00:00+00:00", "data": {"Company ID": "127"}},
                                 "NOID": {"fetched_at": "2026-11-09T00:00:00+00:00", "data": {}}}))
    monkeypatch.setattr(sc, "CACHE", cache)
    monkeypatch.setattr(sc, "_mem", None)
    urls = []
    assert sc.refresh_events(["ALICON", "NOID"], get=lambda u: urls.append(u) or Resp(200, FRAG), sleep=lambda s: None) == 1
    assert urls == ["https://www.screener.in/announcements/recent/127/"]
    assert sc.events("ALICON")[0] == {"date": "2026-11-12", "what": "results"}
