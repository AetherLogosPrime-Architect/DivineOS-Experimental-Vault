"""A remote branch delete needs a tag on the remote at the branch tip. Real git, a real bare remote, no stubs."""

from __future__ import annotations

import subprocess
from pathlib import Path

from divineos.core import deletion_discipline as dd

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        [*GIT, *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _repo_with_remote(tmp_path: Path) -> tuple[Path, str]:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    work.mkdir()
    _git(work, "init")
    _git(work, "remote", "add", "origin", str(remote))
    (work / "a.txt").write_text("one", encoding="utf-8")
    _git(work, "add", ".")
    _git(work, "commit", "-m", "first")
    _git(work, "checkout", "-b", "old-branch")
    _git(work, "push", "origin", "old-branch")
    return work, _git(work, "rev-parse", "HEAD")


def test_not_a_remote_delete_is_silent(tmp_path: Path) -> None:
    work, _ = _repo_with_remote(tmp_path)
    assert dd.archive_tag_problem("git status", cwd=str(work)) is None
    assert dd.archive_tag_problem("git branch -D old-branch", cwd=str(work)) is None


def test_no_tag_on_the_remote_refuses_and_names_the_tip(tmp_path: Path) -> None:
    work, tip = _repo_with_remote(tmp_path)
    problem = dd.archive_tag_problem("git push origin --delete old-branch", cwd=str(work))
    assert problem and tip[:10] in problem and "old-branch" in problem


def test_a_local_only_tag_does_not_count(tmp_path: Path) -> None:
    work, _ = _repo_with_remote(tmp_path)
    _git(work, "tag", "archive/old-branch")  # exists locally, never pushed
    assert dd.archive_tag_problem("git push origin --delete old-branch", cwd=str(work))


def test_tag_pushed_to_the_remote_passes(tmp_path: Path) -> None:
    work, _ = _repo_with_remote(tmp_path)
    _git(work, "tag", "archive/old-branch")
    _git(work, "push", "origin", "archive/old-branch")
    assert dd.archive_tag_problem("git push origin --delete old-branch", cwd=str(work)) is None
    assert dd.archive_tag_problem("git push origin :old-branch", cwd=str(work)) is None


def test_annotated_tag_counts_by_its_peeled_commit(tmp_path: Path) -> None:
    work, _ = _repo_with_remote(tmp_path)
    _git(work, "tag", "-a", "archive/old-branch", "-m", "keep")
    _git(work, "push", "origin", "archive/old-branch")
    assert dd.archive_tag_problem("git push origin --delete old-branch", cwd=str(work)) is None


def test_could_not_ask_the_remote_refuses_and_says_so(tmp_path: Path) -> None:
    work, _ = _repo_with_remote(tmp_path)
    problem = dd.archive_tag_problem("git push nowhere --delete old-branch", cwd=str(work))
    assert problem and "could not ask the remote" in problem


def test_the_gate_actually_calls_it() -> None:
    # The door must reach the new check from block_reason, or this is built and disconnected.
    import inspect

    assert "archive_tag_problem" in inspect.getsource(dd.block_reason)
