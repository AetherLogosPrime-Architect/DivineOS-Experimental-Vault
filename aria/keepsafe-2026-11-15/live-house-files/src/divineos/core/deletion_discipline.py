"""Deletion-discipline gate — block destructive deletions until justified.

Per the deletion-discipline lesson (Andrew 2026-05-21): deletion is
destructive-but-sometimes-necessary; the forbidden shape is PURE deletion
(deleting without read-understand → investigate → extract-what's-needed).
Proven the same day: investigating ``talk-to-wrapper-collapse`` before
deleting found 47 files of needed work that pure deletion would have lost.

Per [code-does-not-think]: this gate does NOT judge whether a deletion is
wise — that judgment is mine. It RECORDS that I made the judgment (what /
why / what I investigated / what I extracted) and BLOCKS the destructive
operation until that record exists and is fresh. Code gates and records;
the thinking stays with me.

Prereg: prereg-251b15df9461.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from divineos.core.paths import marker_path

_JUSTIFICATION_FILE = "deletion_justifications.json"
_TTL_SECONDS = 600  # a justification is fresh for 10 minutes

# Paths whose recursive/force removal is routine cleanup, not loss of
# substrate. rm of ONLY these must NOT trip the gate — false-positive
# friction trains route-around (the gate-misfire family). Matched per-token.
_EPHEMERAL = re.compile(
    r"(__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|node_modules|"
    r"\.egg-info|htmlcov|\.coverage)|"
    r"\.pyc$|\.pyo$|\.tmp$|\.log$|"
    r"(^|/)(tmp|temp|build|dist)(/|$)|"
    r"^/tmp|^/var/tmp",
    re.IGNORECASE,
)

# Destructive git deletions.
_GIT_PUSH_DELETE = re.compile(r"\bgit\s+push\b[^|;&\n]*(--delete\b|\s:\w)", re.IGNORECASE)
_GIT_BRANCH_DELETE = re.compile(r"\bgit\s+branch\b[^|;&\n]*\s(-D|-d|--delete)\b", re.IGNORECASE)
_GIT_RM = re.compile(r"\bgit\s+rm\b", re.IGNORECASE)
# rm carrying a recursive (-r/-R) or force (-f) flag — the high-blast forms.
_RM_RECURSIVE_OR_FORCE = re.compile(r"\brm\s+(-{1,2}\S+\s+)*-{0,2}\w*[rRf]", re.IGNORECASE)

# Heredoc body: <<'EOF' ... EOF  /  <<EOF ... EOF  /  <<-EOF ... EOF
_HEREDOC = re.compile(r"<<-?\s*'?(\w+)'?.*?\n\1\b", re.DOTALL)
_DQUOTED = re.compile(r'"[^"]*"')
_SQUOTED = re.compile(r"'[^']*'")


def _sanitize_for_trigger(command: str) -> str:
    """Strip quoted-string and heredoc CONTENT before trigger detection.

    A deletion verb inside a commit message, echo, or heredoc body is not an
    invocation — it is text. Matching it is the context-blind-keyword misfire
    family (the gate fired on its own commit message describing it). Triggers
    are detected on this sanitized form; the ephemeral path-check still runs
    on the original (it needs the real paths). Known false-negative: a real
    deletion fully wrapped in quotes (``bash -c "git branch -D x"``) — rare,
    and a miss is safer than blocking every commit that mentions a delete."""
    s = _HEREDOC.sub(" ", command)
    s = _DQUOTED.sub(" ", s)
    s = _SQUOTED.sub(" ", s)
    return s


def _rm_targets_all_ephemeral(command: str) -> bool:
    """True if a recursive/force ``rm`` targets ONLY ephemeral paths.

    Extracts non-flag tokens after the first ``rm`` and checks every one is
    ephemeral. Conservative: if there are no clear targets, returns False
    (so the gate fires rather than waving an ambiguous rm through)."""
    m = re.search(r"\brm\b(.*)$", command, re.IGNORECASE | re.DOTALL)
    if not m:
        return False
    tail = re.split(r"[|;&]", m.group(1))[0]  # only the rm clause itself
    tokens = [t for t in tail.split() if not t.startswith("-")]
    if not tokens:
        return False
    return all(_EPHEMERAL.search(t) for t in tokens)


def is_destructive_deletion(command: str) -> tuple[bool, str | None]:
    """Classify a shell command. Returns (is_destructive, target-hint).

    Destructive = remote/local branch deletion, ``git rm``, or recursive/
    force ``rm`` of non-ephemeral paths. The target-hint is a best-effort
    label only; matching to a justification is done on the command text."""
    if not command or not command.strip():
        return False, None
    cmd = command.strip()
    # Detect the delete VERB on the sanitized command (quoted/heredoc content
    # stripped) so a deletion mentioned in a commit message is not a trigger.
    scan = _sanitize_for_trigger(cmd)
    if _GIT_PUSH_DELETE.search(scan):
        return True, "git push delete"
    if _GIT_BRANCH_DELETE.search(scan):
        return True, "git branch delete"
    if _GIT_RM.search(scan):
        return True, "git rm"
    # Ephemeral check runs on the ORIGINAL — it needs the real (possibly
    # quoted) paths to tell rm of /tmp from rm of src/.
    if _RM_RECURSIVE_OR_FORCE.search(scan) and not _rm_targets_all_ephemeral(cmd):
        return True, "rm recursive/force"
    return False, None


def _load() -> list[dict[str, Any]]:
    p = marker_path(_JUSTIFICATION_FILE)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save(entries: list[dict[str, Any]]) -> None:
    p = marker_path(_JUSTIFICATION_FILE)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def record_justification(
    target: str, why: str, investigated: str, extracted: str, now: float | None = None
) -> dict[str, Any]:
    """Record a deletion justification. All four fields must be substantive
    (non-empty after strip) — a hollow justification does not satisfy the
    gate (anti-Goodhart: empty records are rejected at the door)."""
    for label, val in (("why", why), ("investigated", investigated), ("extracted", extracted)):
        if not (val or "").strip():
            raise ValueError(
                f"deletion justification field '{label}' is empty — the gate "
                "requires what/why/investigated/extracted, substantively"
            )
    if not (target or "").strip():
        raise ValueError("deletion justification requires a non-empty target")
    ts = time.time() if now is None else now
    entry = {
        "target": target.strip(),
        "why": why.strip(),
        "investigated": investigated.strip(),
        "extracted": extracted.strip(),
        "ts": ts,
    }
    entries = [e for e in _load() if ts - e.get("ts", 0) < _TTL_SECONDS]
    entries.append(entry)
    _save(entries)
    return entry


def has_fresh_justification(command: str, now: float | None = None) -> bool:
    """True if a fresh (within TTL) justification whose target appears in the
    command exists. Per-deletion matching: justifying branch X does not clear
    deleting branch Y."""
    ts = time.time() if now is None else now
    cmd = (command or "").lower()
    for e in _load():
        if ts - e.get("ts", 0) >= _TTL_SECONDS:
            continue
        tgt = str(e.get("target", "")).strip().lower()
        if tgt and tgt in cmd:
            return True
    return False


def _ask_remote(args: list[str], cwd: str | None) -> tuple[bool, str]:
    """Run git against the real remote. (ok, stdout-or-error). Windowless on Windows."""
    import subprocess
    import sys

    flags = 0x08000000 if sys.platform == "win32" else 0  # CREATE_NO_WINDOW
    try:
        done = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30, creationflags=flags
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if done.returncode != 0:
        return False, (done.stderr or done.stdout).strip()[:200] or f"git exited {done.returncode}"
    return True, done.stdout


def archive_tag_problem(command: str, cwd: str | None = None) -> str | None:
    """For a remote branch delete: None if every branch's tip already has a tag on the remote, else why not.

    Dad 2026-11-10 (notes audit): removing an old remote branch is my own job, done by tagging the tip first
    so nothing becomes unreachable. A justification says why; it does not make the safety copy. This asks
    the REMOTE (not the local repo, which can hold a tag the remote lacks) which tags point at the branch
    tip. Four states kept apart: not a remote delete (None), tag found (None), no tag (reason), could not
    ask the remote (reason, never read as 'tag exists'). It never judges whether the delete is wise, and it
    proves a tag exists at the tip, not that the tag is meaningful.
    """
    scan = _sanitize_for_trigger(command)
    if not _GIT_PUSH_DELETE.search(scan):
        return None
    tail = re.split(r"[|;&\n]", scan.split("git push", 1)[1])[0]
    tokens = tail.split()
    positional = [t for t in tokens if not t.startswith("-")]
    if not positional:
        return None
    remote, names = positional[0], positional[1:]
    branches = [n[1:] if n.startswith(":") else n for n in names]
    if not branches:
        return None
    ok, tag_listing = _ask_remote(["ls-remote", "--tags", remote], cwd)
    if not ok:
        return f"could not ask the remote '{remote}' which tags exist ({tag_listing}); refusing rather than guessing."
    tagged = {line.split()[0] for line in tag_listing.splitlines() if line.strip()}
    missing: list[str] = []
    for branch in branches:
        ok, head = _ask_remote(["ls-remote", remote, f"refs/heads/{branch}"], cwd)
        if not ok:
            return f"could not ask the remote '{remote}' for the tip of '{branch}' ({head}); refusing rather than guessing."
        if not head.strip():
            continue  # no such branch on the remote: nothing to lose
        tip = head.split()[0]
        if tip not in tagged:
            missing.append(f"{branch} (tip {tip[:10]})")
    if not missing:
        return None
    return (
        "no tag on the remote points at the tip of: "
        + ", ".join(missing)
        + ". Tag it and push the tag first, "
        "e.g. git tag archive/<name> <tip> && git push <remote> archive/<name>, then delete."
    )


def block_reason(command: str, now: float | None = None, cwd: str | None = None) -> str | None:
    """The gate's verdict for a command. Returns a block message if the
    command is a destructive deletion lacking a fresh matching justification,
    else None. Code gates/records; it never decides the deletion is wise."""
    destructive, hint = is_destructive_deletion(command)
    if not destructive:
        return None
    if has_fresh_justification(command, now=now):
        tag_problem = archive_tag_problem(command, cwd=cwd)
        return (
            f"BLOCKED: remote branch delete without a safety copy: {tag_problem}"
            if tag_problem
            else None
        )
    return (
        f"BLOCKED: destructive deletion ({hint}) without a justification. "
        "Deletion discipline: never pure-delete. First read+understand WHAT "
        "and WHY, investigate for anything worth saving, extract what's needed "
        "— THEN record it and delete:\n"
        '  divineos delete-justify "<target>" --why "..." '
        '--investigated "..." --extracted "..."\n'
        "The justification is your judgment; this gate only enforces that you "
        "made it before the irreversible act."
    )


def main() -> int:
    """Entry point for the thin PreToolUse hook to call.

    Reads PreToolUse JSON from stdin, writes a deny-decision JSON to
    stdout when ``block_reason()`` returns a reason, exits 0. Fail-open
    on any unexpected error — the hook is observational and must not
    break the workflow.

    2026-06-30 Aether migration: hook script was already a thin doorbell
    in spirit; moving the stdin parsing + decision orchestration here
    finishes the pattern. Now the bash hook is ~12 lines and contains
    zero python.
    """
    import json
    import sys

    try:
        data = json.loads(sys.stdin.read() or "{}")
    except Exception:  # noqa: BLE001
        return 0
    if (data.get("tool_name") or "") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd.strip():
        return 0
    try:
        reason = block_reason(cmd)
    except Exception:  # noqa: BLE001
        return 0
    if not reason:
        return 0
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


__all__ = [
    "is_destructive_deletion",
    "main",
    "record_justification",
    "has_fresh_justification",
    "block_reason",
]
