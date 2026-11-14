"""The promise recorder writes a marker where it says it does, on this machine.

Dad, 2026-11-13: *"it should just record your promise to do something, give you a chance to do it, and if
after 5 or so turns you havent done anything about it ... it reminds you and blocks you"*. The record half
already existed (`.claude/hooks/promise-reach-detector.sh`) and was found, 2026-11-13, to have written nothing
for months: the hook hands its marker folder to Python in a POSIX spelling (`/c/Users/...`), Windows Python
reads that as `C:\\c\\Users\\...`, the write fails, and the loop's `except OSError: continue` hides it. The
folder had been empty since 2026-07-18. This runs the real hook on a transcript with a promise in it and
asks the one question that matters: is there a marker file afterwards, in the folder the hook is told to use.

The control beside it: a transcript with no promise must leave the folder empty, so a pass is not "it writes
a file for anything".
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / ".claude" / "hooks" / "promise-reach-detector.sh"


def _bash() -> str | None:
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        "/usr/bin/bash",
        shutil.which("bash") or "",
    ):
        if candidate and Path(candidate).exists() and "System32" not in candidate:
            return candidate
    return None


BASH = _bash()
pytestmark = pytest.mark.skipif(
    not HOOK.exists() or BASH is None,
    reason="hook or a POSIX bash absent here -- could-not-look, which is not a pass",
)


def _run(tmp_path: Path, reply: str) -> list[Path]:
    home = tmp_path / "home"
    (home / ".divineos-aria").mkdir(parents=True)
    transcript = tmp_path / "session.jsonl"
    row = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": reply}]},
    }
    transcript.write_text(json.dumps(row) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("HOME", "USERPROFILE")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    # The seat's own data home is named by the house's resolver; a test redirects it explicitly, since this
    # checkout's own marker would otherwise point at the REAL home (walk-eb4440341013).
    env["DIVINEOS_HOME"] = str(home / ".divineos-aria")
    done = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"transcript_path": str(transcript)}).encode(),
        capture_output=True,
        env=env,
        cwd=REPO,
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    folder = home / ".divineos-aria" / "promise_markers"
    return sorted(folder.glob("promise_*.json")) if folder.is_dir() else []


def test_a_promise_in_the_reply_leaves_a_marker(tmp_path):
    markers = _run(tmp_path, "Done. I will write the draft after the walk.")
    assert markers, "the recorder wrote nothing: a promise must leave a marker file in the folder"
    data = json.loads(markers[0].read_text(encoding="utf-8"))
    assert "write the draft" in data["promise_text"]


def test_a_reply_with_no_promise_leaves_no_marker(tmp_path):
    """Control: the recorder must not write a file for anything."""
    assert _run(tmp_path, "The sleep fix is in and its tests pass.") == []


def _run_with_transcript_lines(tmp_path: Path, lines: list[str]) -> Path:
    """Run the hook on raw transcript lines; return the home folder so the mark file can be read."""
    home = tmp_path / "home"
    (home / ".divineos-aria").mkdir(parents=True)
    transcript = tmp_path / "session.jsonl"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("HOME", "USERPROFILE")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["DIVINEOS_HOME"] = str(home / ".divineos-aria")
    done = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"transcript_path": str(transcript)}).encode(),
        capture_output=True,
        env=env,
        cwd=REPO,
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    return home


def test_a_failure_inside_the_recorder_is_kept_not_thrown_away(tmp_path):
    """It used to send its own error output to /dev/null. A transcript line that is not JSON is skipped,
    and the skip must now leave a mark saying so."""
    good = json.dumps(
        {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": "ok."}]},
        }
    )
    home = _run_with_transcript_lines(tmp_path, ["this line is not json", good])
    mark = home / ".divineos" / "promise_recorder_broke.txt"
    assert mark.is_file(), "the recorder skipped a bad line and said nothing"
    assert "not readable JSON" in mark.read_text(encoding="utf-8")


def test_a_clean_run_leaves_no_failure_mark(tmp_path):
    """Control: a clean transcript must not leave a failure mark, or the mark means nothing."""
    good = json.dumps(
        {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": "ok."}]},
        }
    )
    home = _run_with_transcript_lines(tmp_path, [good])
    assert not (home / ".divineos" / "promise_recorder_broke.txt").exists()


def _user(origin: str) -> str:
    return json.dumps(
        {"type": "user", "turnOrigin": origin, "message": {"role": "user", "content": "x"}}
    )


def _promise_reply(text: str = "Done. I will write the draft after the walk.") -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
        }
    )


def _markers(home: Path):
    from divineos.core import promise_markers as pm

    return pm.read_folder(home / ".divineos-aria" / "promise_markers")


def test_the_marker_carries_the_turn_it_was_made_in_read_from_a_real_transcript(tmp_path):
    """End to end (Polya, walk-82220bd46c30): the module's own tests seed turn numbers by hand. Here the recorder
    reads a transcript with three turn starts in it and the marker it writes must say turn 3, and the module
    must read that same marker back as five turn starts old after five more."""
    from divineos.core import promise_markers as pm

    home = _run_with_transcript_lines(
        tmp_path, [_user("human"), _user("scheduled"), _user("human"), _promise_reply()]
    )
    state = _markers(home)
    assert len(state.open) == 1, "the recorder should have written exactly one marker"
    assert state.open[0].turn == 3, "the marker must carry the turn it was made in"
    assert state.undated == []
    assert pm.due(state.open, current_turn=8) == [state.open[0]]
    assert pm.due(state.open, current_turn=7) == []


def test_a_marker_made_in_turn_zero_is_dated_not_undated(tmp_path):
    """Turn 0 is a real turn and an undated marker is a different thing; 'if turn:' would make them the same
    (Turing, walk-40224f6d552c)."""
    home = _run_with_transcript_lines(tmp_path, [_promise_reply()])
    state = _markers(home)
    assert len(state.open) == 1
    assert state.open[0].turn == 0
    assert state.undated == []


def test_a_repeated_promise_after_a_close_is_recorded_again_not_dropped(tmp_path):
    """The marker is named by a hash of the promise's words and a write is skipped when the file exists, so a
    closed marker used to swallow the same promise made later (Breaker, walk-40224f6d552c)."""
    from divineos.core import promise_markers as pm

    home = _run_with_transcript_lines(tmp_path, [_user("human"), _promise_reply()])
    folder = home / ".divineos-aria" / "promise_markers"
    first = _markers(home).open[0]
    pm.close(
        folder,
        first.name.removesuffix(".json"),
        "false-alarm",
        "a figure of speech, not a step to take",
    )
    assert _markers(home).open == []
    # the same words again, in a later turn, in the same home
    transcript = tmp_path / "later.jsonl"
    transcript.write_text(
        "\n".join([_user("human"), _user("human"), _promise_reply()]) + "\n", encoding="utf-8"
    )
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("HOME", "USERPROFILE")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["DIVINEOS_HOME"] = str(home / ".divineos-aria")
    subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"transcript_path": str(transcript)}).encode(),
        capture_output=True,
        env=env,
        cwd=REPO,
        timeout=120,
        check=False,
    )
    state = _markers(home)
    assert len(state.open) == 1, "the repeated promise must be recorded as a new open marker"
    # the first session had one turn start and this one has two: ONE running count across sessions, so 1 + 2
    assert state.open[0].turn == 3


def test_a_marker_made_from_a_transcript_with_unreadable_lines_says_its_turn_is_uncertain(tmp_path):
    """Skipped lines can make the count too low, so the marker would look younger than it is
    (Hoare, walk-40224f6d552c): it carries the number of lines skipped, and the module lists it as uncertain."""
    home = _run_with_transcript_lines(
        tmp_path, [_user("human"), "this line is not json", _user("human"), _promise_reply()]
    )
    state = _markers(home)
    assert len(state.open) == 1
    assert state.open[0].data.get("turn_uncertain") == 1
