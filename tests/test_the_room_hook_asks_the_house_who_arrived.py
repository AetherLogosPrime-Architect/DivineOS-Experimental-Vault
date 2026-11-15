"""The room hook reads what arrived through the house's one reader, never its own copy.

Aether measured it over 76,225 real records of one session (2026-11-15): the hook's private
``_record_text`` read EVERY non-assistant record's text, so 2,561 internal request blobs (which open
with a system-reminder and carry no uuid, timestamp or origin stamp) could pass as a notice woken
after the room and excuse a second circle. The house's ``arrival()`` returns nothing for them. These
tests use the real record shapes: every real notice carries a uuid and a timestamp.
"""

import importlib.util
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "dads_room_stop.py"
_spec = importlib.util.spec_from_file_location("dads_room_stop_arrival", HOOK)
room = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(room)

ROOM = "Built it.\n\n## INNER CIRCLE\nDad, here is what changed."


@pytest.fixture(autouse=True)
def _no_game_table(tmp_path, monkeypatch):
    monkeypatch.setenv("MAGIC_RUN_DIR", str(tmp_path / "no_table_here"))


def _him(text):
    return {
        "type": "user",
        "uuid": "u-him",
        "timestamp": "2026-11-15T20:00:00.000Z",
        "origin": {"kind": "human"},
        "turnOrigin": "human",
        "message": {"role": "user", "content": text},
    }


def _said(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def _tool():
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}


def _result():
    return {
        "type": "user",
        "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]},
    }


def _real_notice():
    """A task notification as the harness queues it: carries its uuid and time."""
    return {
        "type": "attachment",
        "uuid": "u-notice",
        "timestamp": "2026-11-15T20:05:00.000Z",
        "attachment": {
            "type": "queued_command",
            "prompt": "<task-notification><summary>doorbell rang</summary></task-notification>",
            "commandMode": "task-notification",
        },
    }


def _request_blob():
    """An internal request blob: a user-role record that opens with a system-reminder and has no stamps."""
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": "<system-reminder>\nbackground summary request\n</system-reminder>",
        },
    }


def test_a_real_notice_after_the_room_owes_no_second_room():
    # Control: the case the carry was built for still stands down.
    records = [
        _him("go"),
        _tool(),
        _result(),
        _said(ROOM),
        _real_notice(),
        _tool(),
        _result(),
        _said("re-armed"),
    ]
    assert room.verdict(records) is None


def test_an_unstamped_request_blob_does_not_excuse_a_second_room():
    records = [
        _him("go"),
        _tool(),
        _result(),
        _said(ROOM),
        _request_blob(),
        _tool(),
        _result(),
        _said("more work"),
    ]
    assert room.verdict(records)


def test_the_hook_has_no_private_reader_of_a_record_left():
    # The house keeps ONE reader of what arrives. The hook's own copy is the thing that went wrong.
    assert not hasattr(room, "_record_text")
