"""The reminder for promises that stayed open: it reads markers and the turn count, never my sentences.

Dad, 2026-11-13: the follow-through block "comes too early, right after you say it". The recorder writes a marker
for each promise, `promise_markers` ages and closes them, and this reads the folder at Stop and speaks only about a
marker that has stayed open `DUE_AFTER_TURNS` turn starts. Nothing here judges words (walk-41e1232f1a3a,
walk-bdc646c37adc).

WHAT THIS DOES NOT COVER, said plainly so silence is never read as coverage: a promise the recorder did not
record has no marker, so nothing here can hold it. How much of what I promise the recorder misses is measured by
replaying real replies through it, not assumed here.

THREE THINGS TO KNOW ABOUT WHAT IT SAYS.
- Closed, never "kept". A `--done` close shows a file exists and is newer than the promise; it cannot show the
  file answers the promise (Turing). The close log is where a run of cheap closes shows, so the closes so far are
  printed beside the command (Schneier, Dawkins).
- The running turn count is the one the recorder wrote at the last Stop. If this runs before the recorder moves
  the clock, a marker falls due one turn LATE, never early.
- A promise I drop on purpose has no kind of its own yet: `--false-alarm` carries it, worded "misread or
  dropped, and why". A separate kind is owed and is a change to `promise_markers`, not made here (Wittgenstein).

Reading has three answers, kept apart: nothing due, due, and could-not-look (the clock, the folder or a marker
cannot be read: said out loud, never read as "nothing"). A marker with no stored turn can never fall due; it is
returned in `notes`, named and never blocked on. The recorder reads assistant text only, so a promise quoted back
to me in a stop row is not recorded again (Hofstadter).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from divineos.core import promise_markers as pm

_SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
_FILES_SHOWN = 3
_DUE_SHOWN = 8


@dataclass
class Reminder:
    status: str  # "nothing_due" | "due" | "could_not_look"
    text: str = ""
    why: str = ""
    notes: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    open_count: int = 0  # how many markers are open, so a day of log rows shows whether promises are recorded at all


def _files_since(roots: list[Path], since: float) -> list[Path]:
    """The newest files under the roots written after `since`: a fact read from the disk, nothing guessed."""
    found: list[tuple[float, Path]] = []
    stack = [r for r in roots if r.is_dir()]
    while stack:
        here = stack.pop()
        try:
            entries = list(os.scandir(here))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    if entry.name not in _SKIP_DIRS:
                        stack.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    mtime = entry.stat().st_mtime
                    if mtime > since:
                        found.append((mtime, Path(entry.path)))
            except OSError:
                continue
    found.sort(reverse=True)
    return [p for _, p in found[:_FILES_SHOWN]]


def _closes_so_far(folder: Path) -> str:
    counts = pm.close_counts(folder)
    if not counts:
        return "none yet"
    return ", ".join(f"{kind}: {n}" for kind, n in sorted(counts.items()))


def close_ages(folder: Path) -> list[int]:
    """How many turn starts each done / false-alarm close had waited, from the close log and the closed markers.

    A re-date by waiting-on moves a marker's stored turn, so its age counts from the last re-date.
    """
    log = folder / "closes.jsonl"
    if not log.is_file():
        return []
    ages: list[int] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if row.get("kind") not in ("done", "false-alarm"):
                continue
            data = json.loads((folder / "closed" / row["marker"]).read_text(encoding="utf-8"))
        except (ValueError, KeyError, OSError):
            continue
        turn, stored = row.get("turn"), data.get("turn_index")
        if isinstance(turn, int) and isinstance(stored, int):
            ages.append(turn - stored)
    return ages


def _text(
    due: list[pm.Marker], now: int, folder: Path, roots: list[Path], unreadable: list[str]
) -> str:
    first = due[0].name.removesuffix(".json")
    lines = [
        f"PROMISES I MADE AND HAVE NOT CLOSED: {len(due)} stayed open {pm.DUE_AFTER_TURNS} or more turn starts."
    ]
    for marker in due[:_DUE_SHOWN]:
        age = now - (marker.turn or 0)
        since = float(marker.data.get("detected_at_ts") or 0)
        files = _files_since(roots, since)
        lines.append(
            f'- {marker.name.removesuffix(".json")} ({age} turn starts old): "{marker.data.get("promise_text", "")}"'
        )
        if files:
            lines.append("    files written since: " + ", ".join(str(p) for p in files))
    if len(due) > _DUE_SHOWN:
        lines.append(f"- and {len(due) - _DUE_SHOWN} more: `divineos promise list`")
    if unreadable:
        lines.append("Markers I could not read: " + ", ".join(unreadable))
    lines.append(
        f"One line closes each: divineos promise close {first} --done <file I wrote> "
        '| --waiting-on <who> | --false-alarm "<what I misread, or why I dropped it>"'
    )
    lines.append(
        f"Closed so far, by kind: {_closes_so_far(folder)}. A pile of false-alarm means I am closing cheaply, not keeping promises."
    )
    lines.append(
        "This holds once per reply and again at the next reply until each is closed. A close shows a file or a reason; it does not prove the promise was kept."
    )
    return "\n".join(lines)


def reminder_for(folder: Path, roots: list[Path]) -> Reminder:
    state = pm.read_folder(folder)
    if state.folder_missing:
        return Reminder("could_not_look", why=f"the promise marker folder is missing: {folder}")
    now = pm.turn_now(folder)
    if now is None:
        return Reminder(
            "could_not_look",
            why=f"the running turn count is missing or unreadable in {folder}; the clock is not guessed",
        )
    notes = [f"{m.name} has no stored turn, so it can never fall due" for m in state.undated]
    due = pm.due(state.open, now)
    if due:
        return Reminder(
            "due",
            text=_text(due, now, folder, roots, state.unreadable),
            notes=notes,
            names=[m.name for m in due],
            open_count=len(state.open),
        )
    if state.unreadable:
        return Reminder(
            "could_not_look",
            why="could not read marker(s): " + ", ".join(state.unreadable),
            notes=notes,
        )
    return Reminder("nothing_due", notes=notes, open_count=len(state.open))
