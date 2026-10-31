"""The checkpoint's commit step must not report success when it saved nothing.

Found 2026-10-28: a staged file made auto_commit_substrate step aside, and the
step still reported succeeded=True with the reason dropped, 218 files unsaved.
"""

import subprocess
from pathlib import Path

import pytest

from divineos.core import auto_cycle


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "a.txt").write_text("one")
    _git(tmp_path, "add", "a.txt")
    _git(tmp_path, "commit", "-q", "-m", "first")
    monkeypatch.setattr(auto_cycle, "Path", lambda _f: tmp_path / "x" / "y" / "z" / "w")
    return tmp_path


def test_staged_index_makes_the_step_fail_loudly(repo):
    (repo / "b.txt").write_text("two")
    _git(repo, "add", "b.txt")
    with pytest.raises(RuntimeError, match="staged index"):
        auto_cycle._step_commit("test")
