"""Promise markers: counted in turns, closed by one explicit line, read in honest states.

Dad, 2026-11-13: the follow-through check "comes too early, right after you say it". Record the promise, give me
a chance to do it, and if after about five turns nothing has been done about it, remind me and block until I do.
The recorder (`.claude/hooks/promise-reach-detector.sh`) already writes one marker file per detected promise;
this module is the one definition of what a marker's age is, how it closes, and how the folder reads, so the
recorder, a CLI and the blocker cannot disagree. Two walks shaped it (walk-82220bd46c30, walk-6e90bce7c85e):

- AGE IS TURN STARTS, never minutes. A turn start is a user record the harness stamped as human, scheduled or
  task-notification (read through `his_message.opener_kind`, never by words). In the night he sends no
  messages, so counting his messages would never age a promise.
- A MARKER CLOSES ONLY BY ONE EXPLICIT LINE: `done` (a file that exists and was written AFTER the promise was
  recorded, since any file exists), or `false-alarm` (a reason of real length). `waiting-on` does not close:
  a promise that waits on someone must not vanish behind a name, so it re-dates the marker to now and records
  who. Nothing is guessed from tool calls.
- NOTHING IS DELETED. A close is written into the marker, and every close is appended to `closes.jsonl`, so a run
  of cheap closes shows as a rate someone other than me can read.
- READING THE FOLDER HAS A FIFTH ANSWER. Open, closed, and could-not-look (a missing folder, a corrupt marker)
  are kept apart; an empty folder is honestly empty and is not could-not-look.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: How many turn starts a promise may stay open before it is due.
DUE_AFTER_TURNS = 5

#: A false-alarm reason must be at least this long, so "nope" cannot close a promise.
MIN_REASON_CHARS = 20

KINDS = ("done", "waiting-on", "false-alarm")


class CloseRefused(Exception):
    """A close was not accepted; the message says exactly what is missing."""


@dataclass
class Marker:
    name: str
    data: dict[str, Any]

    @property
    def turn(self) -> int | None:
        value = self.data.get("turn_index")
        return value if isinstance(value, int) and not isinstance(value, bool) else None


@dataclass
class FolderState:
    open: list[Marker] = field(default_factory=list)
    closed_names: list[str] = field(default_factory=list)
    undated: list[Marker] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)
    folder_missing: bool = False


def turn_index(records: list[dict]) -> int:
    """The number of turn starts in a transcript: user records the harness stamped as a turn's opener."""
    from divineos.core.his_message import UNKNOWN, opener_kind

    return sum(1 for rec in records if opener_kind(rec) != UNKNOWN)


def default_folder() -> Path:
    """The marker folder for this seat: its own data home, as the house's resolver names it (`divineos_home`).

    It used to be chosen by which directories exist on the machine (the aria home when it existed), so on a machine
    with both homes a second seat would have written its promises into the first seat's folder and advanced one
    shared turn count (Aether's cold read, walk-eb4440341013). The home is a fact about the SEAT: env override, then
    the checkout's own `.divineos_data_home` marker. Nothing here looks at what else exists.
    """
    from divineos.core.paths import divineos_home

    return divineos_home() / "promise_markers"


def checked_folder(checkout: Path) -> Path:
    """`default_folder()`, but only when the divineos in use lives under `checkout`.

    The wrong tree answers for another seat (a bare `python` can import the other checkout), so the recorder asks
    through this and, when it raises, writes nothing: the failure keeps the invariant that a seat's promises live in
    that seat's own home (Wayne).

    WHAT IT CHECKS, and no more (Aether's cold read): that `checkout` is an ANCESTOR of the imported `divineos`. It
    refuses a harmless case (a working folder below the root, such as `docs`) and passes a meaningless one (a folder
    above every checkout, such as `C:\\`), so it is weaker than its job. It holds in daily use only because the
    recorder runs `cd "$REPO_ROOT"` before it asks, so `checkout` is always the checkout's root. The stronger
    question is whether the divineos in use lives in the checkout the hook script itself sits in; that needs a path
    from bash that Windows Python reads correctly, and is an open follow-up, not something this docstring claims.
    """
    import divineos

    running = Path(divineos.__file__).resolve()
    if checkout.resolve() not in running.parents:
        raise RuntimeError(
            f"divineos was imported from {running}, not from {checkout}; its promises would go to another seat's home"
        )
    return default_folder()


def _clock_state(folder: Path) -> dict[str, Any] | None:
    """The clock file as it stands: a dict, {} when there is none yet, None when it exists but cannot be read."""
    path = folder / "turn_now.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def advance_turn_now(folder: Path, session: str, session_turns: int) -> int:
    """Move the one running count of turn starts forward and return it.

    A transcript restarts at zero in every new session, so a plain count would put yesterday's promise in the
    future of today's turn 3 and it would never fall due (walk-80ebe4590204). This keeps one monotone count
    across sessions: for the same session only the NEW turn starts are added, for a new session all of its
    starts are. The count never runs backwards (a later, smaller count from unreadable lines changes nothing).
    The write is whole-or-nothing. If the file exists but cannot be read the clock is not guessed: this raises.
    """
    state = _clock_state(folder)
    if state is None:
        raise ValueError(
            f"turn_now.json in {folder} exists but cannot be read; the clock is not guessed"
        )
    raw_total = state.get("global")
    total: int = raw_total if isinstance(raw_total, int) else 0
    if state.get("session") == session:
        raw_seen = state.get("session_turns")
        seen: int = raw_seen if isinstance(raw_seen, int) else 0
        added = max(session_turns - seen, 0)
        kept = max(session_turns, seen)
    else:
        added, kept = session_turns, session_turns
    new_total = total + added
    folder.mkdir(parents=True, exist_ok=True)
    tmp = folder / "turn_now.json.tmp"
    tmp.write_text(
        json.dumps(
            {"global": new_total, "session": session, "session_turns": kept, "at": time.time()}
        ),
        encoding="utf-8",
    )
    os.replace(tmp, folder / "turn_now.json")
    return new_total


