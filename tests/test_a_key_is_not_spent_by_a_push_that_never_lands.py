"""A key is not spent by a push that never lands. See core/bypass_key.py.

Dad, 2026-11-15: *"a failed bypass should never waste your key"*. The gate spends the key at CHECK time,
before the push runs, so a push that then fails for another reason (a remote that did not exist yet, a
second check inside git's pre-push hook) cost the key twice in one afternoon. The refund asks the remote
itself whether what was pushed landed, never the exit code (correction #227: a trailing echo's zero was
read as git's), and refunds only on a clear "no" for EVERY named ref. Everything else stays spent: could
not tell must never mint a key (walk-5195f6e0680e).

These run on real git repositories, a real bare repo as the remote. The severe cases come first: a push
that LANDED must keep the key spent, and so must every case where the answer is not clear.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from divineos.core import bypass_key as bk

GATE = "check-branch-on-push"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


def _pin_this_ledger(monkeypatch) -> None:
    import sqlite3

    from divineos.core._ledger_base import _get_db_path
    from divineos.core.ledger import log_event

    log_event("USER_INPUT", "user", {"content": "genesis for this test"}, validate=False)
    with sqlite3.connect(str(_get_db_path())) as conn:
        first = conn.execute(
            "SELECT chain_hash FROM system_events ORDER BY rowid LIMIT 1"
        ).fetchone()
    monkeypatch.setattr(bk, "GENESIS_BY_SEAT", {"this-test-seat": first[0]})


@pytest.fixture
def world(tmp_path: Path, monkeypatch) -> dict:
    """A work repo with one commit and a real bare repo as its remote `origin`."""
    _pin_this_ledger(monkeypatch)
    bare = tmp_path / "remote.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    subprocess.run(["git", "init", "-q", str(work)], check=True)
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    (work / "a.txt").write_text("one", encoding="utf-8")
    _git(work, "add", "a.txt")
    _git(work, "commit", "-q", "-m", "one")
    _git(work, "remote", "add", "origin", str(bare))
    return {"work": work, "bare": bare, "sha": _git(work, "rev-parse", "HEAD")}


def _spend(command: str, at: float = 100.0) -> None:
    bk.spend(GATE, command[command.find("git push") :], now=at)
    assert not bk.status().held


def test_a_push_that_did_not_land_gives_the_key_back(world) -> None:
    """The refused push: the remote never received the branch."""
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)  # the gate spent it; then something stopped the push
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "refunded", result
    assert bk.status().held, "the key is back"
    assert bk.status().last_reissue.get("refund"), "and the record says it was a refund"


def test_a_push_that_landed_keeps_the_key_spent(world) -> None:
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    _git(world["work"], "push", "-q", "origin", "HEAD:refs/heads/backup/x")
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0) == "landed"
    assert not bk.status().held


def test_a_refund_happens_at_most_once_per_spend(world) -> None:
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0) == "refunded"
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=111.0) == "no-spend"


def test_two_refs_with_one_landed_keeps_the_key_spent(world) -> None:
    command = "git push origin HEAD:refs/heads/a HEAD:refs/heads/b"
    _spend(command)
    _git(world["work"], "push", "-q", "origin", "HEAD:refs/heads/a")
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "landed", "ANYTHING landed means the key was used"
    assert not bk.status().held


def test_everything_up_to_date_keeps_the_key_spent(world) -> None:
    """The remote already holds the sha, so the answer is 'landed'; a no-op is not a failure."""
    _git(world["work"], "push", "-q", "origin", "HEAD:refs/heads/backup/x")
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0) == "landed"
    assert not bk.status().held


def test_a_remote_that_does_not_answer_returns_the_key_once_on_doubt(world) -> None:
    """Dad, 2026-11-15: an unclear answer must return the key too, "so you can try something else,
    otherwise you are stuck in the same boat.. no key and no answers". The remote path is gone."""
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    shutil.rmtree(world["bare"])
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "refunded-on-doubt", result
    assert bk.status().held
    assert bk.status().last_reissue.get("on_doubt") is True, "a doubt refund says it was one"


def test_a_second_doubt_without_a_repair_between_does_not_return_the_key(world) -> None:
    """The guard that makes Dad's rule safe: a bare push that LANDED reads as unclear, so doubt alone
    must not be free forever. One doubt refund per unrepaired lock; the next waits for a merged fix."""
    command = "git push"
    _spend(command)
    assert (
        bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
        == "refunded-on-doubt"
    )
    bk.spend(GATE, command, now=120.0)
    assert (
        bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=130.0)
        == "could-not-tell"
    )
    assert not bk.status().held


def test_a_repair_resets_the_doubt_refund(world) -> None:
    command = "git push"
    _spend(command)
    assert (
        bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
        == "refunded-on-doubt"
    )
    bk.spend(GATE, command, now=120.0)
    bk._log(bk.RETURNED, {"gate": GATE, "fingerprint": command, "repaired": "a merged fix"})
    bk.spend(GATE, command, now=130.0)
    assert (
        bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=140.0)
        == "refunded-on-doubt"
    )


def test_a_clear_no_does_not_use_up_the_doubt_refund(world) -> None:
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0) == "refunded"
    bk.spend(GATE, "git push", now=120.0)
    assert (
        bk.refund_if_not_landed(GATE, "git push", cwd=str(world["work"]), now=130.0)
        == "refunded-on-doubt"
    )


