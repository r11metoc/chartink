import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import db  # noqa: E402



def test_half_read_scan_is_undone(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    c = db.connect()
    full = ["A", "B", "C"]
    for when, syms in [("2026-11-09T02:00:00+00:00", full), ("2026-11-09T02:20:00+00:00", ["A"]),
                       ("2026-11-09T02:40:00+00:00", full)]:
        rid = db.create_run(c)
        c.execute("UPDATE runs SET run_at = ? WHERE id = ?", (when, rid))
        db.save_results(c, rid, "S", [{"_symbol": s} for s in syms])
    for s in ("B", "C"):  # what the third scan wrongly recorded
        db.record_breakout(c, 3, "S", s, {}, kind="retest")
    assert db.repair_partial_reads(c) == 1
    assert db.previous_run_id(c, "S", 3) == 1
    assert c.execute("SELECT COUNT(*) FROM breakouts").fetchone()[0] == 0
    assert db.repair_partial_reads(c) == 0  # idempotent


def test_real_drop_hours_later_is_kept(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    c = db.connect()
    for when, syms in [("2026-11-09T04:00:00+00:00", ["A", "B"]), ("2026-11-09T07:00:00+00:00", ["A"]),
                       ("2026-11-10T04:00:00+00:00", ["A", "B"])]:
        rid = db.create_run(c)
        c.execute("UPDATE runs SET run_at = ? WHERE id = ?", (when, rid))
        db.save_results(c, rid, "S", [{"_symbol": s} for s in syms])
    assert db.repair_partial_reads(c) == 0
