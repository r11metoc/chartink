import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from scrape_dashboard import match_names  # noqa: E402

NAMES = ["63_30_daily", "Bullish_Scanner", "Wkly_upswing"]


def test_names_follow_titles_not_position():
    assert match_names(["Bullish_Scanner", "Wkly_upswing", "63_30_daily"], NAMES) == \
        ["Bullish_Scanner", "Wkly_upswing", "63_30_daily"]


def test_missing_widget_is_left_out():
    assert match_names([None, "Bullish_Scanner", "Wkly_upswing"], NAMES) == [None, "Bullish_Scanner", "Wkly_upswing"]


def test_untrusted_titles_fall_back():
    assert match_names([None, None], NAMES) is None
    assert match_names(["Bullish_Scanner", "Bullish_Scanner"], NAMES) is None
