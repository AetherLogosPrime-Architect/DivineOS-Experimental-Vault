"""The lock on new hooks: a registration added to the harness settings needs a reason.

Dad, 2026-11-12: make it impossible to add a new hook without going through the process,
or the hundred-hook sprawl returns. This is a gate on the push path, not a proof: it makes
an unexplained addition visible and refused at one gate, and the bypass stays counted.

The check reads FACTS about a diff, never words: the set of (event, command) registrations
at the base ref and in the working tree, one per hook (not per group). A removal is never
an addition, so moving a hook into the router passes with no special case. Two commands
that differ only by spelling are two hooks; a reformatted command reads as one removed and
one added.

A reason is a small file under docs/hook_additions/ naming the hook with a non-empty
why-not-router field. It is read from the BASE ref, so a reason written in the same change
as the hook does not count (council walk-e91f08327219 and walk-7b0c47393643). The check
only asks that the field is filled; it never judges what it says.

Only TRACKED settings files are counted: settings.local.json is usually personal and
untracked, and counting it at head but not at base would refuse every machine that has one.

Said in every refusal: user-level settings outside the repo, and logic added inside an
existing script, are not seen.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

REASON_DIR = "docs/hook_additions"
SETTINGS_FILES = (".claude/settings.json", ".claude/settings.local.json")

Registration = tuple[str, str]


class UnreadableBase(RuntimeError):
    """The base ref cannot be resolved (a shallow clone, a typo). Never read as 'no hooks'."""


def registrations(settings: dict) -> set[Registration]:
    """Every (event, command) pair, one per hook."""
    found: set[Registration] = set()
    for event, groups in (settings.get("hooks") or {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                command = hook.get("command")
                if command:
                    found.add((event, command))
    return found


def added_registrations(base: dict, head: dict) -> set[Registration]:
    return registrations(head) - registrations(base)


def parse_reason(text: str) -> dict[Registration, str]:
    """`hook: EVENT | COMMAND` followed by a non-empty `why-not-router:` line."""
    reasons: dict[Registration, str] = {}
    pending: Registration | None = None
    for line in text.splitlines():
        key, _, value = line.partition(":")
        key, value = key.strip().lower(), value.strip()
        if key == "hook" and "|" in value:
            event, _, command = value.partition("|")
            pending = (event.strip(), command.strip())
        elif key == "why-not-router" and pending is not None:
            if value:
                reasons[pending] = value
            pending = None
    return reasons


def unexplained(added: set[Registration], reasons: dict[Registration, str]) -> set[Registration]:
    return {reg for reg in added if reg not in reasons}


@dataclass(frozen=True)
class Verdict:
    refused: bool
    missing: frozenset[Registration]
    message: str


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )


def _merge_layer(merged: dict, text: str) -> None:
    for event, groups in (json.loads(text).get("hooks") or {}).items():
        merged["hooks"].setdefault(event, []).extend(groups)


def _layers_at_base(repo: Path, ref: str) -> dict:
    merged: dict = {"hooks": {}}
    for name in SETTINGS_FILES:
        shown = _git(repo, "show", f"{ref}:{name}")
        if shown.returncode == 0 and shown.stdout.strip():
            _merge_layer(merged, shown.stdout)
    return merged


def _layers_at_head(repo: Path) -> dict:
    merged: dict = {"hooks": {}}
    for name in SETTINGS_FILES:
        tracked = _git(repo, "ls-files", "--error-unmatch", name).returncode == 0
        path = repo / name
        if tracked and path.exists():
            _merge_layer(merged, path.read_text(encoding="utf-8"))
    return merged


def _reasons_at(repo: Path, ref: str) -> dict[Registration, str]:
    listing = _git(repo, "ls-tree", "-r", "--name-only", ref, REASON_DIR).stdout
    reasons: dict[Registration, str] = {}
    for name in listing.split():
        reasons.update(parse_reason(_git(repo, "show", f"{ref}:{name}").stdout))
    return reasons


def check_against_base(repo: Path, base_ref: str) -> Verdict:
    if _git(repo, "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}").returncode:
        raise UnreadableBase(
            f"cannot resolve base ref {base_ref!r}: a shallow clone or a wrong name; "
            "the lock will not read an unreadable base as 'no hooks'"
        )
    base = _layers_at_base(repo, base_ref)
    head = _layers_at_head(repo)
    missing = unexplained(added_registrations(base, head), _reasons_at(repo, base_ref))
    if not missing:
        return Verdict(False, frozenset(), "")
    listed = "\n".join(f"  - {event}: {command}" for event, command in sorted(missing))
    return Verdict(
        True,
        frozenset(missing),
        "MINE, and here is why. A hook was added with no reason filed before it:\n"
        f"{listed}\n"
        f"The reason goes in {REASON_DIR}/<name>.md, committed BEFORE the hook, with the "
        "lines `hook: EVENT | COMMAND` and `why-not-router: <why a router row could not "
        "do this>`. A hook that moves INTO the router removes a registration and needs "
        "none; a reformatted command counts as a new hook. This check reads the tracked "
        ".claude/settings.json and .claude/settings.local.json; it does not see "
        "user-level settings outside the repo, and it does not see logic added inside "
        "an existing script.",
    )
