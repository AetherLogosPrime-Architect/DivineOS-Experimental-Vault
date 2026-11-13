"""Promises are recorded, closed by one explicit line, and age in turns, never in minutes.

Dad, 2026-11-13: record the promise, give me a chance to do it, and "if after 5 or so turns you havent done
anything about it, even recording it to a file and linking it, it reminds you and blocks you until you do".
Two walks (walk-82220bd46c30, walk-6e90bce7c85e) fixed the shape this pins:
- age is counted in TURN STARTS (his message, a letter, a timer wake) taken from the transcript, because in the
  night he sends no messages and a promise would never age (Breaker, Lamport);
- a marker closes only by an explicit one-line close, never by guessing from tool calls (Taleb, Turing);
- "done" must point at a file written AFTER the promise was recorded, since any file exists (Breaker);
- "waiting on someone" does not close a promise, it re-dates it, so a name never hides one (Taleb);
- every close is appended to a log, so a run of cheap closes shows as a rate (Schneier);
- reading the folder has a fifth answer, could not look, never read as "nothing open" (Hoare);
- the turn count is checked against an independent count on a real stamped transcript (Dillahunty).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from divineos.core import promise_markers as pm


def _marker(folder: Path, name: str, text: str, turn: int | None, **extra) -> Path:
    data: dict = {
        "shape": "explicit_future",
        "promise_text": text,
        "trigger_phrase": text,
        "detected_at_ts": time.time() - 60,
    }
    if turn is not None:
        data["turn_index"] = turn
    data.update(extra)
    path = folder / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _user(origin: str | None):
    rec: dict = {"type": "user", "message": {"role": "user", "content": "x"}}
    if origin:
        rec["turnOrigin"] = origin
    return rec


def _fresh_file(folder: Path, name: str = "draft.md") -> Path:
    """A file written AFTER the marker (the marker above is stamped a minute in the past)."""
    f = folder / name
    f.write_text("the deed", encoding="utf-8")
    return f


# ---- turns are counted from the harness's own stamp, not from minutes ----------------------------


def test_turn_starts_count_his_message_a_wake_and_a_notice_and_nothing_else():
    records = [
        _user("human"),
        {"type": "assistant", "message": {"role": "assistant", "content": []}},
        _user("scheduled"),
        _user("task_notification"),
        _user(None),  # a tool result or an unstamped record is not a turn start
        {"type": "assistant", "message": {"role": "assistant", "content": []}},
    ]
    assert pm.turn_index(records) == 3


def test_an_empty_transcript_is_turn_zero():
    assert pm.turn_index([]) == 0


def test_the_count_matches_an_independent_count_on_a_real_stamped_transcript(tmp_path):
    """The burden of proof is on the claim 'counts turns correctly' (Dillahunty): the module's number against a
    count taken a second way, over a file with all the stamp kinds in it, not records I built to suit it."""
    lines = []
    for origin in [
        "human",
        None,
        "scheduled",
        None,
        None,
        "human",
        "task_notification",
        "weird-new-kind",
        None,
    ]:
        lines.append(json.dumps(_user(origin)))
        lines.append(
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": []}})
        )
    transcript = tmp_path / "session.jsonl"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    records = [json.loads(line) for line in transcript.read_text(encoding="utf-8").splitlines()]
    independent = sum(
        1
        for r in records
        if r.get("type") == "user"
        and r.get("turnOrigin") in ("human", "scheduled", "task_notification")
    )
    assert independent == 4
    assert pm.turn_index(records) == independent


# ---- a marker is open until one explicit close ----------------------------------------------------


def test_a_fresh_marker_is_open_and_not_yet_due(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=10)
    state = pm.read_folder(tmp_path)
    assert [m.name for m in state.open] == ["promise_a.json"]
    assert pm.due(state.open, current_turn=12) == []


def test_a_marker_is_due_only_after_five_turn_starts(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=10)
    state = pm.read_folder(tmp_path)
    assert pm.due(state.open, current_turn=14) == []
    assert [m.name for m in pm.due(state.open, current_turn=15)] == ["promise_a.json"]


def test_a_marker_with_no_turn_is_never_guessed_due(tmp_path):
    """An older marker written before turns were stored has no age; it is listed, not blocked on."""
    _marker(tmp_path, "promise_old.json", "I will do it", turn=None)
    state = pm.read_folder(tmp_path)
    assert [m.name for m in state.open] == ["promise_old.json"]
    assert pm.due(state.open, current_turn=999) == []
    assert [m.name for m in state.undated] == ["promise_old.json"]


# ---- done: a file that exists AND was written after the promise ------------------------------------


def test_done_needs_a_file_that_exists(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=1)
    with pytest.raises(pm.CloseRefused, match="file"):
        pm.close(tmp_path, "promise_a", "done", str(tmp_path / "nope.md"))


def test_done_refuses_a_file_older_than_the_promise(tmp_path):
    """Any file exists. A stale README must not stand in for the deed."""
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=1)
    old = tmp_path / "old.md"
    old.write_text("old", encoding="utf-8")
    two_minutes_ago = time.time() - 120
    os.utime(old, (two_minutes_ago, two_minutes_ago))
    with pytest.raises(pm.CloseRefused, match="after"):
        pm.close(tmp_path, "promise_a", "done", str(old))
    assert [m.name for m in pm.read_folder(tmp_path).open] == ["promise_a.json"]


def test_done_with_a_file_written_after_the_promise_closes_it(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=1)
    pm.close(tmp_path, "promise_a", "done", str(_fresh_file(tmp_path)))
    assert pm.read_folder(tmp_path).open == []


# ---- waiting on someone re-dates, it never closes -------------------------------------------------


def test_waiting_on_needs_a_name(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will send it after he says go", turn=1)
    with pytest.raises(pm.CloseRefused, match="who"):
        pm.close(tmp_path, "promise_a", "waiting-on", "  ", current_turn=3)


def test_waiting_on_keeps_the_promise_open_and_resets_its_age(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will send it after he says go", turn=1)
    pm.close(tmp_path, "promise_a", "waiting-on", "Dad", current_turn=20)
    state = pm.read_folder(tmp_path)
    assert [m.name for m in state.open] == ["promise_a.json"], (
        "a promise that waits must not vanish behind a name"
    )
    assert pm.due(state.open, current_turn=24) == []
    assert [m.name for m in pm.due(state.open, current_turn=25)] == ["promise_a.json"]
    assert state.open[0].data["waiting_on"][-1]["who"] == "Dad"


# ---- a false alarm needs a reason of real length ---------------------------------------------------


def test_a_false_alarm_needs_a_reason_of_real_length(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will keep trying", turn=1)
    with pytest.raises(pm.CloseRefused, match="reason"):
        pm.close(tmp_path, "promise_a", "false-alarm", "nope")
    pm.close(
        tmp_path, "promise_a", "false-alarm", "a stance about conduct, nothing a tool could do"
    )
    assert pm.read_folder(tmp_path).open == []


# ---- every close is kept, never deleted, and logged ------------------------------------------------


def test_a_close_is_kept_in_the_marker_not_deleted(tmp_path):
    path = _marker(tmp_path, "promise_a.json", "I will write the draft", turn=1)
    pm.close(
        tmp_path, "promise_a", "false-alarm", "a figure of speech inside a picture, not a step"
    )
    assert path.exists(), "append-only: a closed marker stays, with its close recorded"
    assert json.loads(path.read_text(encoding="utf-8"))["closed"]["kind"] == "false-alarm"


def test_every_close_is_appended_to_a_log_so_cheap_closes_show_as_a_rate(tmp_path):
    _marker(tmp_path, "promise_a.json", "one", turn=1)
    _marker(tmp_path, "promise_b.json", "two", turn=1)
    pm.close(tmp_path, "promise_a", "false-alarm", "a reason that is long enough to count here")
    pm.close(tmp_path, "promise_b", "done", str(_fresh_file(tmp_path)))
    rows = [
        json.loads(line)
        for line in (tmp_path / "closes.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [r["kind"] for r in rows] == ["false-alarm", "done"]
    assert pm.close_counts(tmp_path) == {"false-alarm": 1, "done": 1}


def test_closing_an_unknown_prefix_says_so(tmp_path):
    with pytest.raises(pm.CloseRefused, match="no marker"):
        pm.close(tmp_path, "promise_zzz", "false-alarm", "a reason that is long enough to count")


def test_an_ambiguous_prefix_is_refused_not_guessed(tmp_path):
    _marker(tmp_path, "promise_a1.json", "one", turn=1)
    _marker(tmp_path, "promise_a2.json", "two", turn=1)
    with pytest.raises(pm.CloseRefused, match="more than one"):
        pm.close(tmp_path, "promise_a", "false-alarm", "a reason that is long enough to count")


def test_an_unknown_kind_is_refused(tmp_path):
    _marker(tmp_path, "promise_a.json", "one", turn=1)
    with pytest.raises(pm.CloseRefused, match="kind"):
        pm.close(
            tmp_path, "promise_a", "forgotten", "whatever reason long enough to pass the length"
        )


# ---- reading the folder: could-not-look is its own answer -----------------------------------------


def test_a_corrupt_marker_is_could_not_look_not_nothing(tmp_path):
    (tmp_path / "promise_bad.json").write_text("{not json", encoding="utf-8")
    state = pm.read_folder(tmp_path)
    assert state.open == []
    assert state.unreadable == ["promise_bad.json"], (
        "a corrupt marker must be said, never read as clean"
    )


def test_a_missing_folder_is_could_not_look(tmp_path):
    state = pm.read_folder(tmp_path / "does_not_exist")
    assert state.folder_missing is True


def test_an_empty_folder_is_honestly_empty(tmp_path):
    """Control: empty is found-nothing, and must not be reported as could-not-look."""
    state = pm.read_folder(tmp_path)
    assert state.open == [] and state.folder_missing is False and state.unreadable == []
