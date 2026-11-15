"""The push refuses a hook that this push ADDS and nothing calls.

Dad, 2026-11-10: "NOTHING is to even push to github without it being FULLY WIRED UP.. PLUGGED IN AND WORKING LIVE"
and "who the fuck says a test passes on something THAT WAS NEVER FUCKING USED". The house already has the check:
scripts/check_hook_wiring.py (Andrew 2026-08-05) names every hook that is neither registered in settings.json nor
declared INTENTIONALLY UNWIRED. It ran only in scripts/precommit.sh, which Aether wrote on 2026-10-08 "is wired to
nothing", so a finished, tested hook (PR 845, the bell that re-arms itself) reached GitHub dark. The push is the one
place every branch passes, so the same check runs there, as a ratchet over what THIS push adds: existing declared or
dark hooks block nothing.

SYNTHETIC REPOS, never this repository: a gate test whose answer depends on where it stands is not a measurement
(its sibling test_push_gate_draft_path.py says the same).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).parent.parent
_SCRIPTS = _PROJECT_ROOT / "scripts"
_NEEDED = (
    "check_push_readiness.sh",
    "check_branch_scope.py",
    "draft_test_selection.py",
    "check_hook_wiring.py",
)
_ZERO = "0" * 40
_REFUSAL = "a hook this push adds is not wired"


def _find_bash() -> str | None:
    for candidate in (r"C:\Program Files\Git\bin\bash.exe", "/bin/bash", "/usr/bin/bash"):
        if Path(candidate).exists():
            return candidate
    return shutil.which("bash")


_BASH = _find_bash()

pytestmark = [
    pytest.mark.timeout(600),
    pytest.mark.skipif(_BASH is None, reason="bash not available"),
]

_HARNESS_OWNED = frozenset(
    {"DIVINEOS_DB", "DIVINEOS_HOME", "DIVINEOS_SESSION_ID", "DIVINEOS_DISABLE_AUTO_REMEDIATE"}
)


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, check=True)
    return done.stdout.strip()


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "test")
    (root / "scripts").mkdir()
    for name in _NEEDED:
        shutil.copy2(_SCRIPTS / name, root / "scripts" / name)
    (root / ".claude" / "hooks").mkdir(parents=True)
    (root / ".claude" / "settings.json").write_text(json.dumps({"hooks": {}}), encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "thing.py").write_text("value = 1\n", encoding="utf-8")
    _commit(root, "base")
    _git(root, "update-ref", "refs/remotes/origin/main", _git(root, "rev-parse", "HEAD"))
    return root


def _add_hook(repo: Path, name: str, body: str) -> None:
    (repo / ".claude" / "hooks" / name).write_text(body, encoding="utf-8")
    _commit(repo, f"add {name}")


def _register(repo: Path, name: str) -> None:
    settings = {
        "hooks": {
            "Stop": [{"hooks": [{"type": "command", "command": f"bash .claude/hooks/{name}"}]}]
        }
    }
    (repo / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    _commit(repo, f"register {name}")


def _push(repo: Path) -> subprocess.CompletedProcess[str]:
    sha = _git(repo, "rev-parse", "HEAD")
    env = {
        k: v for k, v in os.environ.items() if not k.startswith("DIVINEOS_") or k in _HARNESS_OWNED
    }
    return subprocess.run(
        [_BASH, str(repo / "scripts" / "check_push_readiness.sh")],
        input=f"refs/heads/work {sha} refs/heads/work {_ZERO}\n",
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(repo),
        env=env,
    )


def _said(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


def test_a_hook_the_push_adds_that_nothing_calls_is_refused_and_named(repo):
    _add_hook(repo, "brand_new_hook.sh", "#!/bin/bash\nexit 0\n")
    result = _push(repo)
    assert result.returncode != 0, _said(result)[-2500:]
    assert _REFUSAL in _said(result), _said(result)[-2500:]
    assert "brand_new_hook.sh" in _said(result)


def test_the_same_hook_registered_in_settings_is_not_refused_for_wiring(repo):
    _add_hook(repo, "brand_new_hook.sh", "#!/bin/bash\nexit 0\n")
    _register(repo, "brand_new_hook.sh")
    assert _REFUSAL not in _said(_push(repo))


def test_a_note_saying_the_hook_is_unwired_on_purpose_does_not_clear_it(repo):
    """Dad 2026-11-10: "there is nothing that should not be fucking wired up". The header note was a way out
    the lazy path would take every time, so it is not one."""
    _add_hook(
        repo,
        "kept_for_git.sh",
        "#!/bin/bash\n# INTENTIONALLY UNWIRED (2026-11-10): git calls this one, settings never will.\nexit 0\n",
    )
    result = _push(repo)
    assert result.returncode != 0, _said(result)[-2500:]
    assert _REFUSAL in _said(result)
    assert "kept_for_git.sh" in _said(result)


def test_the_old_emergency_switch_does_nothing_because_there_is_no_option(repo):
    """Dad 2026-11-10: "options are the optimizers attack surface". The variable the neighbouring checks
    honour is not honoured here, so setting it cannot get a dark hook through."""
    _add_hook(repo, "brand_new_hook.sh", "#!/bin/bash\nexit 0\n")
    sha = _git(repo, "rev-parse", "HEAD")
    env = {
        k: v for k, v in os.environ.items() if not k.startswith("DIVINEOS_") or k in _HARNESS_OWNED
    }
    env["DIVINEOS_SKIP_WIRING_CHECK"] = "1"
    result = subprocess.run(
        [_BASH, str(repo / "scripts" / "check_push_readiness.sh")],
        input=f"refs/heads/work {sha} refs/heads/work {_ZERO}\n",
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(repo),
        env=env,
    )
    assert result.returncode != 0, _said(result)[-2500:]
    assert _REFUSAL in _said(result)


def test_a_push_that_adds_no_hook_is_not_refused_for_wiring(repo):
    (repo / "src" / "thing.py").write_text("value = 2\n", encoding="utf-8")
    _commit(repo, "a change")
    assert _REFUSAL not in _said(_push(repo))


def test_a_dark_hook_already_on_main_blocks_nothing(repo):
    """The ratchet: only what THIS push adds is judged, so the backlog never blocks an unrelated push."""
    _add_hook(repo, "old_dark_hook.sh", "#!/bin/bash\nexit 0\n")
    _git(repo, "update-ref", "refs/remotes/origin/main", _git(repo, "rev-parse", "HEAD"))
    (repo / "src" / "thing.py").write_text("value = 3\n", encoding="utf-8")
    _commit(repo, "an unrelated change")
    assert _REFUSAL not in _said(_push(repo))
