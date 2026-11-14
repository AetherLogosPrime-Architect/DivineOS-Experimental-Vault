"""One file per hold: no row is lost or torn when hooks end a reply together (walk-b95759224dae).

Aether measured the failure: two processes appending to one file with the same open-and-write that `record` uses
lose about 4% of 8,000 rows and tear about 3%. WHAT THIS DOES NOT COVER: two processes writing the SAME hold name
(the closed list and the one-writer-per-name scan are what keep that from being written), and the harness
ordering of hooks.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from divineos.core import hold_log

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _home(tmp_path, monkeypatch):
    monkeypatch.setattr(hold_log, "_log_path", lambda: tmp_path / "hold_log.jsonl")


def _write(path: Path, *rows: dict) -> None:
    path.write_text("".join(json.dumps(r) + chr(10) for r in rows), encoding="utf-8")


def test_each_hold_writes_only_its_own_file(tmp_path):
    hold_log.record("room", "stopped", "a")
    hold_log.record("follow_through", "passed", "b")
    assert (tmp_path / "hold_log_room.jsonl").is_file()
    assert (tmp_path / "hold_log_follow_through.jsonl").is_file()
    assert not (tmp_path / "hold_log.jsonl").exists()


@pytest.mark.parametrize(
    "name", ["made_up", "../escape", "", "Room", "room/x", None, 5, ["x"], "x" * 500]
)
def test_a_name_off_the_list_never_raises_and_lands_in_the_one_fixed_file(tmp_path, capsys, name):
    """walk-57dcc761cdbd: a new hold added in a hurry must not crash a Stop hook; it is a defect, said loudly."""
    written = hold_log.record(name, "stopped", "a")
    assert written == tmp_path / "hold_log_unlisted.jsonl"
    assert sorted(p.name for p in tmp_path.glob("hold_log*")) == ["hold_log_unlisted.jsonl"]
    err = capsys.readouterr().err
    assert err.startswith("DEFECT") and "hold_log" in err
    row = hold_log.read_all()[0]
    assert row["hold"] == "unlisted" and row["outcome"] == "stopped"
    assert len(row["offered"]) <= 83  # the repr of the name, cut to 80 plus quotes


def test_record_returns_the_path_it_wrote_and_none_when_it_could_not(tmp_path, capsys):
    assert hold_log.record("room", "stopped", "a") == tmp_path / "hold_log_room.jsonl"
    (
        tmp_path / "hold_log_voice.jsonl"
    ).mkdir()  # a folder where the file should be: the write fails
    assert hold_log.record("voice", "lifted", "a") is None
    assert "could not write" in capsys.readouterr().err


def test_a_failing_write_of_an_unlisted_row_does_not_raise_either(tmp_path, capsys):
    (tmp_path / "hold_log_unlisted.jsonl").mkdir()
    assert hold_log.record("made_up", "stopped", "a") is None
    assert "could not write" in capsys.readouterr().err


@pytest.mark.parametrize("text", [None, 5, ["a"], b"bytes"])
def test_record_never_raises_whatever_the_text_or_outcome_is(tmp_path, text):
    hold_log.record("room", text, text)
    assert hold_log.read_all()[0]["hold"] == "room"


def test_the_real_record_in_a_separate_process_survives_an_unlisted_name(tmp_path):
    home = tmp_path / "real_home"
    home.mkdir()
    code = "from divineos.core import hold_log; hold_log.record('a_new_hold', 'stopped', 'x')"
    done = subprocess.run(
        [sys.executable, "-c", code],
        env={**os.environ, "DIVINEOS_HOME": str(home)},
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert done.returncode == 0
    assert "DEFECT" in done.stderr and "a_new_hold" in done.stderr
    assert (home / "hold_log_unlisted.jsonl").is_file()


def test_every_hold_name_in_the_source_is_on_the_list_and_has_one_writing_file():
    """Wayne: the invariant holds only while each name has one writer. A name called from two files fails here."""
    pattern = re.compile(r"(?:record|_log_stand_down)\(\s*[\"'](\w+)[\"']")
    files_by_name: dict[str, set[str]] = {}
    roots = [ROOT / ".claude" / "hooks", ROOT / "src" / "divineos"]
    for base in roots:
        for path in list(base.rglob("*.py")):
            if path.name == "hold_log.py":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "hold_log" not in text:
                continue
            for name in pattern.findall(text):
                files_by_name.setdefault(name, set()).add(path.name)
    assert files_by_name, "the scan found no record calls, so it proves nothing"
    for name, files in files_by_name.items():
        assert name in hold_log.HOLDS, f"{name} is written but not on the closed list"
        assert len(files) == 1, f"{name} is written from more than one file: {sorted(files)}"


def test_read_all_merges_files_in_time_order_with_a_fixed_tie_break(tmp_path):
    _write(
        tmp_path / "hold_log_room.jsonl",
        {"at": "x", "t": 10.0, "hold": "room", "outcome": "first", "first_words": ""},
        {"at": "x", "t": 30.0, "hold": "room", "outcome": "third", "first_words": ""},
        {"at": "x", "t": 40.0, "hold": "room", "outcome": "tie_room", "first_words": ""},
    )
    _write(
        tmp_path / "hold_log_follow_through.jsonl",
        {"at": "x", "t": 20.0, "hold": "follow_through", "outcome": "second", "first_words": ""},
        {"at": "x", "t": 40.0, "hold": "follow_through", "outcome": "tie_ft", "first_words": ""},
    )
    assert [r["outcome"] for r in hold_log.read_all()] == [
        "first",
        "second",
        "third",
        "tie_ft",
        "tie_room",
    ]


def test_rows_of_one_hold_with_equal_times_keep_their_file_order(tmp_path):
    """The last row decides, and the Windows clock is coarse, so equal times must not reorder a hold's own rows."""
    _write(
        tmp_path / "hold_log_follow_through.jsonl",
        {"at": "x", "t": 5.0, "hold": "follow_through", "outcome": "stopped", "first_words": ""},
        {"at": "x", "t": 5.0, "hold": "follow_through", "outcome": "deferred", "first_words": ""},
    )
    assert [r["outcome"] for r in hold_log.read_all("follow_through")] == ["stopped", "deferred"]


