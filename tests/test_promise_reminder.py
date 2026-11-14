"""The reminder speaks only about a marker that stayed open five turn starts, and says plainly when it cannot look.

walk-41e1232f1a3a. WHAT THIS DOES NOT COVER: that the harness runs the hook at Stop (the wiring test in
test_stall_on_promise.py reads settings.json for that), and whether the recorder catches a promise in the first
place (a promise it never recorded has no marker, so nothing here can hold it).
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest

from divineos.core import hold_log, promise_markers as pm
from divineos.core.promise_reminder import reminder_for

HOOKS = Path(__file__).resolve().parents[1] / ".claude" / "hooks"


@pytest.fixture(autouse=True)
def _own_hold_log(tmp_path, monkeypatch):
    monkeypatch.setattr(hold_log, "_log_path", lambda: tmp_path / "hold_log.jsonl")


def _folder(tmp_path, now_turn=100):
    folder = tmp_path / "promise_markers"
    folder.mkdir()
    pm.advance_turn_now(folder, "s1", now_turn)
    return folder


def _marker(folder, name, turn, text="I'll write Aether back", at=None):
    data = {
        "shape": "explicit_future",
        "promise_text": text,
        "detected_at_ts": at if at is not None else time.time() - 3600,
    }
    if turn is not None:
        data["turn_index"] = turn
    (folder / name).write_text(json.dumps(data), encoding="utf-8")


def test_a_young_marker_is_not_due(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 96)
    result = reminder_for(folder, roots=[])
    assert result.status == "nothing_due" and result.text == ""


def test_a_marker_five_turn_starts_old_is_due_and_names_itself(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 95, text="I'll write Aether back about the door")
    result = reminder_for(folder, roots=[])
    assert result.status == "due"
    assert "I'll write Aether back about the door" in result.text
    assert "promise_a" in result.text and "5 turn starts" in result.text


def test_a_marker_written_this_turn_is_never_due(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 100)
    assert reminder_for(folder, roots=[]).status == "nothing_due"


def test_the_reminder_carries_the_three_ways_to_close_it(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    text = reminder_for(folder, roots=[]).text
    assert "divineos promise close promise_a --done" in text
    assert "--waiting-on" in text and "--false-alarm" in text


def test_files_written_since_the_promise_are_named_and_older_ones_are_not(tmp_path):
    folder = _folder(tmp_path)
    root = tmp_path / "work"
    root.mkdir()
    old, new = root / "older_note.md", root / "newer_note.md"
    old.write_text("x")
    new.write_text("x")
    promised = time.time() - 600
    os.utime(old, (promised - 500, promised - 500))
    os.utime(new, (promised + 100, promised + 100))
    _marker(folder, "promise_a.json", 90, at=promised)
    text = reminder_for(folder, roots=[root]).text
    assert "newer_note.md" in text and "older_note.md" not in text


def test_the_closes_so_far_by_kind_are_in_front_of_me(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_gone.json", 80, text="I'll check the thing")
    pm.close(folder, "promise_gone", "false-alarm", "that was a hope and not a promise at all", 100)
    _marker(folder, "promise_a.json", 90)
    text = reminder_for(folder, roots=[]).text
    assert "false-alarm: 1" in text


def test_a_missing_clock_is_could_not_look_never_nothing_due(tmp_path):
    folder = tmp_path / "promise_markers"
    folder.mkdir()
    _marker(folder, "promise_a.json", 1)
    result = reminder_for(folder, roots=[])
    assert result.status == "could_not_look" and "turn count" in result.why


def test_a_missing_folder_is_could_not_look(tmp_path):
    result = reminder_for(tmp_path / "nope", roots=[])
    assert result.status == "could_not_look" and "folder" in result.why


def test_an_unreadable_marker_with_nothing_else_due_is_could_not_look(tmp_path):
    folder = _folder(tmp_path)
    (folder / "promise_bad.json").write_text("{ not json", encoding="utf-8")
    result = reminder_for(folder, roots=[])
    assert result.status == "could_not_look" and "promise_bad.json" in result.why


def test_an_unreadable_marker_beside_a_due_one_still_reminds_and_says_so(tmp_path):
    folder = _folder(tmp_path)
    (folder / "promise_bad.json").write_text("{ not json", encoding="utf-8")
    _marker(folder, "promise_a.json", 90)
    result = reminder_for(folder, roots=[])
    assert result.status == "due" and "promise_bad.json" in result.text


def test_an_undated_marker_never_falls_due_but_is_named_in_the_notes(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_old.json", None)
    result = reminder_for(folder, roots=[])
    assert result.status == "nothing_due" and any("promise_old.json" in n for n in result.notes)


def test_a_marker_waiting_on_someone_is_re_dated_and_not_due(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 80)
    pm.close(folder, "promise_a", "waiting-on", "Dad", 100)
    assert reminder_for(folder, roots=[]).status == "nothing_due"


def _hook():
    sys.path.insert(0, str(HOOKS))
    import stall_on_promise_stop as hook

    return hook


def test_the_hook_holds_for_a_due_marker_and_logs_it(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    reason = _hook().decide(folder, roots=[], stop_hook_active=False)
    assert reason and "promise_a" in reason
    assert ("follow_through", "stopped") in [(r["hold"], r["outcome"]) for r in hold_log.read_all()]


def test_the_hook_is_silent_when_nothing_is_due(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 98)
    assert _hook().decide(folder, roots=[], stop_hook_active=False) is None
    assert ("follow_through", "passed") in [(r["hold"], r["outcome"]) for r in hold_log.read_all()]


def _outcomes():
    return [(r["hold"], r["outcome"]) for r in hold_log.read_all()]


def test_a_second_stop_in_the_same_reply_passes_but_leaves_a_deferred_row(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    assert _hook().decide(folder, roots=[], stop_hook_active=True) is None
    assert ("follow_through", "deferred") in _outcomes()


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize("state", ["nothing_due", "due", "could_not_look"])
def test_every_status_and_stop_has_one_answer(tmp_path, state, active):
    """The six cases (Turing): what is written and whether it blocks, for each status and each stop of a reply."""
    if state == "could_not_look":
        folder = tmp_path / "nope"
    else:
        folder = _folder(tmp_path)
        _marker(folder, "promise_a.json", 90 if state == "due" else 99)
    reason = _hook().decide(folder, roots=[], stop_hook_active=active)
    expected_block = not active and state in ("due", "could_not_look")
    assert bool(reason) is expected_block
    rows = _outcomes()
    if active:
        assert rows == ([("follow_through", "deferred")] if state == "due" else [])
    else:
        assert rows == [
            (
                "follow_through",
                {"nothing_due": "passed", "due": "stopped", "could_not_look": "could_not_look"}[
                    state
                ],
            )
        ]


def test_a_passed_row_says_how_many_promises_are_open(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 99)
    _marker(folder, "promise_b.json", 98)
    _hook().decide(folder, roots=[], stop_hook_active=False)
    assert "2 open" in hold_log.read_all()[0]["first_words"]


def test_the_hook_reads_the_same_folder_the_command_line_does(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert pm.default_folder() == tmp_path / ".divineos" / "promise_markers"
    (tmp_path / ".divineos-aria").mkdir()
    assert pm.default_folder() == tmp_path / ".divineos-aria" / "promise_markers"
    assert "default_folder" in (HOOKS / "stall_on_promise_stop.py").read_text(encoding="utf-8")


def test_the_marker_keys_the_reminder_reads_are_the_ones_the_recorder_writes():
    """A rename in either place fails here, so tests that hand-make markers cannot drift from the real shape."""
    recorder = (HOOKS / "promise-reach-detector.sh").read_text(encoding="utf-8")
    for key in ("promise_text", "detected_at_ts", "turn_index"):
        assert key in recorder, key


def _run_hook(tmp_path, folder_home, payload):
    import subprocess

    env = {**os.environ, "HOME": str(folder_home), "USERPROFILE": str(folder_home)}
    env["STALL_ON_PROMISE_MARK"] = str(tmp_path / "mark.txt")
    env["DIVINEOS_HOME"] = str(tmp_path / "dhome")
    return subprocess.run(
        [sys.executable, str(HOOKS / "stall_on_promise_stop.py")],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def test_the_hook_script_itself_blocks_on_a_due_marker(tmp_path):
    home = tmp_path / "home"
    folder = home / ".divineos" / "promise_markers"
    folder.mkdir(parents=True)
    pm.advance_turn_now(folder, "s1", 100)
    _marker(folder, "promise_a.json", 90)
    out = _run_hook(tmp_path, home, {"stop_hook_active": False})
    assert json.loads(out.stdout)["decision"] == "block"
    assert "promise_a" in json.loads(out.stdout)["reason"]


def test_the_hook_script_itself_blocks_loudly_when_it_cannot_look(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    out = _run_hook(tmp_path, home, {"stop_hook_active": False})
    assert "could not look" in json.loads(out.stdout)["reason"]


def test_a_crash_inside_the_hook_is_shown_once_and_never_loops(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    first = _run_hook(tmp_path, home, {"stop_hook_active": False, "transcript_path": 5})
    assert first.stdout.strip() and json.loads(first.stdout)["decision"] == "block"
    second = _run_hook(tmp_path, home, {"stop_hook_active": True, "transcript_path": 5})
    assert second.stdout.strip() == ""


def test_the_block_repeats_on_the_next_reply_until_the_marker_is_closed(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    hook = _hook()
    assert hook.decide(folder, roots=[], stop_hook_active=False)
    assert hook.decide(folder, roots=[], stop_hook_active=False)
    pm.close(folder, "promise_a", "false-alarm", "that was a hope and not a promise at all", 100)
    assert hook.decide(folder, roots=[], stop_hook_active=False) is None


def test_a_blind_reader_says_so_once_and_is_logged_as_could_not_look(tmp_path):
    reason = _hook().decide(tmp_path / "nope", roots=[], stop_hook_active=False)
    assert reason and "could not look" in reason
    assert ("follow_through", "could_not_look") in _outcomes()


def test_each_close_has_an_age_in_turn_starts_read_from_the_log(tmp_path):
    from divineos.core.promise_reminder import close_ages

    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 93)
    pm.close(folder, "promise_a", "false-alarm", "that was a hope and not a promise at all", 100)
    assert close_ages(folder) == [7]
