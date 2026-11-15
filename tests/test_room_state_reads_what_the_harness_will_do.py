"""The room watchman reads the timeout the harness will enforce, and prints a remedy that restores a wired room.

2026-11-15, from the second reader's note 783 on PR 768 and Aether's measurements (draft:
docs/drafts/the_room_watchman_reads_the_timeout_the_checkout_and_a_safe_remedy_draft_2026-11-15.md, walk-2fe11221e54b).

  * a room entry whose settings timeout is 1 second is cut off by the harness while the watchman called it wired;
  * the remedy it printed restored from origin/main, which restores the unplugged file if main carries it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from divineos.core import room_state

ROOM = room_state.ROOM_FILE


def _repo(tmp_path: Path, timeout: int | None) -> Path:
    claude = tmp_path / ".claude"
    (claude / "hooks").mkdir(parents=True)
    (claude / "hooks" / ROOM).write_text("print('room')\n", encoding="utf-8")
    entry: dict = {"type": "command", "command": f"true # {ROOM}"}
    if timeout is not None:
        entry["timeout"] = timeout
    settings = {"hooks": {"Stop": [{"hooks": [entry]}]}}
    (claude / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    return tmp_path


def _git_bash() -> str:
    """The bash that ships with git. On Windows a bare `bash` can be the WSL launcher, which reads this command
    differently (the same reason test_the_wrapper_never_passes_silently_... fails on this machine)."""
    try:
        exec_path = (
            subprocess.run(["git", "--exec-path"], capture_output=True, check=True, timeout=30)
            .stdout.decode("utf-8", "replace")
            .strip()
        )
    except (OSError, subprocess.SubprocessError):
        return "bash"
    for parent in Path(exec_path).parents:
        candidate = parent / "bin" / "bash.exe"
        if candidate.is_file():
            return str(candidate)
    return "bash"


def test_a_room_entry_with_a_one_second_timeout_is_not_standing(tmp_path):
    state = room_state.check(_repo(tmp_path, timeout=1))
    assert not state.standing
    assert any("timeout" in p.lower() and "1" in p for p in state.problems)


def test_a_room_entry_with_a_fifteen_second_timeout_raises_no_timeout_problem(tmp_path):
    """The control: the instrument says no as well as yes."""
    state = room_state.check(_repo(tmp_path, timeout=15))
    assert not any("timeout" in p.lower() for p in state.problems)


def test_a_room_entry_with_no_timeout_raises_no_timeout_problem(tmp_path):
    """No value means the harness's own default applies, which this check does not second-guess."""
    state = room_state.check(_repo(tmp_path, timeout=None))
    assert not any("timeout" in p.lower() for p in state.problems)


def test_the_remedy_does_not_restore_from_origin_main():
    assert "origin/main" not in room_state.RESTORE


@pytest.mark.skipif(
    shutil.which("git") is None or shutil.which("bash") is None, reason="needs git and bash"
)
def test_the_remedy_restores_a_wired_room_from_history_even_when_the_newest_commit_unplugs_it(
    tmp_path,
):
    """Run the printed remedy for real: a repository whose latest commit removed the room, and an earlier one that had it."""

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    _repo(tmp_path, timeout=15)
    git("add", ".")
    git("commit", "-q", "-m", "room wired")
    (tmp_path / ".claude" / "settings.json").write_text(
        json.dumps({"hooks": {"Stop": []}}), encoding="utf-8"
    )
    (tmp_path / ".claude" / "hooks" / ROOM).write_text("# gutted\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "room unplugged")

    done = subprocess.run(
        [_git_bash(), "-c", room_state.RESTORE], cwd=str(tmp_path), capture_output=True, timeout=60
    )
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    assert ROOM in (tmp_path / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert "gutted" not in (tmp_path / ".claude" / "hooks" / ROOM).read_text(encoding="utf-8")
