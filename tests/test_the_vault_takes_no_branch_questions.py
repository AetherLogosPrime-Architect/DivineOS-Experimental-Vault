"""A push to the Vault is not asked the questions written for pull requests to main.

Dad, 2026-11-15: the Vault "needs no checks or tests or anything", it is for what we do not want to
lose that has not reached main, and broken or unfinished work may go there. The branch check
(check-branch-on-push) asks "would this look like it deletes work on main?", a question about pull
requests, and spends the one bypass key to answer it. Aria's first vault push spent two keys on pushes
that never landed.

The half that matters more is the other direction: a push that only LOOKS like the Vault must still be
checked (walk-8a9bb5b1fc18). A remote merely NAMED vault must not buy a pass, so the answer is read from
the remote's real PUSH url. The hook reads that url before the chain runs, so a chain that changes the
remote first must not ride the skip. Most of this file is those cases.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from divineos.core.push_detection import pushes_only_to_vault

VAULT_URL = "https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git"
MAIN_URL = "https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental.git"
_URLS = {"vault": VAULT_URL, "origin": MAIN_URL, "main-repo": "https://github.com/x/DivineOS.git"}


def _url_of(remote: str) -> str | None:
    return _URLS.get(remote)


@pytest.mark.parametrize(
    "command",
    [
        "git push vault HEAD:refs/heads/backup/aria-house-2026-11-15",
        "git push -q vault backup/x",
        "git push --force-with-lease vault backup/x",
        "git push -o ci.skip vault backup/x",
        "git push vault --tags",
        'cd "C:/w507" && git push vault backup/x',
        "git push vault a && git push vault b",
        "git push -u vault aria/keepsafe",
    ],
)
def test_pushes_that_go_only_to_the_vault_are_recognised(command: str) -> None:
    assert pushes_only_to_vault(command, url_of=_url_of)


@pytest.mark.parametrize(
    "command",
    [
        # another remote entirely
        "git push origin main",
        "git push main-repo main",
        # a second push in the chain goes elsewhere: it must not ride the vault's pass
        "git push vault x && git push origin y",
        "git push origin y && git push vault x",
        "git push vault x; git push origin y",
        # the same smuggle through git's own -C, which the strict push pattern does not see
        "git push vault x && git -C other push origin y",
        # the hook reads the url BEFORE the chain runs: a chain that changes the remote first
        "git remote set-url vault https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental.git && git push vault x",
        "git remote set-url --push vault https://example.invalid/x.git && git push vault x",
        "git config remote.vault.pushurl https://example.invalid/x.git && git push vault x",
        "echo hi && git push vault x",
        # no remote named: git picks one, so it could be origin
        "git push",
        "git push --all",
        # --repo names the remote after a flag, so the first positional is not it
        "git push --repo origin vault x",
        # the Vault's own main is left under the check, and so is a delete (Lovelace, Aristotle)
        "git push vault main",
        "git push vault HEAD:main",
        "git push vault HEAD:refs/heads/main",
        "git push vault HEAD:MAIN",
        "git push vault HEAD:refs/heads/Main",
        "git push vault HEAD:",
        "git push vault +",
        "git push vault HEAD",
        "git push vault",
        "git push vault && git push vault",
        'cd "C:/w507"',
        "git push -q vault HEAD:refs/heads/backup/x 2>&1 | node -e 1",
        "git push vault :backup/x",
        "git push vault --delete backup/x",
        "git push --mirror vault",
        "git push --all vault",
        # a remote that does not exist: could not tell, so the check runs
        "git push nowhere x",
        # could not parse
        "git push vault 'x",
        # not a push at all
        "git status",
        "",
    ],
)
def test_anything_that_could_reach_another_remote_or_hurt_the_vault_is_not(command: str) -> None:
    assert not pushes_only_to_vault(command, url_of=_url_of)


def test_a_remote_only_named_vault_buys_no_pass() -> None:
    urls = {"vault": MAIN_URL}  # named vault, pointing at the main working repo
    assert not pushes_only_to_vault("git push vault x", url_of=urls.get)


@pytest.mark.parametrize(
    "url",
    [
        VAULT_URL,
        VAULT_URL.removesuffix(".git"),
        VAULT_URL + "/",
        "git@github.com:AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git",
        "https://github.com/aetherlogosprime-architect/divineos-experimental-vault",
    ],
)
def test_the_vault_is_known_by_its_url_in_every_spelling(url: str) -> None:
    assert pushes_only_to_vault("git push v x", url_of={"v": url}.get)


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/SomeoneElse/DivineOS-Experimental-Vault.git",
        "https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental-Vault-fork.git",
        "https://evil.example/AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git",
        "https://github.com.evil.example/AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git",
        "",
        "not a url",
    ],
)
def test_a_lookalike_url_is_not_the_vault(url: str) -> None:
    assert not pushes_only_to_vault("git push v x", url_of={"v": url}.get)


def test_a_remote_that_cannot_be_read_is_not_the_vault() -> None:
    assert not pushes_only_to_vault("git push vault x", url_of=lambda remote: None)


# The hook itself, run for real. A reasonless kill-switch marker in a throwaway home refuses EVERY
# push that reaches the check, so a push that must be checked is refused (the control) and a push to
# the Vault must not be, because it never gets there.
_HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "check-branch-on-push.sh"


def _bash() -> str:
    found = shutil.which("bash")
    assert found, "no bash on PATH; this suite cannot exercise shell hooks"
    probe = subprocess.run([found, "-c", "exit 7"], capture_output=True)
    assert probe.returncode == 7, f"{found} cannot run a trivial script"
    return found


_HOUSE: list[Path] = []


def _repo(path: Path, **remotes: str) -> Path:
    """A throwaway repo that carries the real hook folder AND the real source, with the given remotes.

    The hook cds to the root of the repo it is run in, sources its own _lib.sh from there, and fails
    OPEN when that is missing; and it accepts a Python only if the divineos that Python sees lives
    under THIS repo. So a bare temp repo would pass every push and prove nothing. Built once per run
    (src is 56 MB) in a folder the platform's temp cleaner owns, and only its remotes change per test.
    """
    if not _HOUSE:
        import tempfile

        house = Path(tempfile.mkdtemp(prefix="vault_house_"))
        subprocess.run(["git", "init", "-q", str(house)], check=True)
        shutil.copytree(_HOOK.parent, house / ".claude" / "hooks")
        shutil.copytree(
            _HOOK.parents[2] / "src",
            house / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        _HOUSE.append(house)
    house = _HOUSE[0]
    listed = subprocess.run(
        ["git", "-C", str(house), "remote"], capture_output=True, text=True, check=True
    ).stdout.split()
    for name in listed:
        subprocess.run(["git", "-C", str(house), "remote", "remove", name], check=True)
    for name, url in remotes.items():
        subprocess.run(["git", "-C", str(house), "remote", "add", name, url], check=True)
    return house


def _python_shim(folder: Path) -> Path:
    """The hook finds its Python in the repo's own .venv or on PATH; a throwaway repo has no .venv, so a
    one-line python3 in a folder at the front of PATH hands it the interpreter running this test."""
    folder.mkdir(parents=True, exist_ok=True)
    shim = folder / "python3"
    real = Path(sys.executable).as_posix()
    shim.write_text(f'#!/bin/sh\nexec "{real}" "$@"\n', encoding="utf-8")
    return folder


def _run_hook(command: str, home: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = dict(os.environ)
    env["PYTHONPATH"] = str(cwd / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["PATH"] = str(_python_shim(home.parent / "shim")) + os.pathsep + env.get("PATH", "")
    env["DIVINEOS_HOME"] = str(home)
    return subprocess.run(
        [_bash(), str(cwd / ".claude" / "hooks" / _HOOK.name)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=str(cwd),
    )


def _marked_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    (home / "check-branch.disabled").write_text("", encoding="utf-8")
    return home


def test_the_hook_lets_a_vault_push_through_without_the_branch_check_or_the_key(
    tmp_path: Path,
) -> None:
    home = _marked_home(tmp_path)
    repo = _repo(tmp_path / "repo", vault=VAULT_URL, origin=MAIN_URL)

    control = _run_hook("git push origin archive/some/branch", home=home, cwd=repo)
    assert control.returncode == 2, control.stderr
    assert "NO REASON" in control.stderr

    vault = _run_hook("git push vault backup/some/branch", home=home, cwd=repo)
    assert vault.returncode == 0, vault.stderr
    assert (home / "check-branch.disabled").exists(), "a vault push must not consume the switch"
    assert "vault" in vault.stderr.lower(), "a skipped check says so, never silently"


def test_the_hook_still_checks_a_push_to_a_remote_only_named_vault(tmp_path: Path) -> None:
    home = _marked_home(tmp_path)
    repo = _repo(tmp_path / "repo", vault=MAIN_URL)

    result = _run_hook("git push vault backup/some/branch", home=home, cwd=repo)
    assert result.returncode == 2, result.stderr
    assert "NO REASON" in result.stderr


def test_the_hook_still_checks_a_chain_that_changes_the_remote_first(tmp_path: Path) -> None:
    home = _marked_home(tmp_path)
    repo = _repo(tmp_path / "repo", vault=VAULT_URL)

    chain = f"git remote set-url vault {MAIN_URL} && git push vault backup/x"
    result = _run_hook(chain, home=home, cwd=repo)
    assert result.returncode == 2, result.stderr
    assert "NO REASON" in result.stderr


def test_the_hook_still_checks_the_vaults_own_main(tmp_path: Path) -> None:
    home = _marked_home(tmp_path)
    repo = _repo(tmp_path / "repo", vault=VAULT_URL)

    result = _run_hook("git push vault HEAD:main", home=home, cwd=repo)
    assert result.returncode == 2, result.stderr
    assert "NO REASON" in result.stderr


# The git pre-push hook is the second layer: it calls the freshness script as `origin main` whatever it
# is pushing to. It is run for real from the template setup writes (the installed copy is only a copy of
# it), with git's own two arguments: the remote's name and the URL the bytes go to.
_SETUP = _HOOK.parents[2] / "setup" / "setup-hooks.sh"
_SKIP_LINE = "push to the Vault: no checks run"


def _pre_push(tmp_path: Path, remote: str, url: str) -> subprocess.CompletedProcess[str]:
    from divineos.core.git_hooks_drift import setup_hooks

    hook = tmp_path / "pre-push"
    hook.write_bytes(setup_hooks(_SETUP.read_text(encoding="utf-8"))["pre-push"].encode("utf-8"))
    repo = tmp_path / "bare_repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    env = dict(os.environ, DIVINEOS_SKIP_TESTS="1", DIVINEOS_SKIP_FRESHNESS_CHECK="1")
    return subprocess.run(
        [_bash(), str(hook), remote, url],
        input="",
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=str(repo),
    )


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental-Vault",
        VAULT_URL,
        "git@github.com:AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git",
    ],
)
def test_the_pre_push_hook_runs_no_checks_for_the_vault(tmp_path: Path, url: str) -> None:
    result = _pre_push(tmp_path, "whatever-it-is-called", url)
    assert result.returncode == 0, result.stderr
    assert _SKIP_LINE in result.stderr, "a skipped check says so, never silently"


@pytest.mark.parametrize(
    "url",
    [
        MAIN_URL,
        "https://github.com/AetherLogosPrime-Architect/DivineOS-Experimental-Vault-fork.git",
        "https://github.com/SomeoneElse/DivineOS-Experimental-Vault.git",
        "https://evil.example/AetherLogosPrime-Architect/DivineOS-Experimental-Vault.git",
        "",
    ],
)
def test_the_pre_push_hook_still_runs_for_anything_else(tmp_path: Path, url: str) -> None:
    """A remote NAMED vault but pointing elsewhere gets no pass: the hook reads the URL, not the name."""
    result = _pre_push(tmp_path, "vault", url)
    assert _SKIP_LINE not in result.stderr
