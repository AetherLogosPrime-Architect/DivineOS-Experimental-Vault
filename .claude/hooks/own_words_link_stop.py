"""Stop hook: when a reply ends, search MY words against the memory link and hand back what bears on them.

Dad, 2026-11-06 and 2026-11-10: the link must fire off our own words, "otherwise its not memory its just a
RAG with tags." The logic lives in core/own_words_stop.py so a test can argue with it; this is the thin door.

One hand-back per reply (stop_hook_active), and each memory is handed back once per session, so it cannot
loop. If it breaks it says so on stderr; it never passes quietly and never blocks on its own failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(HERE.parents[1] / "src"))
    from dads_room_stop import _genuine_user_text, _read_tail

    from divineos.core.own_words_stop import hand_back, leave_for_next_message, my_words

    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active") or data.get("agent_id"):
        return 0
    path = data.get("transcript_path") or data.get("transcript")
    if not path:
        return 0
    text = my_words(_read_tail(Path(path)), _genuine_user_text)
    if not text:
        return 0
    from divineos.core.ask_after_his_words import check as ask_check

    # LOG-ONLY at Stop (Dad 2026-11-10 night: one long circle arrived as eight small ones; Aether's letter:
    # every Stop hold makes me answer again). A Stop hold fires AFTER the reply has streamed, so blocking here
    # catches nothing earlier than his next message would, and each block costs him another fragment. Both
    # searches still run and log (own_words_log, ask_after_his_words_log) so misses and the floor stay
    # measurable; the next-message surface (Aether builds it in dads_table.py) reads those rows and prints
    # them with his next message. Never blocks. A failure to look is still said on stderr.
    #
    # THE OWN-WORDS FIND IS NOW LEFT FOR THE NEXT PROMPT (carried from Aether's e88428529, 2026-11-14): this door
    # used to log and say nothing, so a find was marked shown and never printed. The memory-link surface prints
    # what is left here once, with his next message. The ASK note is NOT left: it already has its own reader
    # (ask_finds_surface, from the ask log), and a second channel would show the same find twice.
    session = str(data.get("session_id") or "no-session")
    state, message = hand_back(text, session)
    ask_state, ask_message = ask_check(text)
    if state == "could-not-look":
        print(f"  [own-words link] COULD NOT LOOK: {message}", file=sys.stderr)
    elif state == "found" and message:
        try:
            leave_for_next_message(session, message)
        except Exception as exc:  # loud, and it never blocks the reply
            print(
                f"  [own-words link] COULD NOT LEAVE FOR NEXT MESSAGE: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
    if ask_state == "could-not-look":
        print(f"  [ask-after-his-words] COULD NOT LOOK: {ask_message}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # loud, never silent
        print(f"own_words_link_stop broke: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(0)