def test_a_clear_yes_is_never_refunded_on_doubt(world) -> None:
    """A landed ref beside an unclear one is still LANDED: doubt is for when nothing is known to have landed."""
    command = "git push origin HEAD:refs/heads/a HEAD"
    _spend(command)
    _git(world["work"], "push", "-q", "origin", "HEAD:refs/heads/a")
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "landed", result
    assert not bk.status().held


def test_a_remote_that_was_never_added_is_a_clear_no(world) -> None:
    """The first of today's two lost keys: the push named a remote that did not exist yet. A bare name
    that is not a configured remote cannot have received anything, so the key comes back."""
    command = "git push vault HEAD:refs/heads/backup/x"
    _spend(command)
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "refunded", result
    assert bk.status().held


def test_a_url_or_path_that_cannot_be_asked_is_doubt_not_a_clear_no(world, tmp_path: Path) -> None:
    """A url or a path is not a configured remote name, so 'no such remote' proves nothing about it:
    it is doubt, and doubt returns the key once."""
    command = f"git push {tmp_path / 'nowhere.git'} HEAD:refs/heads/backup/x"
    _spend(command)
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "refunded-on-doubt", result
    assert bk.status().held


@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin",
        "git push --all origin",
        "git push origin HEAD",
        "git push origin :refs/heads/gone",
        "git push origin --delete gone",
    ],
)
def test_a_push_that_names_no_clear_ref_is_doubt_and_returns_the_key_once(
    world, command: str
) -> None:
    _spend(command)
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0)
    assert result == "refunded-on-doubt", result
    assert bk.status().held


def test_a_different_push_than_the_one_that_spent_it_is_not_refunded(world) -> None:
    _spend("git push origin HEAD:refs/heads/a")
    result = bk.refund_if_not_landed(
        GATE, "git push origin HEAD:refs/heads/b", cwd=str(world["work"]), now=110.0
    )
    assert result == "not-this-push", result
    assert not bk.status().held


def test_a_push_with_a_trailing_clause_cannot_ride_the_refund(world) -> None:
    """`git push ...; exit 1` after a push that landed must not be read as a failed push."""
    spent = "git push origin HEAD:refs/heads/backup/x"
    _spend(spent)
    _git(world["work"], "push", "-q", "origin", "HEAD:refs/heads/backup/x")
    result = bk.refund_if_not_landed(GATE, spent + "; exit 1", cwd=str(world["work"]), now=110.0)
    assert result in ("landed", "not-this-push"), result
    assert not bk.status().held


def test_no_spend_means_nothing_to_refund(world) -> None:
    result = bk.refund_if_not_landed(
        GATE, "git push origin HEAD:refs/heads/a", cwd=str(world["work"]), now=110.0
    )
    assert result == "no-spend", result


def test_a_refund_is_bound_to_the_one_gate_whose_key_is_spent_on_a_push(world) -> None:
    _spend("git push origin HEAD:refs/heads/a")
    with pytest.raises(ValueError):
        bk.refund_if_not_landed("some-other-gate", "git push origin HEAD:refs/heads/a")


def test_a_refund_is_late_when_the_spend_is_old(world) -> None:
    """A spend from long ago is not this push; a stale window refunds nothing."""
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command, at=100.0)
    result = bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=100.0 + 7200)
    assert result == "too-late", result
    assert not bk.status().held


def test_a_refunded_key_can_be_spent_again(world) -> None:
    command = "git push origin HEAD:refs/heads/backup/x"
    _spend(command)
    assert bk.refund_if_not_landed(GATE, command, cwd=str(world["work"]), now=110.0) == "refunded"
    bk.spend(GATE, command, now=120.0)
    assert not bk.status().held


# The real hook, run for real, and the proof that it is registered (Bengio: automatic, not remembered).
_HOOK = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "refund-bypass-key-if-push-failed.sh"
)
_SETTINGS = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"


def test_the_refund_hook_is_registered_to_run_after_every_bash_command() -> None:
    import json

    data = json.loads(_SETTINGS.read_text(encoding="utf-8"))
    bash_blocks = [b for b in data["hooks"]["PostToolUse"] if b.get("matcher") == "Bash"]
    commands = [h["command"] for b in bash_blocks for h in b["hooks"]]
    assert any("refund-bypass-key-if-push-failed.sh" in c for c in commands), (
        "built but not wired: nothing would ever call the refund"
    )
    assert _HOOK.is_file()


def test_the_hook_does_nothing_and_says_nothing_for_a_command_that_is_not_a_push(
    tmp_path: Path,
) -> None:
    import json

    found = shutil.which("bash")
    assert found
    payload = json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": "ls"}, "tool_response": {"stdout": ""}}
    )
    env = dict(os.environ, PYTHONPATH=str(_HOOK.parents[2] / "src"), DIVINEOS_HOME=str(tmp_path))
    result = subprocess.run(
        [found, str(_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=str(_HOOK.parents[2]),
    )
    assert result.returncode == 0, result.stderr
    assert "bypass key" not in (result.stdout + result.stderr).lower()
    assert sys.platform  # the hook never blocks a command; it only speaks when it refunds
