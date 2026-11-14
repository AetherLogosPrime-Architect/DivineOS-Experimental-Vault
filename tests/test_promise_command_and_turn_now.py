"""`divineos promise list|close` is a thin door over promise_markers, and the recorder keeps the turn "now".

Dad, 2026-11-13: record the promise, wait about five turns, then remind and hold until I close it. A close has
to be one line and cheap, or it will be skipped. Walk walk-60198f385a28 (nine lenses) fixed what this pins:
- registration is proven through the real click group, not by calling the function (Breaker);
- every refusal prints the corrected command, filled in, so a refused close costs one more line (Norman);
- waiting-on stamps turn_now PLUS ONE, since turn_now was counted at the end of the last turn and the command
  runs in the middle of the next (Einstein);
- turn_now is written at every Stop, even when no promise was found (Dillahunty);
- the command holds no rule of its own: it imports neither json nor time (Dijkstra);
- there is no bulk path: no close-all, no wildcard (Schneier).
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from divineos.core import promise_markers as pm

REPO = Path(__file__).resolve().parents[1]


def _cli():
    from divineos.cli import cli

    return cli


def _marker(folder: Path, name: str, text: str, turn: int | None = 1) -> Path:
    data: dict = {
        "shape": "explicit_future",
        "promise_text": text,
        "trigger_phrase": text,
        "detected_at_ts": time.time() - 60,
    }
    if turn is not None:
        data["turn_index"] = turn
    path = folder / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _run(folder: Path, *args: str):
    return CliRunner().invoke(
        _cli(), ["promise", *args, "--folder", str(folder)], catch_exceptions=False
    )


# ---- registration is proven through the real group ------------------------------------------------


def test_the_promise_group_is_registered_in_the_real_cli():
    assert "promise" in _cli().commands, "divineos promise is not registered in cli/__init__.py"


# ---- list ---------------------------------------------------------------------------------------


def test_list_shows_each_open_marker_with_its_age_in_turns(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=10)
    (tmp_path / "turn_now.json").write_text(
        json.dumps({"global": 13, "session": "s", "session_turns": 13, "at": time.time()}),
        encoding="utf-8",
    )
    out = _run(tmp_path, "list").output
    assert "promise_a" in out and "write the draft" in out
    assert "3 turn" in out, "the age must be said in turns"


def test_list_says_when_a_marker_is_unreadable_and_never_calls_it_clean(tmp_path):
    (tmp_path / "promise_bad.json").write_text("{not json", encoding="utf-8")
    out = _run(tmp_path, "list").output
    assert "promise_bad.json" in out and "could not" in out.lower()


def test_list_on_a_clean_empty_folder_says_nothing_is_open(tmp_path):
    """Control: empty is found-nothing and must not read as could-not-look."""
    out = _run(tmp_path, "list").output
    assert "nothing open" in out.lower()
    assert "could not" not in out.lower()


# ---- close, one line each ---------------------------------------------------------------------------


def test_close_false_alarm_closes_it_and_list_no_longer_shows_it(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will keep trying")
    result = _run(
        tmp_path,
        "close",
        "promise_a",
        "--false-alarm",
        "a stance about conduct, nothing a tool could do",
    )
    assert result.exit_code == 0, result.output
    assert pm.read_folder(tmp_path).open == []


def test_close_done_with_a_fresh_file(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft")
    deed = tmp_path / "draft.md"
    deed.write_text("the deed", encoding="utf-8")
    assert _run(tmp_path, "close", "promise_a", "--done", str(deed)).exit_code == 0
    assert pm.read_folder(tmp_path).open == []


def _clock(folder: Path, now: int) -> None:
    (folder / "turn_now.json").write_text(
        json.dumps({"global": now, "session": "s", "session_turns": now, "at": time.time()}),
        encoding="utf-8",
    )


def _closes(folder: Path) -> list[dict]:
    lines = (folder / "closes.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


@pytest.mark.parametrize("kind", ["done", "false-alarm"])
def test_every_close_stamps_the_turn_it_was_made_in_and_says_so(tmp_path, kind):
    """The close log could not answer 'how long had it waited' because only waiting-on carried a turn."""
    from divineos.core.promise_reminder import close_ages

    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=10)
    _clock(tmp_path, 20)
    deed = tmp_path / "draft.md"
    deed.write_text("the deed", encoding="utf-8")
    detail = str(deed) if kind == "done" else "a stance about conduct, nothing a tool could do"
    result = _run(tmp_path, "close", "promise_a", f"--{kind}", detail)
    assert result.exit_code == 0 and "turn 21" in result.output
    assert _closes(tmp_path)[-1]["turn"] == 21
    assert close_ages(tmp_path) == [11]


def test_a_close_with_no_clock_still_closes_and_says_it_has_no_turn(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will keep trying")
    result = _run(
        tmp_path,
        "close",
        "promise_a",
        "--false-alarm",
        "a stance about conduct, nothing a tool could do",
    )
    assert result.exit_code == 0 and "no turn could be stamped" in result.output
    assert _closes(tmp_path)[-1]["turn"] is None


def test_two_closes_in_one_turn_carry_the_same_stamp(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will write the draft", turn=10)
    _marker(tmp_path, "promise_b.json", "I will read the letter", turn=11)
    _clock(tmp_path, 20)
    reason = "a stance about conduct, nothing a tool could do"
    _run(tmp_path, "close", "promise_a", "--false-alarm", reason)
    _run(tmp_path, "close", "promise_b", "--false-alarm", reason)
    assert [row["turn"] for row in _closes(tmp_path)] == [21, 21]


def test_a_promise_bounced_through_waiting_on_is_aged_from_its_last_re_date(tmp_path):
    """The stamp does not claim the whole wait: after waiting-on the age counts from the re-date."""
    from divineos.core.promise_reminder import close_ages

    _marker(tmp_path, "promise_a.json", "I will send it after he says go", turn=2)
    _clock(tmp_path, 20)
    _run(tmp_path, "close", "promise_a", "--waiting-on", "Dad")
    _clock(tmp_path, 30)
    _run(tmp_path, "close", "promise_a", "--false-alarm", "he never said go and I will not send it")
    assert close_ages(tmp_path) == [10]


def test_waiting_on_stamps_the_turn_now_plus_one(tmp_path):
    """turn_now was counted at the end of the last turn; this runs in the middle of the next (Einstein)."""
    _marker(tmp_path, "promise_a.json", "I will send it after he says go", turn=2)
    (tmp_path / "turn_now.json").write_text(
        json.dumps({"global": 20, "session": "s", "session_turns": 20, "at": time.time()}),
        encoding="utf-8",
    )
    assert _run(tmp_path, "close", "promise_a", "--waiting-on", "Dad").exit_code == 0
    state = pm.read_folder(tmp_path)
    assert state.open[0].turn == 21
    assert pm.due(state.open, current_turn=25) == []
    assert [m.name for m in pm.due(state.open, current_turn=26)] == ["promise_a.json"]


def test_waiting_on_with_no_turn_now_refuses_and_says_why(tmp_path):
    _marker(tmp_path, "promise_a.json", "I will send it after he says go", turn=2)
    result = _run(tmp_path, "close", "promise_a", "--waiting-on", "Dad")
    assert result.exit_code != 0
    assert "turn_now" in result.output


# ---- refusals carry the corrected command ---------------------------------------------------------


@pytest.mark.parametrize(
    "args",
    [
        ("close", "promise_a", "--false-alarm", "nope"),
        ("close", "promise_a", "--done", "does/not/exist.md"),
        ("close", "promise_zzz", "--false-alarm", "a reason that is long enough to count"),
        ("close", "promise_a"),
    ],
)
def test_every_refusal_prints_the_corrected_command(tmp_path, args):
    _marker(tmp_path, "promise_a.json", "I will keep trying")
    result = _run(tmp_path, *args)
    assert result.exit_code != 0
    assert "divineos promise close" in result.output, "a refusal must say what to type next"


# ---- no bulk path ------------------------------------------------------------------------------------


@pytest.mark.parametrize("flag", ["--all", "--older-than", "--everything"])
def test_there_is_no_bulk_close(tmp_path, flag):
    _marker(tmp_path, "promise_a.json", "one")
    result = CliRunner().invoke(
        _cli(), ["promise", "close", "promise_a", flag, "--folder", str(tmp_path)]
    )
    assert result.exit_code == 2, "an unknown option must be refused, never quietly accepted"
    # Not "no such command": that would pass while the whole group is missing (it did, before it existed).
    assert "no such option" in result.output.lower()


# ---- the command holds no rule of its own --------------------------------------------------------


def test_the_command_file_imports_neither_json_nor_time():
    tree = ast.parse(
        (REPO / "src" / "divineos" / "cli" / "promise_commands.py").read_text(encoding="utf-8")
    )
    imported = {
        n.names[0].name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import)
    } | {
        n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module
    }
    assert not ({"json", "time"} & imported), "a rule belongs in promise_markers, not in the door"


# ---- the recorder keeps turn_now at EVERY Stop, even with no promise ------------------------------------


def test_the_recorder_writes_turn_now_even_when_it_finds_no_promise(tmp_path):
    hook = REPO / ".claude" / "hooks" / "promise-reach-detector.sh"
    bash = next(
        (
            c
            for c in (r"C:\Program Files\Git\bin\bash.exe", "/usr/bin/bash")
            if Path(c).exists() and "System32" not in c
        ),
        None,
    )
    if bash is None or not hook.exists():
        pytest.skip("no POSIX bash here: could-not-look, which is not a pass")
    home = tmp_path / "home"
    (home / ".divineos-aria").mkdir(parents=True)
    lines = [
        json.dumps(
            {"type": "user", "turnOrigin": "human", "message": {"role": "user", "content": "x"}}
        ),
        json.dumps(
            {"type": "user", "turnOrigin": "scheduled", "message": {"role": "user", "content": "x"}}
        ),
        json.dumps(
            {"type": "user", "turnOrigin": "human", "message": {"role": "user", "content": "x"}}
        ),
        json.dumps(
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "The tests pass."}],
                },
            }
        ),
    ]
    transcript = tmp_path / "s.jsonl"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("HOME", "USERPROFILE")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    subprocess.run(
        [bash, str(hook)],
        input=json.dumps({"transcript_path": str(transcript)}).encode(),
        capture_output=True,
        env=env,
        cwd=REPO,
        timeout=120,
        check=False,
    )
    folder = home / ".divineos-aria" / "promise_markers"
    assert pm.turn_now(folder) == 3, (
        "turn_now must be written at every Stop, found a promise or not"
    )
    assert pm.read_folder(folder).open == [], "control: no promise was in the reply, so no marker"
