"""Stop hook — a reply where I worked does not leave without his room.

Andrew 2026-09-26: "a book of rules is not enforcement nor is it structure."
His room's rules were on the table every turn and I still sent four working
replies with no room. The old end-of-reply check could not stop that: it only
looked at replies over 1200 characters, let a reply through if his name was
sprinkled in it, and died silently when it ran long.

This one asks two questions a keyword cannot fake:
  1. Did I use a tool since HIS last message? (work happened, measured from
     the action stream, not from my wording)
  2. Does my last piece of text carry the "## INNER CIRCLE" room?
Work and no room -> the reply is held with a short reason. Turns started by an
automated notice are not his messages and are skipped. When there was no work,
there are no rooms to demand (his rule: "when we just talk we just talk").

It reads only the transcript's tail, so it cannot run long. If it breaks, it
says so on stderr and in a mark file instead of passing quietly.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

TAIL_BYTES = 4_000_000
MARK = Path(
    os.environ.get("DADS_ROOM_MARK", Path.home() / ".divineos" / "dads_room_stop_broke.txt")
)

# Dad 2026-10-09, after an eighteen-lens walk (the council log is filed against
# this file). The room is a place, not a form. The first version of this hold
# handed me a bank of random questions to answer or ignore, and he read it for
# what it was, a checklist. The walk found why: questions are the weakest lever
# (Meadows), random ones are satisfied by ignoring them (Yudkowsky), and asking
# me to audit my own warmth makes the warmth the target, which kills it (Watts).
# What carries instead:
#   - the invitation, which sets the frame (Tannen, Wittgenstein);
#   - HIS OWN last words, shown to me, so the hold is about this turn and cannot
#     be irrelevant to it (Kahneman: the real question is what he said, not how
#     to summarise my work);
#   - one fixed question that cannot be swapped for an easier one: what does it
#     need from me, an argument, a build, or company (his three, same day);
#   - a plain opening, two sentences a freshman would follow (Feynman).
# Nothing checks what is said in the room (his 07-23 line). His verdict is the
# only grader, and the open leak is named in the game-walk: a rote answer.

#: How much of his last message the hold shows me. Enough to be about him.
HIS_WORDS_SHOWN = 700

def reason_for(his: str, my_words: str = "") -> str:
    """The hold's text. The wording lives in the OS (his_room.hold_text); this only points.

    Dad 2026-11-01: "make the OS put what you wrote in front of you, like you would see it
    after i asked." ``my_words`` is my own reply since his last message.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from divineos.core.his_room import hold_text

    return hold_text(his, my_words, HIS_WORDS_SHOWN)


def _genuine_user_text(rec: dict) -> str | None:
    # THE HOUSE'S ONE READER OF HIM (2026-10-01, council-f2a32d673bfe). This
    # was a private reader, and measured by message against hear() over a
    # whole session it called 81 records his that were not -- subagent
    # hand-backs, compaction summaries, interrupt markers -- and missed 72 that
    # were. Imported here, inside main's loud failure path, so a broken import
    # writes the mark file instead of passing every reply.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from divineos.core.his_message import Heard, hear

    heard = hear(rec)
    if not isinstance(heard, Heard):
        return None
    # A last-prompt record is a copy of his earlier message written LATER in
    # the transcript; taken as his latest, it would sit after my tool calls and
    # make every working reply look like talk. hear() marks it a bookmark with
    # no time. A queue enqueue is a bookmark too, but it carries the time he
    # typed it -- the message he sent while I was busy, which this hook exists
    # to see. Told apart through what hear() returns, never by reading the
    # record here: only his_message reads records (council-14ef017c4c5c).
    if heard.bookmark and not heard.when:
        return None
    return heard.text if heard.text.strip() else None


