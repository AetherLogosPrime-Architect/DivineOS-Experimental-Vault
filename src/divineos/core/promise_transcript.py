"""The promise recorder reads only what was appended to the transcript since its last Stop.

MINE, and here is why. The recorder is a Stop hook with a 10-second limit, and it parsed the WHOLE transcript at every
reply to find the last assistant text and to count turn starts. At 403 MB that is 2.0 s on its own (5.2 s median for
the whole hook in its log, 2 of 40 runs past the limit), and it grows with every turn. It did not start slow: it read
a small file once and got slower one line at a time, so nothing ever showed it. What it needs is the same as what a
bookmark in a book gives: where I stopped reading, and how many turns I had counted by then.

The bookmark is a BYTE offset, read in binary, and it sits at the end of the last COMPLETE line. A text-mode position
is unreliable on Windows (CRLF, multibyte characters), and a line cut in the middle of a character must be read whole
next time, not skipped. The condition this keeps, in one sentence: the turn count from bookmark plus new bytes equals
the count a full read gives on the same bytes. A transcript that is new (different name) or shorter than the bookmark
(replaced) starts again from zero and says so. An unreadable bookmark reads as none, which costs one full read and
never a wrong count.

Not here: the other readers of whole transcripts, and the monotone turn clock across sessions (``promise_markers``).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NewTranscript:
    last_reply: str  # the last assistant text in the NEW bytes ('' when there was none)
    turns_total: int  # turn starts in this transcript so far, bookmark plus new
    reset: bool  # True when the read started again from byte zero
    bad_lines: int  # lines in the new bytes that were not readable JSON, skipped
    name: str  # the transcript's file name, kept so a different file starts again
    end_offset: int  # the byte offset after the last complete line read


def _load(bookmark_file: Path) -> dict | None:
    try:
        data = json.loads(bookmark_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("file"), str) or not isinstance(data.get("offset"), int):
        return None
    if not isinstance(data.get("turns"), int) or data["offset"] < 0 or data["turns"] < 0:
        return None
    return data


def read_new(
    transcript: Path, bookmark_file: Path, is_turn_start: Callable[[dict], bool]
) -> NewTranscript:
    """Read what was appended to ``transcript`` since the bookmark, without moving the bookmark.

    ``is_turn_start`` says whether one record opens a turn (the house's own test, passed in so this module does not
    own it). Moving the bookmark is ``commit``'s job, so a caller that fails before it has used the result does not
    lose the bytes.
    """
    size = transcript.stat().st_size
    mark = _load(bookmark_file)
    if mark is None or mark["file"] != transcript.name or mark["offset"] > size:
        reset, offset, turns = True, 0, 0
    else:
        reset, offset, turns = False, mark["offset"], mark["turns"]
    with transcript.open("rb") as handle:
        handle.seek(offset)
        data = handle.read(size - offset)
    complete = data[: data.rfind(b"\n") + 1]  # a line still being written is left for the next read
    last_reply, bad_lines = "", 0
    for raw in complete.split(b"\n"):
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            bad_lines += 1
            continue
        if not isinstance(rec, dict):
            bad_lines += 1
            continue
        if is_turn_start(rec):
            turns += 1
        msg = rec.get("message", {})
        if not isinstance(msg, dict) or msg.get("role") != "assistant":
            continue
        content = msg.get("content", [])
        if isinstance(content, list):
            parts = [
                c.get("text", "")
                for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            ]
            if parts:
                last_reply = "\n".join(parts)
        elif isinstance(content, str):
            last_reply = content
    return NewTranscript(
        last_reply=last_reply,
        turns_total=turns,
        reset=reset,
        bad_lines=bad_lines,
        name=transcript.name,
        end_offset=offset + len(complete),
    )


def commit(result: NewTranscript, bookmark_file: Path) -> None:
    """Move the bookmark to where ``result`` stopped reading. Whole-or-nothing: a temp file is swapped in."""
    bookmark_file.parent.mkdir(parents=True, exist_ok=True)
    temp = bookmark_file.with_name(bookmark_file.name + ".tmp")
    temp.write_text(
        json.dumps({"file": result.name, "offset": result.end_offset, "turns": result.turns_total}),
        encoding="utf-8",
    )
    temp.replace(bookmark_file)
