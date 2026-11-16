"""The caller the push gate runs has exactly three exits: 0, 1 and 2, and no other.

Exit 0: nothing unexplained was added. Exit 1: refused, message on stderr. Exit 2: the base
could not be read, which is never read as "no hooks" (walk-d63e509a117b, Lamport).
"""

import json
import subprocess
import sys
from pathlib import Path

from tests.test_hook_lock import _repo_with_base, _settings


def _run_script(repo, *args):
    root = Path(__file__).resolve().parent.parent
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "check_new_hooks.py"), *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def test_the_script_exits_0_when_nothing_unexplained_was_added():
    repo = _repo_with_base()
    assert _run_script(repo, "--base", "HEAD").returncode == 0


def test_the_script_exits_1_and_says_why_on_a_refusal():
    repo = _repo_with_base()
    (repo / ".claude" / "settings.json").write_text(
        json.dumps(_settings(Stop=["a.sh", "new.sh"])), encoding="utf-8"
    )
    result = _run_script(repo, "--base", "HEAD")
    assert result.returncode == 1
    assert "new.sh" in result.stderr


def test_the_script_exits_2_when_the_base_cannot_be_read():
    repo = _repo_with_base()
    result = _run_script(repo, "--base", "no-such-ref")
    assert result.returncode == 2
    assert "COULD NOT CHECK" in result.stderr
