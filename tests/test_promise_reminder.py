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


def test_the_retry_of_its_own_block_passes_but_leaves_a_deferred_row(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    hold_log.record("follow_through", "stopped", "promise_a.json")
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
    if state == "due" and active:
        hold_log.record(
            "follow_through", "stopped", "promise_a.json"
        )  # so this stop is its own retry
    seeded = len(hold_log.read_all())
    reason = _hook().decide(folder, roots=[], stop_hook_active=active)
    expected_block = not active and state in ("due", "could_not_look")
    assert bool(reason) is expected_block
    rows = _outcomes()[seeded:]
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


def _seed_rows(*outcomes):
    for outcome in outcomes:
        hold_log.record("follow_through", outcome, "seed")


def _due_folder(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    return folder


@pytest.mark.parametrize(
    "rows,blocks",
    [
        ((), True),  # empty log: nothing says this hook blocked, so the flag came from another gate
        (("passed",), True),
        (("deferred",), True),
        (("could_not_look",), True),
        (("stopped",), False),  # the retry of its own block passes
        (("stopped", "deferred"), True),
        (("deferred", "deferred", "stopped"), False),
    ],
)
def test_a_second_stop_blocks_unless_it_is_the_retry_of_its_own_block(tmp_path, rows, blocks):
    """walk-9c155ee1c052: the harness sets stop_hook_active after ANY gate refused, so the doorbell starved this."""
    folder = _due_folder(tmp_path)
    _seed_rows(*rows)
    reason = _hook().decide(folder, roots=[], stop_hook_active=True)
    assert bool(reason) is blocks
    assert _outcomes()[-1] == ("follow_through", "stopped" if blocks else "deferred")


def test_the_hook_reads_its_rows_only_through_hold_log_and_parses_nothing_itself():
    """walk-aaa47de00741 (Bengio, Peirce): one reader, so a fix to corrupt-line handling is made once."""
    import inspect

    source = inspect.getsource(_hook()._rows_or_none)
    assert "read_all(" in source
    assert "json.loads" not in source and "read_text" not in source


def test_a_shadow_row_after_a_stopped_row_does_not_hide_that_it_was_the_retry(tmp_path):
    """The shadow of the old judgement is another hold; the last row of THIS hold decides (Dennett)."""
    folder = _due_folder(tmp_path)
    hold_log.record("follow_through", "stopped", "promise_a.json")
    hold_log.record("follow_through_old", "passed", "something")
    assert _hook().decide(folder, roots=[], stop_hook_active=True) is None


def test_a_repeated_block_says_how_many_times_it_has_held_for_that_marker(tmp_path):
    folder = _due_folder(tmp_path)
    hold_log.record("follow_through", "stopped", "promise_a.json")
    hold_log.record("follow_through", "deferred", "promise_a.json")
    reason = _hook().decide(folder, roots=[], stop_hook_active=True)
    assert reason and "held 1 time" in reason and "promise_a" in reason


def test_the_reminder_never_blocks_two_stops_in_a_row_over_a_long_volley(tmp_path):
    """The invariant (Dijkstra): over a run of second stops with a due marker it blocks, then passes the retry,
    then blocks again, so it is never starved and never blocks twice in a row."""
    folder = _due_folder(tmp_path)
    hook = _hook()
    verdicts = [bool(hook.decide(folder, roots=[], stop_hook_active=True)) for _ in range(40)]
    assert verdicts == [i % 2 == 0 for i in range(40)]


def test_an_unreadable_hold_log_never_blocks_a_second_stop(tmp_path, monkeypatch):
    folder = _due_folder(tmp_path)
    unreadable = tmp_path / "a_folder_where_the_log_should_be"
    unreadable.mkdir()
    monkeypatch.setattr(hold_log, "_log_path", lambda: unreadable)
    assert _hook().decide(folder, roots=[], stop_hook_active=True) is None


def test_corrupt_lines_are_skipped_not_fatal_and_the_last_good_row_counts(tmp_path, capsys):
    """The real log holds two corrupt lines, and read_all raises on the first; the reminder must still read it."""
    folder = _due_folder(tmp_path)
    log = (
        tmp_path / "hold_log_follow_through.jsonl"
    )  # a single-writer file: a bad line here is a defect and is said
    good = json.dumps(
        {
            "at": "x",
            "t": 5.0,
            "hold": "follow_through",
            "outcome": "stopped",
            "first_words": "promise_a.json",
        }
    )
    log.write_text('igned."}' + chr(10) + "{ not json" + chr(10) + good + chr(10), encoding="utf-8")
    assert (
        _hook().decide(folder, roots=[], stop_hook_active=True) is None
    )  # the retry of its own block
    assert "corrupt line" in capsys.readouterr().err


def test_known_corrupt_history_in_the_old_file_does_not_raise_a_standing_alarm(tmp_path, capsys):
    folder = _due_folder(tmp_path)
    (tmp_path / "hold_log.jsonl").write_text('igned."}' + chr(10), encoding="utf-8")
    hold_log.record("follow_through", "stopped", "promise_a.json")
    assert _hook().decide(folder, roots=[], stop_hook_active=True) is None
    assert "corrupt line" not in capsys.readouterr().err


def test_a_passed_row_says_how_many_promises_are_open(tmp_path):
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 99)
    _marker(folder, "promise_b.json", 98)
    _hook().decide(folder, roots=[], stop_hook_active=False)
    assert "2 open" in hold_log.read_all()[0]["first_words"]


def test_the_hook_reads_the_same_folder_the_command_line_does(tmp_path, monkeypatch):
    """Both ask the one function, and it follows the seat's own data home, not which directories exist."""
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "seat"))
    assert pm.default_folder() == tmp_path / "seat" / "promise_markers"
    assert "default_folder" in (HOOKS / "stall_on_promise_stop.py").read_text(encoding="utf-8")