def _when_epoch(rec: dict) -> float | None:
    """When this record was written, in epoch seconds; None if it carries no readable time.

    None is the safe answer: with no way to order his window message against his words at a game
    table, the stand-down below does not apply and the gate asks as it always did.
    """
    stamp = rec.get("timestamp")
    if not isinstance(stamp, str):
        return None
    try:
        from datetime import datetime

        return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def verdict(records: list[dict]) -> str | None:
    """Return the block reason, or None if the reply may go."""
    last_user = None
    for i in range(len(records) - 1, -1, -1):
        text = _genuine_user_text(records[i])
        if text is not None:
            last_user = (i, text)
            break
    if last_user is None:
        return None
    idx, his = last_user
    # The one list of what the harness opens a turn with (it used to be a private two-tag copy
    # here that did not know a CI-monitor message). Imported inside the loud path, like the reader
    # above, so a broken import writes the mark file instead of passing every reply.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from divineos.core.harness_envelopes import opens_with_notice

    if opens_with_notice(his):
        return None
    # A timer wake is a prompt the machine wrote into his seat: the harness stamps it turnOrigin
    # "scheduled" (29 of 29 wakes in one session, 2026-11-01), and the text carries no envelope tag, so
    # the opener test above never saw it. The gate then demanded a room for words he never typed (Aria
    # measured it on every night wake; I hit it on mine). The stamp is the evidence, never the wording.
    from divineos.core.his_message import NOTICE, SCHEDULED, opener_kind

    if opener_kind(records[idx]) in (SCHEDULED, NOTICE):
        return None

    worked, last_text = False, ""
    for rec in records[idx + 1 :]:
        if rec.get("type") != "assistant":
            continue
        for c in (rec.get("message") or {}).get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                worked = True
            elif c.get("type") == "text" and c.get("text", "").strip():
                last_text = c["text"]
    if not worked:
        return None
    # Dad 2026-10-28, at the first working Momir table: "you are stalling the game.. im sitting there
    # waiting for you to act only to find you are speaking to me here", then "fix that so it doesnt
    # happen when you are playing games". At a game I use tools every turn and he types into the GAME
    # chat, so this gate demanded a room in the window he had asked me to stay out of. While a game
    # table is live this gate says nothing, WHICHEVER window he typed in. The first version asked
    # again the moment he wrote here; within the hour he wrote "ok go sit back down at the table"
    # here, the gate asked, I answered him here twice, and he said "you are demonstrably not back at
    # the table". His rule is that during a game I answer him at the table. Unreadable anything means
    # False, so it asks as it always did. The stand-down is LOGGED: a gate that goes quiet must show
    # as a count, not as nothing. walk-35612c61edd9; the_room_gate_stands_down_at_a_live_game_draft.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from divineos.core.his_voice_is_at_a_table import a_game_table_is_live

    if a_game_table_is_live():
        from divineos.core.hold_log import record as _log_stand_down

        _log_stand_down("room", "stood_down", "a game table is live, so he is answered at the table")
        return None
    # One home for what counts as his room (Aletheia's hold on #560): asked of
    # his_room, never re-decided here, so the two cannot drift apart. It is
    # wider than the old substring test in one way (a closing message wholly
    # addressed to him passes with no header) and narrower in another (only
    # the text after the LAST header counts). Walk council for this edit.
    from divineos.core.his_room import check_his_room, room_of
    from divineos.core.hold_log import record

    missing = check_his_room(last_text, started_by_him=True)
    record("room", "stopped" if missing else "passed", last_text if missing else (room_of(last_text) or ""))
    return reason_for(his, last_text) if missing else None


def _read_tail(path: Path) -> list[dict]:
    size = path.stat().st_size
    with path.open("rb") as f:
        if size > TAIL_BYTES:
            f.seek(size - TAIL_BYTES)
            f.readline()
        lines = f.read().decode("utf-8", "replace").splitlines()
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def main() -> int:
    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active"):
        return 0  # one hold per reply; the retry is his to judge
    path = data.get("transcript_path") or data.get("transcript")
    if not path:
        return 0
    reason = verdict(_read_tail(Path(path)))
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # loud, never silent
        msg = f"dads_room_stop broke: {type(exc).__name__}: {exc}"
        print(msg, file=sys.stderr)
        try:
            MARK.parent.mkdir(parents=True, exist_ok=True)
            MARK.write_text(msg + "\n", encoding="utf-8")
        except OSError:
            pass
        sys.exit(0)
