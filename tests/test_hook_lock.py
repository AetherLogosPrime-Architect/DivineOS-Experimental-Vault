"""A hook added to the harness settings needs a recorded reason; a removal never does.

Dad, 2026-11-12: "make it impossible to add a new hook without going through this same
process or it will happen all over again." The lock reads FACTS about the diff -- the set
of (event, command) registrations at base and at head -- never words. Moving a hook into
the router removes a registration, so it passes with no special case.
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from divineos.core.hook_lock import (
    UnreadableBase,
    added_registrations,
    check_against_base,
    parse_reason,
    registrations,
    unexplained,
)


def _settings(**events):
    return {
        "hooks": {
            event: [{"matcher": "", "hooks": [{"type": "command", "command": c} for c in cmds]}]
            for event, cmds in events.items()
        }
    }


def test_registrations_are_counted_per_hook_not_per_group():
    s = _settings(Stop=["a.sh", "b.sh"], PreToolUse=["c.sh"])
    assert registrations(s) == {("Stop", "a.sh"), ("Stop", "b.sh"), ("PreToolUse", "c.sh")}


def test_zero_registrations_and_a_missing_hooks_key_are_empty_not_an_error():
    assert registrations({}) == set()
    assert registrations({"hooks": {}}) == set()


def test_an_added_registration_is_found():
    base = _settings(Stop=["a.sh"])
    head = _settings(Stop=["a.sh", "new.sh"])
    assert added_registrations(base, head) == {("Stop", "new.sh")}


def test_a_removed_registration_is_never_an_addition():
    # Moving a hook into the router removes its registration: the cure must pass.
    base = _settings(Stop=["a.sh", "old.sh"])
    head = _settings(Stop=["a.sh"])
    assert added_registrations(base, head) == set()


def test_a_renamed_script_counts_as_one_added_and_one_removed():
    base = _settings(Stop=["old.sh"])
    head = _settings(Stop=["new.sh"])
    assert added_registrations(base, head) == {("Stop", "new.sh")}


def test_a_change_to_a_non_hooks_key_adds_nothing():
    base = {"permissions": {"allow": []}, **_settings(Stop=["a.sh"])}
    head = {"permissions": {"allow": ["x"]}, **_settings(Stop=["a.sh"])}
    assert added_registrations(base, head) == set()


REASON = (
    "hook: Stop | new.sh\nwhy-not-router: it needs the raw harness event before the router starts\n"
)


def test_a_reason_names_its_hook_and_carries_a_nonempty_why():
    assert parse_reason(REASON) == {
        ("Stop", "new.sh"): "it needs the raw harness event before the router starts"
    }


def test_an_empty_why_is_not_a_reason():
    assert parse_reason("hook: Stop | new.sh\nwhy-not-router:   \n") == {}


def test_an_added_hook_with_no_reason_is_unexplained():
    assert unexplained({("Stop", "new.sh")}, reasons={}) == {("Stop", "new.sh")}


def test_an_added_hook_with_a_reason_is_explained():
    assert unexplained({("Stop", "new.sh")}, reasons=parse_reason(REASON)) == set()


# The instrument must be able to find a case it should find: a real repo, a real commit.


def _git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _repo_with_base():
    repo = Path(tempfile.mkdtemp())
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    (repo / ".claude").mkdir()
    (repo / ".claude" / "settings.json").write_text(
        json.dumps(_settings(Stop=["a.sh"])), encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    return repo


def test_a_real_added_registration_is_refused_and_the_refusal_says_what_it_cannot_see():
    repo = _repo_with_base()
    (repo / ".claude" / "settings.json").write_text(
        json.dumps(_settings(Stop=["a.sh", "new.sh"])), encoding="utf-8"
    )
    verdict = check_against_base(repo, "HEAD")
    assert verdict.refused
    assert ("Stop", "new.sh") in verdict.missing
    assert "settings.json" in verdict.message
    assert "user-level" in verdict.message  # says plainly which layer it does not see


def test_a_real_removal_passes():
    repo = _repo_with_base()
    (repo / ".claude" / "settings.json").write_text(json.dumps(_settings()), encoding="utf-8")
    assert not check_against_base(repo, "HEAD").refused


def test_a_reason_filed_at_base_lets_the_hook_in():
    repo = _repo_with_base()
    (repo / "docs" / "hook_additions").mkdir(parents=True)
    (repo / "docs" / "hook_additions" / "new.md").write_text(REASON, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "reason first")
    (repo / ".claude" / "settings.json").write_text(
        json.dumps(_settings(Stop=["a.sh", "new.sh"])), encoding="utf-8"
    )
    assert not check_against_base(repo, "HEAD").refused


def test_an_untracked_local_settings_file_is_not_counted():
    # settings.local.json is usually personal and untracked; counting it at head but not at
    # base would refuse every machine that has one (walk: Holmes).
    repo = _repo_with_base()
    (repo / ".claude" / "settings.local.json").write_text(
        json.dumps(_settings(Stop=["mine-only.sh"])), encoding="utf-8"
    )
    assert not check_against_base(repo, "HEAD").refused


def test_an_unreadable_base_raises_and_never_passes():
    # A shallow clone cannot resolve the base. Silence would read as "no hooks at base".
    repo = _repo_with_base()
    with pytest.raises(UnreadableBase):
        check_against_base(repo, "no-such-ref")


def test_the_push_readiness_script_calls_the_check():
    # Built-but-unwired ships dead (walk: Breaker). The caller must stay in the script.
    root = Path(__file__).resolve().parent.parent
    script = (root / "scripts" / "check_push_readiness.sh").read_text(encoding="utf-8")
    assert "check_new_hooks.py" in script
    assert (root / "scripts" / "check_new_hooks.py").exists()


def test_the_push_step_does_not_hide_the_refusal():
    # "my push was refused and I do not know why" (walk: Breaker). No redirect may hide it.
    root = Path(__file__).resolve().parent.parent
    script = (root / "scripts" / "check_push_readiness.sh").read_text(encoding="utf-8")
    lines = [ln for ln in script.splitlines() if "check_new_hooks.py" in ln]
    assert lines
    assert not any("/dev/null" in ln for ln in lines)


def test_a_reason_written_in_the_same_change_does_not_count():
    # Schneier's cheapest path: edit the allow-list in the same commit as the new hook.
    repo = _repo_with_base()
    (repo / "docs" / "hook_additions").mkdir(parents=True)
    (repo / "docs" / "hook_additions" / "new.md").write_text(REASON, encoding="utf-8")
    (repo / ".claude" / "settings.json").write_text(
        json.dumps(_settings(Stop=["a.sh", "new.sh"])), encoding="utf-8"
    )
    assert check_against_base(repo, "HEAD").refused
