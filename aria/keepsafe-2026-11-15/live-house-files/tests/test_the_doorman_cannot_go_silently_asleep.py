"""The build-flow doorman may never be asleep without saying so.

Found 2026-11-11 by trying an unprepared edit while the briefing was stale: the edit went through. Root cause, read
from the code and not guessed: the hook asks ``divineos work-item gate``; the CLI refuses EVERY command that is not on
its short bootstrap list when the briefing is not loaded (cli/__init__.py, _enforce_briefing_gate, exit 1); and the
hook treats every answer other than exit 2 as permission. So a stale briefing turned the door that guards every build
into a permission, silently, for as long as the briefing stayed stale (Dad: "for as long as the briefing was not
enforced.. which has literally been for months").

Two faults, two kinds of test, both written BEFORE the fix:

1. The hook: when the checker could not answer, the door must not be both permissive and silent. (Whether it holds
   or says so loudly is the walk's decision; this pins only that silent-and-open cannot be the outcome.)
2. The checker: the doorman's own command must be able to answer with no briefing loaded, because its answer depends
   on the work-item store and not on the briefing. A gate must never be blocked by a gate that is not its business.

Real commands, a fresh empty home for every run so nothing here can touch a real ledger (the lesson of the same night:
a "read-only" check that used the real CLI wrote two records into a folder that was not mine to write in).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / ".claude" / "hooks" / "work-item-doorman.sh"
PAYLOAD = json.dumps(
    {"tool_name": "Write", "tool_input": {"file_path": "src/x.py", "content": "x = 1\n"}}
)
BRIEFING_BLOCK = "BLOCKED: Briefing not loaded"


def _git_bash() -> str:
    """A bash PROVEN to run a script (asked to exit 7), found beside git so the WSL stub cannot win."""
    candidates = []
    git = shutil.which("git")
    if git:
        here = Path(git)
        candidates += [here.parents[1] / "bin" / "bash.exe", here.parents[2] / "bin" / "bash.exe"]
    found = shutil.which("bash")
    if found:
        candidates.append(Path(found))
    for c in candidates:
        if (
            c.is_file()
            and subprocess.run(
                [str(c), "-c", "exit 7"], capture_output=True, check=False
            ).returncode
            == 7
        ):
            return str(c)
    pytest.skip("no bash here can be shown to run a script")
    return ""


def _fresh_env(tmp_path: Path) -> dict[str, str]:
    """An environment whose every home folder is empty and inside tmp_path."""
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "DIVINEOS_HOME": str(home / ".divineos"),
            "DIVINEOS_SHARED_DIR": str(home / ".divineos-shared"),
            "DIVINEOS_FAMILY_DB": str(home / "family.db"),
            "DIVINEOS_FAMILY_LEDGER_DIR": str(home / "family_ledgers"),
        }
    )
    env.pop("CLAUDE_PROJECT_DIR", None)
    return env


def _run_cli(args: list[str], tmp_path: Path, stdin: str = "") -> subprocess.CompletedProcess[str]:
    code = f"import sys; sys.argv = ['divineos'] + {args!r}; from divineos.cli import cli; cli()"
    return subprocess.run(
        [sys.executable, "-c", code],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
        env=_fresh_env(tmp_path),
        timeout=180,
        check=False,
    )


def test_the_control_a_gated_command_is_really_blocked_in_the_fresh_home(tmp_path: Path) -> None:
    """THE CONTROL. Without this, every test below could pass because the home is somehow briefed, and a pass would
    mean nothing: a dead control and a blind instrument return the same value."""
    # A command that is NOT on the bootstrap list. (First written with `work-item status`; once the fix put that group on
    # the list the control correctly failed, which is how a control earns its place: it noticed the thing it measures
    # with had changed.)
    out = _run_cli(["decisions", "list"], tmp_path)
    assert BRIEFING_BLOCK in (out.stdout + out.stderr), (
        "the fresh home is not briefing-less, so the tests below could not tell asleep from awake:\n"
        f"rc={out.returncode}\n{(out.stdout + out.stderr)[-400:]}"
    )


def test_the_doormans_own_command_answers_with_no_briefing_loaded(tmp_path: Path) -> None:
    """THE FAULT, at the checker. The gate command decides from the work-item store; it is not the briefing's business.
    On main this exits 1 with the briefing block, which the hook then reads as permission."""
    out = _run_cli(["work-item", "gate"], tmp_path, stdin=PAYLOAD)
    assert BRIEFING_BLOCK not in (out.stdout + out.stderr), (
        "the doorman's command was stopped by the briefing gate, so it never formed an answer:\n"
        f"rc={out.returncode}\n{(out.stdout + out.stderr)[-400:]}"
    )
    assert out.returncode in (0, 2), (
        f"the gate exited {out.returncode}, which is neither an allow nor a hold"
    )


@pytest.fixture
def unanswering_checker(tmp_path: Path) -> Path:
    """A stand-in ``divineos`` that behaves like the real one with no briefing: prints the block and exits 1."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = bin_dir / "divineos"
    script.write_text(
        '#!/usr/bin/env bash\ncat >/dev/null\necho "  BLOCKED: Briefing not loaded."\necho "  Run: divineos briefing"\nexit 1\n',
        encoding="utf-8",
    )
    script.chmod(0o755)
    return bin_dir


