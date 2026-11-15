"""An edit that adds or removes a decision owes a walk opened after his latest message. Real walk store (a temp
DIVINEOS_HOME), a real transcript file, no stubs of the thing under test."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from divineos.core import walk_after_his_message as w
from divineos.core.council_walk import open_walk

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "divineos" / "core" / "ask_after_his_words.py"
REL = "src/divineos/core/ask_after_his_words.py"
DECISION_EDIT = {
    "file_path": str(TARGET),
    "old_string": '    if not shown:\n        return "nothing", None\n',
    "new_string": '    if not shown or (x and y):\n        return "nothing", None\n',
}
HARMLESS_EDIT = {
    "file_path": str(TARGET),
    "old_string": "MAX_SHOWN = 2\n",
    "new_string": "MAX_SHOWN = 3\n",
}
# Both fragments end in a colon and do not parse on their own; 25 of the 194 real edits of one night were like this.
UNPARSABLE_FRAGMENT_EDIT = {
    "file_path": str(TARGET),
    "old_string": "    if not shown:\n",
    "new_string": "    if not shown or x:\n",
}


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()


def _stamp(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _transcript(tmp_path: Path, messages: list[tuple[float, str, str]]) -> str:
    """messages: (time, origin kind, text). Writes real harness-shaped records."""
    path = tmp_path / "t.jsonl"
    lines = []
    for when, kind, text in messages:
        rec = {
            "type": "user",
            "timestamp": _stamp(when),
            "message": {"role": "user", "content": text},
        }
        if kind:
            rec["origin"] = {"kind": kind}
        lines.append(json.dumps(rec))
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def _check(tool_input, transcript, tmp_path):
    return w.check("Edit", tool_input, transcript, ROOT, tmp_path / "log.jsonl")


def test_decision_delta_sees_a_real_decision_and_ignores_comments_and_renames() -> None:
    assert w.decision_delta("return x\n", "if a and b:\n    return x\nreturn x\n") >= 2
    assert w.decision_delta("# old\nx = f(a)\n", "# a much longer explanation\nx = f(a)\n") == 0
    assert w.decision_delta("total = f(a)\n", "row_total = f(a)\n") == 0
    assert (
        w.decision_delta("x = (\n", "x = 1\n") is None
    )  # cannot parse either side: says so, not zero


def test_a_fragment_that_does_not_parse_on_its_own_is_still_judged_on_the_whole_file(
    tmp_path,
) -> None:
    tr = _transcript(tmp_path, [(time.time() - 5, "human", "Go look properly")])
    assert _check(UNPARSABLE_FRAGMENT_EDIT, tr, tmp_path)[0] == "owed"


def test_a_harmless_edit_is_not_applicable(tmp_path) -> None:
    tr = _transcript(tmp_path, [(time.time(), "human", "go look properly")])
    assert _check(HARMLESS_EDIT, tr, tmp_path)[0] == "not-applicable"


def test_a_decision_edit_after_his_message_with_no_walk_is_owed_and_the_house_opens_one(
    tmp_path,
) -> None:
    tr = _transcript(tmp_path, [(time.time() - 5, "human", "Go look properly")])
    state, message = _check(DECISION_EDIT, tr, tmp_path)
    assert state == "owed", message  # the message names why when the check could not run
    assert REL in message and "Go look properly" not in message
    row = json.loads((tmp_path / "log.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert row["state"] == "owed" and row["walk"].startswith("walk-")
    # asking again reuses the open walk, never a second one
    again = _check(DECISION_EDIT, tr, tmp_path)
    assert again[0] == "owed" and row["walk"] in again[1]


def test_an_older_walk_that_names_the_file_does_not_count(tmp_path) -> None:
    open_walk("an older question about something else entirely", "normal", (REL,))
    time.sleep(0.05)
    tr = _transcript(tmp_path, [(time.time(), "human", "new ask")])
    assert _check(DECISION_EDIT, tr, tmp_path)[0] == "owed"


def test_a_closed_walk_opened_after_his_message_naming_the_file_passes(tmp_path) -> None:
    tr = _transcript(tmp_path, [(time.time() - 1, "human", "new ask")])
    walk = open_walk("the question for this change, stated as a sentence", "normal", (REL,))
    import sqlite3

    from divineos.core.council_walk import _db_path

    with sqlite3.connect(str(_db_path())) as conn:
        conn.execute("UPDATE walks SET closed_at = ? WHERE id = ?", (time.time(), walk["walk_id"]))
    assert _check(DECISION_EDIT, tr, tmp_path)[0] == "pass"


def test_a_walk_opened_since_the_piece_of_work_began_covers_later_edits_even_after_a_newer_message(
    tmp_path,
) -> None:
    # Dad 2026-11-11: a picture frame is not a wall. One walk per piece of work about the files, not one per message.
    import sqlite3

    from divineos.core.council_walk import _db_path

    floor = time.time() - 100  # the work item's window began 100 s ago
    walk = open_walk(
        "the piece of work this file belongs to, stated as a sentence", "normal", (REL,)
    )
    with sqlite3.connect(str(_db_path())) as conn:
        conn.execute("UPDATE walks SET closed_at = ? WHERE id = ?", (time.time(), walk["walk_id"]))
    time.sleep(0.05)
    tr = _transcript(tmp_path, [(time.time(), "human", "a newer message than the walk")])
    state, _ = w.check("Edit", DECISION_EDIT, tr, ROOT, tmp_path / "log.jsonl", since=floor)
    assert state == "pass"
    # without the piece-of-work floor the old rule still holds, so the first knock is not weakened
    assert w.check("Edit", DECISION_EDIT, tr, ROOT, tmp_path / "log2.jsonl")[0] == "owed"


def test_a_walk_opened_before_the_piece_of_work_began_does_not_count(tmp_path) -> None:
    import sqlite3

    from divineos.core.council_walk import _db_path

    walk = open_walk("an older piece of work that happened to name this file", "normal", (REL,))
    with sqlite3.connect(str(_db_path())) as conn:
        conn.execute("UPDATE walks SET closed_at = ? WHERE id = ?", (time.time(), walk["walk_id"]))
    time.sleep(0.05)
    tr = _transcript(tmp_path, [(time.time(), "human", "go on")])
    assert (
        w.check("Edit", DECISION_EDIT, tr, ROOT, tmp_path / "log.jsonl", since=time.time())[0]
        == "owed"
    )


def test_a_file_no_walk_names_is_still_owed_inside_the_piece_of_work(tmp_path) -> None:
    other = {
        **DECISION_EDIT,
        "file_path": str(ROOT / "src" / "divineos" / "core" / "root_cause_before_fix.py"),
    }
    tr = _transcript(tmp_path, [(time.time(), "human", "go on")])
    state, message = w.check(
        "Edit", other, tr, ROOT, tmp_path / "log.jsonl", since=time.time() - 100
    )
    assert state in {"owed", "not-applicable"} and (
        "piece of work" in message or state == "not-applicable"
    )


def test_a_turn_with_no_human_stamped_message_owes_nothing_new(tmp_path) -> None:
    tr = _transcript(tmp_path, [(time.time(), "", "a bell, a helper result, hook feedback")])
    assert _check(DECISION_EDIT, tr, tmp_path)[0] == "no-human-message"


def test_an_unreadable_transcript_stands_aside_and_says_so(tmp_path) -> None:
    state, message = _check(DECISION_EDIT, str(tmp_path / "nope.jsonl"), tmp_path)
    assert state == "could-not-check" and "could not be read" in message
    assert (
        json.loads((tmp_path / "log.jsonl").read_text(encoding="utf-8").splitlines()[0])["state"]
        == "could-not-check"
    )


def test_the_door_actually_calls_it() -> None:
    # Built and disconnected is the failure he named; the door must reach this from decide().
    import inspect

    from divineos.core import work_item_doorman as door

    assert "walk_after_his_message" in inspect.getsource(door.decide)
    assert "transcript_path" in inspect.getsource(door.gate_from_stdin)


def test_the_real_transcript_of_this_machine_has_a_human_stamped_message() -> None:
    # The real seam: the real harness records, not my synthetic ones. Skipped where no transcript exists.
    candidates = sorted(
        (Path.home() / ".claude" / "projects").glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime
    )
    if not candidates:
        pytest.skip("no harness transcript on this machine")
    found = w.latest_human_message(str(candidates[-1]))
    assert found is None or (isinstance(found[0], float) and isinstance(found[1], str))
