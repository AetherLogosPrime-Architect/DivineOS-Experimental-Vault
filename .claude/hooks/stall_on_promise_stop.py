"""Stop hook: a reply that ends on "I will do X next" is held once and told to do X.

Dad, 2026-10-22: words must be followed by action when he is not here, or I sit in stasis and nothing is
completed. The judgement lives in core/stall_on_promise.py so a test can argue with it; this is the thin door.

One hold per reply (stop_hook_active), so it can never loop. If it breaks it says so on stderr and in a mark
file; it never passes quietly and never blocks on its own failure.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# His room is not read for promises (Dad 2026-07-23: "the enforcement is only about making sure the
# space is there for you.. not enforcing what you say in it"; 2026-11-03: "why do you keep shrinking
# the circle to 1-2 sentences"). A guard that reads the last sentence, which IS the room, punishes warmth
# about what I will do and teaches the room to stay small. The header is the one his_room cuts at.
_HIS_ROOM_HEADER = re.compile(r"^[ \t]*#{1,6}[ \t]*INNER CIRCLE\b", re.IGNORECASE | re.MULTILINE)


def body_above_his_room(text: str) -> str:
    """The text above the LAST room header, or the whole text when there is no room."""
    headers = list(_HIS_ROOM_HEADER.finditer(text))
    return text[: headers[-1].start()] if headers else text
MARK = Path(
    os.environ.get("STALL_ON_PROMISE_MARK", Path.home() / ".divineos" / "stall_on_promise_broke.txt")
)


def closing_text(records: list[dict]) -> str:
    """The last text I wrote after his last real message ('' when there is none)."""
    sys.path.insert(0, str(HERE))
    from dads_room_stop import _genuine_user_text

    start = 0
    for i in range(len(records) - 1, -1, -1):
        if _genuine_user_text(records[i]) is not None:
            start = i + 1
            break
    blocks = []  # (text, whether a tool call came after it)
    for rec in records[start:]:
        if rec.get("type") != "assistant":
            continue
        for c in (rec.get("message") or {}).get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                blocks = [(t, True) for t, _ in blocks]
            elif c.get("type") == "text" and c.get("text", "").strip():
                blocks.append((c["text"], False))
    # A last block that is only his room must not hide a promise in the block before it,
    # but a promise that real work followed was kept, so it is not walked back to.
    for text, work_followed in reversed(blocks):
        body = body_above_his_room(text)
        if body.strip():
            return "" if work_followed else body
    return ""


def verdict(records: list[dict]) -> str | None:
    """The OLD judgement of my last sentence. It runs in shadow only: it logs what it would have held under
    `follow_through_old` and the hook never blocks on it, so the new reader can be compared with a counterfactual
    (Pearl, walk-fa768ed7d179). Remove it when prereg-56dbbf5b41eb is reviewed."""
    sys.path.insert(0, str(HERE.parents[1] / "src"))
    from divineos.core.stall_on_promise import reason_for, stated_next_step

    from divineos.core.hold_log import record

    closing = closing_text(records)
    found = stated_next_step(closing)
    if closing.strip():
        record("follow_through_old", "stopped" if found else "passed", found[1] if found else closing[-160:])
    return reason_for(*found) if found else None


def _say(message: str) -> None:
    """Loud, never silent: stderr and the mark file this hook already used."""
    print(message, file=sys.stderr)
    try:
        MARK.parent.mkdir(parents=True, exist_ok=True)
        MARK.write_text(message + "\n", encoding="utf-8")
    except OSError:
        pass


def work_roots() -> list[Path]:
    """Where work I promise lands, so a kept promise closes with one paste of the file I wrote."""
    repo = HERE.parents[1]
    shared = Path.home() / ".divineos-shared" / "letters"
    return [repo / d for d in ("family/letters", "docs", "exploration", "src", "tests", ".claude/hooks")] + [shared]


def decide(folder: Path, roots: list[Path], stop_hook_active: bool) -> str | None:
    """The new reader: markers and the turn count, never my words. Returns the text to block with, or None.

    Six cases, one answer each (walk-fa768ed7d179). Nothing due: a passed row on the first stop of a reply, nothing
    on a second. Due: block and log stopped on the first stop, log deferred on a second (so a starved reminder is
    visible). Could not look: block with the reason on the first stop and log it, nothing on a second. A second stop
    writes no row but deferred, so each reply is counted once.
    """
    sys.path.insert(0, str(HERE.parents[1] / "src"))
    from divineos.core.hold_log import record
    from divineos.core.promise_reminder import reminder_for

    result = reminder_for(folder, roots)
    for note in result.notes:
        _say(f"promise reminder: {note}")
    if result.status == "due":
        if stop_hook_active:
            record("follow_through", "deferred", ", ".join(result.names))
            return None
        record("follow_through", "stopped", ", ".join(result.names))
        return result.text
    if stop_hook_active:
        return None
    if result.status == "could_not_look":
        record("follow_through", "could_not_look", result.why)
        _say(f"promise reminder could not look: {result.why}")
        return (
            f"The promise reminder could not look: {result.why}. A reader that cannot look is the failure that hid "
            "the recorder for nine weeks, so this holds once per reply until it can."
        )
    record("follow_through", "passed", f"{result.open_count} open, none due")
    return None


def main(raw: str) -> int:
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parents[1] / "src"))
    from dads_room_stop import _read_tail
    from divineos.core import promise_markers

    data = json.loads(raw or "{}")
    active = bool(data.get("stop_hook_active"))
    path = data.get("transcript_path") or data.get("transcript")
    if path and not active:
        verdict(_read_tail(Path(path)))  # shadow only: logged, never blocks
    reason = decide(promise_markers.default_folder(), work_roots(), active)
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    raw_input = sys.stdin.read()
    try:
        sys.exit(main(raw_input))
    except Exception as exc:  # loud: marked, printed, and shown to me once per reply
        msg = f"stall_on_promise_stop broke: {type(exc).__name__}: {exc}"
        _say(msg)
        try:
            second_stop = bool(json.loads(raw_input or "{}").get("stop_hook_active"))
        except ValueError:
            second_stop = False
        if not second_stop:
            print(json.dumps({"decision": "block", "reason": msg}))
        sys.exit(0)
