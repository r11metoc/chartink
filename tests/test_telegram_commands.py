import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import telegram_commands as tc  # noqa: E402


def test_pending_keeps_only_our_chat_commands(monkeypatch):
    ups = [{"update_id": 5, "message": {"chat": {"id": 111}, "text": "/holdings"}},
           {"update_id": 6, "message": {"chat": {"id": 999}, "text": "/holdings"}},   # stranger
           {"update_id": 7, "message": {"chat": {"id": 111}, "text": "hello"}},
           {"update_id": 8, "message": {"chat": {"id": 111}, "text": "/Today@my_bot extra"}}]
    monkeypatch.setattr(tc, "_api", lambda *a, **k: ups)
    cmds, last = tc.pending("t", "111")
    assert cmds == ["holdings", "today"] and last == 8


def test_main_answers_each_command_once(monkeypatch):
    sent, calls = [], []
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "t")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111")
    monkeypatch.setattr(tc, "pending", lambda t, c: (["help", "help", "nope"], 9))
    monkeypatch.setattr(tc, "_api", lambda t, m, **k: calls.append((m, k)))
    monkeypatch.setattr(tc, "send_telegram_message", sent.append)
    assert tc.main() == 0
    assert ("getUpdates", {"offset": 10, "timeout": 0}) in calls
    assert len(sent) == 2 and "Unknown command /nope" in sent[1]
