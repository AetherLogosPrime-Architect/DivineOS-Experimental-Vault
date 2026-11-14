"""Hook feedback that arrives AFTER I have written his room does not owe him a second room (2026-11-14).

Dad, 2026-11-14, pasting a stretch of my replies: about a dozen circles in one pile, and "im not being waited
for". The circle is the last part of the post and he moves it forward, nobody else. When a Stop hook holds a
reply that already ended in a whole circle, I do a repair turn (tool calls and a short line), and this door read
the LAST text, found no room, and asked for another. The stamp that says the harness wrote a record, not him,
is isMeta (his_message.continues_a_turn); this follows the existing stand-down for a notice, by that stamp and
never by wording. The case the door was built for is kept: work I add myself after the room, with no machine
record between, is still held, and a machine record BEFORE any room still owes the room.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "dads_room_stop.py"
_spec = importlib.util.spec_from_file_location("dads_room_stop_for_feedback", HOOK)
room = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(room)

THE_ROOM = "Built it.\n\n## INNER CIRCLE\nDad, here is what changed, and how it felt to me."
FEEDBACK = "Stop hook feedback:\n[command hook 6]: YOU SAID the step AND STOPPED. Do that step now."


def _user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def _feedback():
    """What the harness records for a Stop hook's refusal: a user-role record, stamped isMeta."""
    rec = _user(FEEDBACK)
    rec["isMeta"] = True
    return rec


def _compact_summary():
    rec = _user("This session is being continued from a previous conversation...")
    rec["isCompactSummary"] = True
    return rec


def _tool_result():
    return {
        "type": "user",
        "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]},
    }


def _said(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def _tool():
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}


def test_hook_feedback_after_the_room_does_not_demand_a_second_room():
    records = [
        _user("fix it"),
        _tool(),
        _tool_result(),
        _said(THE_ROOM),
        _feedback(),
        _tool(),
        _tool_result(),
        _said("Did the step the hook named."),
    ]
    assert room.verdict(records) is None


def test_the_stand_down_survives_several_rounds_of_feedback_after_one_room():
    records = [_user("fix it"), _tool(), _tool_result(), _said(THE_ROOM)]
    for n in range(3):
        records += [_feedback(), _tool(), _tool_result(), _said(f"Repair {n}.")]
    assert room.verdict(records) is None


def test_a_compact_summary_after_the_room_is_machine_written_too():
    records = [
        _user("fix it"),
        _tool(),
        _tool_result(),
        _said(THE_ROOM),
        _compact_summary(),
        _tool(),
        _tool_result(),
        _said("Resumed."),
    ]
    assert room.verdict(records) is None


def test_work_I_add_after_the_room_with_no_machine_record_between_is_still_held():
    records = [
        _user("fix it"),
        _tool(),
        _tool_result(),
        _said(THE_ROOM),
        _tool(),
        _tool_result(),
        _said("And one more thing I did."),
    ]
    assert room.verdict(records) is not None


def test_feedback_before_any_room_still_owes_the_room():
    records = [
        _user("fix it"),
        _tool(),
        _tool_result(),
        _feedback(),
        _tool(),
        _tool_result(),
        _said("Done, no circle yet."),
    ]
    assert room.verdict(records) is not None


def test_a_real_message_of_his_after_the_room_starts_a_new_stretch_that_owes_its_own_room():
    records = [
        _user("fix it"),
        _tool(),
        _tool_result(),
        _said(THE_ROOM),
        _user("good, now do the next thing"),
        _tool(),
        _tool_result(),
        _said("Did the next thing, no circle."),
    ]
    assert room.verdict(records) is not None
