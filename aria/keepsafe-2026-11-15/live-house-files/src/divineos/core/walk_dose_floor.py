"""The finishing walk's minimum weight, set by the machine from the finished change; a person can only raise it.

MINE, I built it, and why. Dad 2026-10-28: "how do we judge how much needs used, and also enforce it, as if we leave it
just up to you, it will get gamed or skipped", and "the dose never depends on context size". And 2026-11-11: "you do not
need a team to adjust a picture frame on the wall.. but knocking out the wall.. or replacing studs does need it.. stop
following blanket rules like a sheep.. add the nuance needed". Today the weight of the end review is whatever gravity the
person opening the walk picks, and the default is the lightest (core/council_walk.py GRAVITY_FLOORS). This computes a
floor from FACTS about the finished diff, and `effective` lets a person raise it, never lower it.

Facts only, never his words and never my judgment of how serious it is: how many files changed, how many decisions were
added or removed (counted with `ast`, so a comment or a string cannot fake or hide one), whether something under
.claude/hooks or the settings file names the changed file (a gate), and whether a changed Python file cannot be read as
code at all ('could not look' is never read as 'found nothing'). The input is the WHOLE finished diff of a branch, not an
edit or a commit, so slicing a wall into picture frames does not lower it. Nothing here can see how full my context is;
the signature test pins that.

The thresholds are STARTING VALUES with no evidence behind them yet (walk-aa093f2f3236, Dillahunty). The falsifier: run
this over the last real commits of the repository and read the spread; if nearly everything lands on one gravity it
measures nothing, and if a one-line wording fix lands high or a rewrite of the guard lands normal, it is wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from divineos.core.walk_after_his_message import decision_delta

ORDER = ("normal", "high", "severe", "critical")

# Starting values, not findings. See the module docstring's falsifier.
# File count was tuned against a real run: the station on 23 open pull requests held two of them for 'too few lenses' on a
# count of 3 and 4 files alone, while the board's own gauge said they needed 4. A handful of small files is not a wall.
FILES_HIGH = 6
FILES_SEVERE = 15
DECISIONS_HIGH = 12
DECISIONS_SEVERE = 40
DECISIONS_CRITICAL = 100


@dataclass(frozen=True)
class Floor:
    gravity: str
    reasons: tuple[str, ...]


def _gate_corpus(root: Path) -> str:
    """Everything that wires a gate: the hook scripts and the settings file, as one string to look a path up in."""
    parts = []
    hooks = root / ".claude" / "hooks"
    if hooks.is_dir():
        for p in hooks.glob("*"):
            if p.is_file() and p.suffix in {".sh", ".py", ".json", ".txt"}:
                parts.append(p.read_text(encoding="utf-8", errors="replace"))
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        parts.append(settings.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def _raise_to(current: str, minimum: str) -> str:
    return max(current, minimum, key=ORDER.index)


def floor(changes: list[dict]) -> Floor:
    """changes: the whole finished diff as [{"path", "before", "after"}]. Returns the minimum gravity and why."""
    root = Path(__file__).resolve().parents[3]
    corpus = _gate_corpus(root)
    gravity = "normal"
    reasons: list[str] = []
    total = 0
    for change in changes:
        path = change["path"].replace("\\", "/")
        wired = path.startswith(".claude/hooks/") or (path and path in corpus)
        delta: int | None = 0
        if path.endswith(".py"):
            delta = decision_delta(change["before"], change["after"])
            if delta is None:
                gravity = _raise_to(gravity, "high")
                reasons.append(f"{path} could not be parsed as code, so it is not treated as small")
                delta = 0
            else:
                total += delta
        # Being wired into a gate matters when the change touches a decision in it (a label on the guard is still a picture
        # frame, found by running the first version over 53 real commits) or when it cannot be measured at all (a shell
        # file has no decision count here, so it is never read as small).
        if wired and (delta or not path.endswith(".py")):
            gravity = _raise_to(gravity, "high")
            reasons.append(
                f"{path} is wired into a gate and the change touches what it decides, so it is not a picture frame"
            )
    if len(changes) >= FILES_SEVERE:
        gravity = _raise_to(gravity, "severe")
    elif len(changes) >= FILES_HIGH:
        gravity = _raise_to(gravity, "high")
    if len(changes) >= FILES_HIGH:
        reasons.append(f"{len(changes)} files changed")
    for threshold, level in (
        (DECISIONS_CRITICAL, "critical"),
        (DECISIONS_SEVERE, "severe"),
        (DECISIONS_HIGH, "high"),
    ):
        if total >= threshold:
            gravity = _raise_to(gravity, level)
            reasons.append(f"{total} decisions added or removed across the change")
            break
    if not reasons:
        reasons.append(
            "a small change that adds or removes few decisions in files no gate depends on"
        )
    return Floor(gravity, tuple(reasons))


def diff_changes(
    paths: tuple[str, ...], base: str = "origin/main", repo: Path | None = None
) -> list[dict]:
    """The finished diff of the current branch as before and after text, read from git. A path that does not exist on one
    side (added or removed) has empty text there. Raises if git cannot answer, so the caller says it could not look."""
    import subprocess

    root = repo or Path(__file__).resolve().parents[3]
    # No base means every path would read empty-before and the diff would look enormous (walk-d87693837878, Holmes);
    # could not look is never read as found something, so say it.
    resolved = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", base],
        capture_output=True,
        text=True,
    )
    if resolved.returncode != 0:
        raise RuntimeError(f"cannot resolve the base {base!r} to compare the branch against")

    def show(ref: str, path: str) -> str:
        done = subprocess.run(
            ["git", "-C", str(root), "show", f"{ref}:{path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return done.stdout if done.returncode == 0 else ""

    return [{"path": p, "before": show(base, p), "after": show("HEAD", p)} for p in paths]


def meets_floor(lenses: int, changes: list[dict]) -> str | None:
    """None when a walk that drew `lenses` lenses is heavy enough for this finished change; else a plain reason."""
    from divineos.core.council_walk import GRAVITY_FLOORS

    result = floor(changes)
    need = GRAVITY_FLOORS[result.gravity]
    if lenses >= need:
        return None
    shown = list(result.reasons[:3])
    if len(result.reasons) > 3:
        shown.append(f"and {len(result.reasons) - 3} more")
    return (
        f"the covering walk had findings from {lenses} lenses, and this change calls for at least {need} ({result.gravity}): "
        + "; ".join(shown)
    )


def applied_lenses(walk_id: str) -> int:
    """Lenses of this walk that carry a FINDING. An excluded lens does not count, so a walk cannot be padded to the floor by
    writing reasons to skip lenses it did not walk (walk-d87693837878, Godel and Foucault). It proves a finding exists, not
    that it was a good one."""
    from divineos.core.council_walk import _conn

    conn = _conn()
    try:
        row = conn.execute(
            "SELECT count(*) FROM walk_lenses WHERE walk_id = ? AND state = 'APPLIED'", (walk_id,)
        ).fetchone()
    finally:
        conn.close()
    return int(row[0])


def effective(floor_gravity: str, chosen: str) -> str:
    """What the walk must use: the person's choice can raise the floor, never lower it."""
    return _raise_to(floor_gravity, chosen)