def test_the_reminder_says_which_folder_it_read_from(tmp_path):
    """walk-eb4440341013 (Norman): a reminder drawn from the wrong seat's promises must not look like a right one."""
    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 90)
    assert f"Read from: {folder}" in reminder_for(folder, roots=[]).text


def test_a_close_log_with_a_bad_byte_still_gives_the_good_ages(tmp_path):
    from divineos.core.promise_reminder import close_ages

    folder = _folder(tmp_path)
    _marker(folder, "promise_a.json", 93)
    pm.close(folder, "promise_a", "false-alarm", "that was a hope and not a promise at all", 100)
    with (folder / "closes.jsonl").open("ab") as handle:
        handle.write(b'{"kind": "done", "marker": "x\xff')
    assert close_ages(folder) == [7]


def test_a_shadow_that_crashes_is_said_and_logged_and_does_not_stop_the_reminder(
    tmp_path, monkeypatch, capsys
):
    """walk-eb4440341013 (Breaker): the old judgement is shadow only, so its failure must not block a reply."""
    hook = _hook()
    folder = _due_folder(tmp_path)
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("", encoding="utf-8")

    def broken(_records):
        raise RuntimeError("the shadow broke")

    monkeypatch.setattr(hook, "verdict", broken)
    monkeypatch.setattr(pm, "default_folder", lambda: folder)
    monkeypatch.setattr(hook, "work_roots", lambda: [])
    code = hook.main(json.dumps({"transcript_path": str(transcript), "stop_hook_active": False}))
    assert code == 0
    assert ("follow_through_old", "could_not_look") in _outcomes()
    assert "the shadow broke" in capsys.readouterr().err
    assert ("follow_through", "stopped") in _outcomes()  # the reminder still spoke


def test_the_marker_keys_the_reminder_reads_are_the_ones_the_recorder_writes():
    """A rename in either place fails here, so tests that hand-make markers cannot drift from the real shape."""
    recorder = (HOOKS / "promise-reach-detector.sh").read_text(encoding="utf-8")
    for key in ("promise_text", "detected_at_ts", "turn_index"):
        assert key in recorder, key


def _run_hook(tmp_path, folder_home, payload):
    import subprocess

    env = {**os.environ, "HOME": str(folder_home), "USERPROFILE": str(folder_home)}
    env["STALL_ON_PROMISE_MARK"] = str(tmp_path / "mark.txt")
    env["DIVINEOS_HOME"] = str(
        folder_home / ".divineos"
    )  # the seat's own home: markers and hold log live under it
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