def test_the_old_single_file_is_still_read_and_placed_by_its_time(tmp_path):
    _write(
        tmp_path / "hold_log.jsonl",
        {"at": "2026-11-13T01:00:00Z", "hold": "room", "outcome": "old", "first_words": ""},
    )
    hold_log.record("room", "stopped", "new")
    assert [r["outcome"] for r in hold_log.read_all()] == ["old", "stopped"]


def test_read_all_for_one_hold_returns_only_that_hold_including_its_old_rows(tmp_path):
    _write(
        tmp_path / "hold_log.jsonl",
        {"at": "2026-11-13T01:00:00Z", "hold": "room", "outcome": "old_room", "first_words": ""},
        {"at": "2026-11-13T01:00:01Z", "hold": "voice", "outcome": "old_voice", "first_words": ""},
    )
    hold_log.record("room", "stopped", "x")
    hold_log.record("voice", "lifted", "y")
    assert [r["outcome"] for r in hold_log.read_all("room")] == ["old_room", "stopped"]


def test_corrupt_lines_are_skipped_and_counted_never_fatal(tmp_path):
    path = tmp_path / "hold_log_room.jsonl"
    good = json.dumps({"at": "x", "t": 1.0, "hold": "room", "outcome": "ok", "first_words": ""})
    path.write_text(
        'igned."}' + chr(10) + good + chr(10) + "{ not json" + chr(10), encoding="utf-8"
    )
    assert [r["outcome"] for r in hold_log.read_all()] == ["ok"]
    assert hold_log.last_skipped == 2


def test_corrupt_lines_in_the_old_shared_file_are_counted_apart_from_the_new_files(tmp_path):
    """The known history is neither hidden nor a standing alarm; a bad line in a single-writer file is the alarm."""
    good = json.dumps(
        {"at": "2026-11-13T01:00:00Z", "hold": "room", "outcome": "old", "first_words": ""}
    )
    (tmp_path / "hold_log.jsonl").write_text(
        'igned."}' + chr(10) + good + chr(10), encoding="utf-8"
    )
    hold_log.record("room", "stopped", "new")
    assert [r["outcome"] for r in hold_log.read_all()] == ["old", "stopped"]
    assert hold_log.last_skipped == 0 and hold_log.last_skipped_legacy == 1


def test_a_clean_read_says_zero_skipped(tmp_path):
    hold_log.record("room", "stopped", "a")
    hold_log.read_all()
    assert hold_log.last_skipped == 0


def test_nothing_written_is_empty_but_an_unreadable_file_raises(tmp_path):
    assert hold_log.read_all() == []
    (tmp_path / "hold_log_room.jsonl").mkdir()
    with pytest.raises(OSError):
        hold_log.read_all()


def _writer(home: Path, hold: str, count: int) -> subprocess.Popen:
    code = (
        "from divineos.core import hold_log\n"
        f"for i in range({count}):\n"
        f"    hold_log.record({hold!r}, 'stopped', 'row ' + str(i))\n"
    )
    env = {**os.environ, "DIVINEOS_HOME": str(home)}
    return subprocess.Popen([sys.executable, "-c", code], env=env, cwd=str(ROOT))


@pytest.mark.parametrize("holds", [("room", "follow_through"), ("room", "follow_through", "voice")])
def test_concurrent_writers_on_different_holds_lose_and_tear_nothing(tmp_path, holds):
    """The race Aether measured, through the real record in separate processes, with the home set by environment."""
    home = tmp_path / "real_home"
    home.mkdir()
    count = 1500
    procs = [_writer(home, hold, count) for hold in holds]
    assert all(p.wait(timeout=300) == 0 for p in procs)
    total = torn = 0
    for hold in holds:
        for line in (home / f"hold_log_{hold}.jsonl").read_text(encoding="utf-8").splitlines():
            total += 1
            try:
                json.loads(line)
            except ValueError:
                torn += 1
    assert (total, torn) == (count * len(holds), 0)
