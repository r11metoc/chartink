import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import db  # noqa: E402
import market  # noqa: E402


class Resp:
    def raise_for_status(self):
        pass

    def json(self):
        return [{"scrip_Code": "532339", "short_name": "ALICON", "Long_Name": "Alicon", "meeting_date": "12 Nov 2026"},
                {"scrip_Code": "500001", "short_name": "XYZBSE", "Long_Name": "X", "meeting_date": "10 Nov 2026"},
                {"scrip_Code": "9", "short_name": "LATER", "Long_Name": "L", "meeting_date": "30 Nov 2026"},
                {"scrip_Code": "8", "short_name": "BAD", "meeting_date": "soon"}]


def test_calendar_and_matching(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    c = db.connect()
    assert market.refresh_calendar(c, get=lambda u: Resp()) == 3
    assert market.refresh_calendar(c, get=lambda u: Resp()) == 0  # fresh: not refetched
    import screener_company
    monkeypatch.setattr(screener_company, "cached", lambda s: {"BSE Code": "500001"} if s == "XYZ" else None)
    ev = market.upcoming_results(c, ["ALICON", "XYZ", "LATER", "NONE"], today=date(2026, 11, 9))
    assert ev == {"ALICON": "2026-11-12", "XYZ": "2026-11-10"}


def test_pulse_trend(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    c = db.connect()
    days = [d.date().isoformat() for d in __import__("pandas").bdate_range(end=date.today(), periods=260)]
    db.save_daily_prices(c, "^NSEI", [(d, 100 + i, 100 + i, 100 + i, 100 + i) for i, d in enumerate(days)])
    p = market.pulse(c)
    assert p["trend"] == "Uptrend" and p["indexes"][0]["vs50"] > 0 and p["indexes"][0]["vs200"] > 0