def test_a_checker_that_could_not_answer_is_never_silent_and_open(
    unanswering_checker: Path, tmp_path: Path
) -> None:
    """THE FAULT, at the door. Whether the door holds or says plainly that it let the call through is the walk's
    decision; what cannot stand is exit 0 with nothing said, which is what a sleeping guard looks like from outside."""
    env = _fresh_env(tmp_path)
    env["PATH"] = str(unanswering_checker) + os.pathsep + env.get("PATH", "")
    env["CLAUDE_PROJECT_DIR"] = str(REPO_ROOT)
    out = subprocess.run(
        [_git_bash(), str(HOOK)],
        input=PAYLOAD,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )
    silent_and_open = out.returncode == 0 and not out.stderr.strip() and not out.stdout.strip()
    assert not silent_and_open, (
        "the door let a call through in complete silence although its checker never answered"
    )


# ---- what walk-1f4842776480 added: the door has three states and must have three outputs ----------------------------

MARKER = "work-item-gate: allow"


def _stand_in(tmp_path: Path, body: str) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / "divineos"
    script.write_text("#!/usr/bin/env bash\ncat >/dev/null\n" + body, encoding="utf-8")
    script.chmod(0o755)
    return bin_dir


def _run_door(
    tmp_path: Path, *, path_dirs: list[Path], payload: str = PAYLOAD
) -> subprocess.CompletedProcess[str]:
    env = _fresh_env(tmp_path)
    env["PATH"] = os.pathsep.join(str(d) for d in path_dirs)
    env["CLAUDE_PROJECT_DIR"] = str(REPO_ROOT)
    return subprocess.run(
        [_git_bash(), str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    )


def _path_without_divineos() -> list[Path]:
    """The real PATH minus every folder that holds a ``divineos``, so 'not installed' is proven rather than assumed."""
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        folder = Path(entry)
        if entry and not any(
            (folder / name).exists()
            for name in ("divineos", "divineos.exe", "divineos.cmd", "divineos.bat")
        ):
            keep.append(folder)
    return keep


def test_the_checker_says_allow_in_its_own_words(tmp_path: Path) -> None:
    """The positive half. An allow is something the checker SAYS, so exit 0 alone can no longer pass for a yes."""
    out = _run_cli(
        ["work-item", "gate"],
        tmp_path,
        stdin=json.dumps({"tool_name": "Read", "tool_input": {"file_path": "README.md"}}),
    )
    assert out.returncode == 0, (out.stdout + out.stderr)[-400:]
    assert MARKER in out.stdout


def test_exit_zero_without_the_marker_is_not_taken_for_a_yes(tmp_path: Path) -> None:
    """A checker that crashed quietly and exited 0 is 'could not answer', not 'allowed'. The door says so."""
    out = _run_door(
        tmp_path, path_dirs=[_stand_in(tmp_path, "exit 0\n"), *_path_without_divineos()]
    )
    assert out.returncode == 0
    assert (out.stderr + out.stdout).strip(), "exit 0 with no marker passed in complete silence"
    assert (
        "NOT CHECK" in (out.stderr + out.stdout).upper()
        or "UNCHECKED" in (out.stderr + out.stdout).upper()
    )


def test_an_unchecked_pass_leaves_a_row_so_the_next_sleep_is_a_number(tmp_path: Path) -> None:
    """Holmes: no log recorded whether the checker answered, so a sleeping door and a working one looked identical. The
    row is the fix for that, and it must really be written (Pearl: how often it happened is unmeasured until it is)."""
    _run_door(tmp_path, path_dirs=[_stand_in(tmp_path, "exit 0\n"), *_path_without_divineos()])
    row_file = tmp_path / "home" / ".divineos" / "doorman_unchecked.jsonl"
    assert row_file.is_file(), "no row was written for a call the door could not check"
    row = json.loads(row_file.read_text(encoding="utf-8").splitlines()[-1])
    assert "without saying allow" in row["why"] and row["t"] > 0


def test_the_hooks_allow_words_and_the_checkers_are_the_same_words() -> None:
    """The hook and the command each carry the literal; if they drift, every real allow reads as 'could not answer' and
    the door cries wolf on every call, which is how a door gets switched off."""
    hook = HOOK.read_text(encoding="utf-8")
    command = (REPO_ROOT / "src" / "divineos" / "cli" / "work_item_commands.py").read_text(
        encoding="utf-8"
    )
    assert f'GATE_ALLOW_MARKER="{MARKER}"' in hook
    assert f'click.echo("{MARKER}")' in command


def test_exit_zero_with_the_marker_stays_quiet(tmp_path: Path) -> None:
    """The other direction: a real allow costs nothing. A door that speaks on every pass teaches me to scroll past it."""
    out = _run_door(
        tmp_path,
        path_dirs=[_stand_in(tmp_path, f'echo "{MARKER}"\nexit 0\n'), *_path_without_divineos()],
    )
    assert out.returncode == 0
    assert not out.stderr.strip() and not out.stdout.strip(), (out.stdout + out.stderr)[-300:]


def test_no_divineos_on_the_path_is_said_not_swallowed(tmp_path: Path) -> None:
    """The second silent exit, found by re-reading the hook: the checker is not installed, so the door exits 0 unspoken."""
    empty = tmp_path / "empty_bin"
    empty.mkdir()
    # bash itself must still be reachable for the script to run; only divineos is absent.
    out = _run_door(tmp_path, path_dirs=[empty, *_path_without_divineos()])
    assert out.returncode == 0
    assert (out.stderr + out.stdout).strip(), (
        "the door passed a call in silence because divineos was not on the path"
    )


def test_an_empty_payload_is_said_not_swallowed(tmp_path: Path) -> None:
    out = _run_door(
        tmp_path,
        path_dirs=[_stand_in(tmp_path, f'echo "{MARKER}"\nexit 0\n'), *_path_without_divineos()],
        payload="",
    )
    assert out.returncode == 0
    assert (out.stderr + out.stdout).strip(), "an empty payload passed in silence"


def test_the_real_door_with_the_real_checker_holds_an_unprepared_edit_with_no_briefing(
    tmp_path: Path,
) -> None:
    """THE END-TO-END TEST (Popper's severe one). The stand-in here is only a doorway to THIS tree's real checker, so the
    briefing gate, the work-item store and the decision are all real. No briefing, no open piece of work, an edit to
    code: it must be held. On main it is allowed, which is the whole fault."""
    runner = tmp_path / "realbin"
    runner.mkdir()
    wrapper = runner / "divineos"
    py = Path(sys.executable).as_posix()
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        f'exec "{py}" -c "import sys; sys.argv=[\'divineos\']+sys.argv[1:]; from divineos.cli import cli; cli()" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(0o755)
    out = _run_door(tmp_path, path_dirs=[runner, *_path_without_divineos()])
    assert out.returncode == 2, (
        f"the unprepared edit was not held (exit {out.returncode}); the door is asleep:\n{(out.stdout + out.stderr)[-500:]}"
    )