def turn_now(folder: Path) -> int | None:
    """The running turn count at the last Stop, or None when it is missing or unreadable (said, never zero)."""
    state = _clock_state(folder)
    if not state:
        return None
    value = state.get("global")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def read_folder(folder: Path) -> FolderState:
    """Read the marker folder into honest states. Never raises on a bad marker; it says so."""
    state = FolderState()
    if not folder.is_dir():
        state.folder_missing = True
        return state
    for path in sorted(folder.glob("promise_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state.unreadable.append(path.name)
            continue
        if not isinstance(data, dict):
            state.unreadable.append(path.name)
            continue
        marker = Marker(path.name, data)
        if data.get("closed"):  # a closed marker left in the live folder by an older version
            state.closed_names.append(path.name)
            continue
        state.open.append(marker)
        if marker.turn is None:
            state.undated.append(marker)
    closed_dir = folder / "closed"
    if closed_dir.is_dir():
        # Names only: the live read costs what is open, never everything ever said.
        state.closed_names.extend(sorted(p.name for p in closed_dir.glob("promise_*.json")))
        state.closed_names.sort()
    return state


def due(open_markers: list[Marker], current_turn: int) -> list[Marker]:
    """Open markers at least DUE_AFTER_TURNS turn starts old. A marker with no stored turn is never due."""
    return [
        m for m in open_markers if m.turn is not None and current_turn - m.turn >= DUE_AFTER_TURNS
    ]


def _find(folder: Path, prefix: str) -> Path:
    matches = sorted(
        p for p in folder.glob("promise_*.json") if p.stem.startswith(prefix.removesuffix(".json"))
    )
    if not matches:
        raise CloseRefused(f"no marker in {folder} starts with {prefix!r}")
    if len(matches) > 1:
        names = ", ".join(p.name for p in matches[:6])
        raise CloseRefused(
            f"more than one marker starts with {prefix!r} ({names}); give more of the name"
        )
    return matches[0]


def _log(folder: Path, row: dict[str, Any]) -> None:
    with (folder / "closes.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def close(
    folder: Path,
    prefix: str,
    kind: str,
    detail: str,
    current_turn: int | None = None,
) -> Marker:
    """Close (or, for waiting-on, re-date) one marker with one line. Raises CloseRefused with what is missing."""
    if kind not in KINDS:
        raise CloseRefused(f"kind must be one of {', '.join(KINDS)}; got {kind!r}")
    path = _find(folder, prefix)
    data = json.loads(path.read_text(encoding="utf-8"))
    promised_at = float(data.get("detected_at_ts") or 0)
    detail = (detail or "").strip()
    now = time.time()

    if kind == "done":
        deed = Path(detail)
        if not detail or not deed.is_file():
            raise CloseRefused(
                f"done needs a file that exists, written after the promise; got {detail!r}"
            )
        if deed.stat().st_mtime < promised_at:
            raise CloseRefused(
                f"done needs a file written after the promise was recorded; {deed.name} is older than it"
            )
        data["closed"] = {"kind": "done", "file": str(deed), "at": now}
    elif kind == "waiting-on":
        if not detail:
            raise CloseRefused("waiting-on needs who it is waiting on (a name)")
        if current_turn is None:
            raise CloseRefused("waiting-on re-dates the promise to now and needs the current turn")
        data["turn_index"] = current_turn
        data.setdefault("waiting_on", []).append({"who": detail, "at": now, "turn": current_turn})
    else:
        if len(detail) < MIN_REASON_CHARS:
            raise CloseRefused(
                f"a false alarm needs a reason of at least {MIN_REASON_CHARS} characters saying what was misread"
            )
        data["closed"] = {"kind": "false-alarm", "reason": detail, "at": now}

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    _log(
        folder,
        {"marker": path.name, "kind": kind, "detail": detail, "turn": current_turn, "at": now},
    )
    if data.get("closed"):
        # Moved, not deleted: the live folder then holds only what is open (Carmack, walk-80ebe4590204).
        closed_dir = folder / "closed"
        closed_dir.mkdir(exist_ok=True)
        path.replace(closed_dir / path.name)
    return Marker(path.name, data)


def close_counts(folder: Path) -> dict[str, int]:
    """How many closes of each kind the log holds (a run of cheap closes shows as a rate)."""
    counts: dict[str, int] = {}
    log = folder / "closes.jsonl"
    if not log.is_file():
        return counts
    for line in log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            kind = json.loads(line).get("kind")
        except ValueError:
            continue
        if isinstance(kind, str):
            counts[kind] = counts.get(kind, 0) + 1
    return counts
