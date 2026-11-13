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
    closed: list[Marker] = field(default_factory=list)
    undated: list[Marker] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)
    folder_missing: bool = False


def turn_index(records: list[dict]) -> int:
    """The number of turn starts in a transcript: user records the harness stamped as a turn's opener."""
    from divineos.core.his_message import UNKNOWN, opener_kind

    return sum(1 for rec in records if opener_kind(rec) != UNKNOWN)


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
        if data.get("closed"):
            state.closed.append(marker)
            continue
        state.open.append(marker)
        if marker.turn is None:
            state.undated.append(marker)
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
