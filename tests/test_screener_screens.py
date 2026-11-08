import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import screener_screens as ss  # noqa: E402
from market_data import to_yahoo_ticker  # noqa: E402

PAGE = """<h1 class="margin-0">
        Hitting_Highs
    </h1> 75 results found: Showing page 1 of 3
<table class="data-table"><tbody>
<tr><th><a href="?sort=name&amp;order=desc">Company</a></th></tr>
<tr data-row-company-id="1"><td class="text">1.</td><td class="text">
  <a href="/company/SAMBHV/" target="_blank">Sambhv Steel</a></td><td>167.75</td></tr>
<tr data-row-company-id="2"><td class="text">2.</td><td class="text">
  <a href="/company/515008/consolidated/" target="_blank">Modern Insulator</a></td></tr>
<tr data-row-company-id="3"><td class="text">3.</td><td class="text">
  <a href="/company/PNGSREVA/" target="_blank">PNGS Reva Diamo.</a></td></tr>
</tbody></table><a href="/company/OTHER/">not in table</a>"""


def test_parse_reads_title_total_and_companies():
    got = ss.parse(PAGE)
    assert got["title"] == "Hitting_Highs"
    assert got["total"] == 75
    assert got["stocks"] == [("SAMBHV", "Sambhv Steel"), ("515008", "Modern Insulator"), ("PNGSREVA", "PNGS Reva Diamo.")]


def test_screen_urls_drop_query_strings(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text("# c\nhttps://www.screener.in/screens/1/x/?page=2\nhttps://example.com/no\n")
    assert ss.screen_urls(f) == ["https://www.screener.in/screens/1/x/"]


def test_bse_codes_map_to_bo():
    assert to_yahoo_ticker("515008") == "515008.BO"
    assert to_yahoo_ticker("SAMBHV") == "SAMBHV.NS"


def test_metrics_and_rank():
    def bars(path):
        return [(f"d{i:03d}", p, p * 1.01, p * 0.99, p) for i, p in enumerate(path)]
    up = bars([100 + i * 0.5 for i in range(260)])            # steady trend, at the high
    pull = bars([100 + i for i in range(200)] + [300 - 2 * i for i in range(60)])  # fell back
    m_up, m_pull = ss.metrics(up), ss.metrics(pull)
    assert m_up["vs50"] > 0 and m_pull["vs50"] < 0
    assert m_pull["below_high"] < m_up["below_high"] <= 0
    assert ss.metrics(up[:30]) is None
    rows = ss.rank([{"symbol": "A", **m_up}, {"symbol": "B", **m_pull}, {"symbol": "C"}])
    assert [r["symbol"] for r in rows][-1] == "C" and "score" not in rows[-1]
    assert rows[0]["rank"] == 1 and 0 <= rows[0]["score"] <= 100


def test_view_uses_saved_list(monkeypatch):
    conn = sqlite3.connect(":memory:")
    ss._ensure(conn)
    conn.execute("INSERT INTO screen_stocks VALUES ('u', 'T', 75, 0, 'SAMBHV', 'Sambhv', '2026-11-08T00:00:00+00:00')")
    monkeypatch.setattr(ss.db, "daily_prices_since", lambda c, s, d: [])
    v = ss.view(conn, {"SAMBHV"})
    assert v[0]["title"] == "T" and v[0]["total"] == 75
    assert v[0]["stocks"][0]["on_scanner"] is True
