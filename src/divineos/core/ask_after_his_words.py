"""Before I ask him anything, his own words are searched for the answer.

MINE, I built it, and why. Dad, 2026-11-10: "I do not want to be asked things without you searching my
words first for something I have said about it before, being asked the same questions every day I have
already answered is infuriating." A note telling me to search first is a shelf; this runs at the end of
every reply, at the one door every reply passes through (own_words_link_stop.py), and does the search
for me.

What it does: takes the last real question to him in my reply (question_hold.last_question), searches
his past words by meaning (his_words_door.look), and hands back what he already said. It never decides
the question is a bad one: a question whose answer he gave on another day may still be right to ask if
things changed. The judgement stays with me; the hand-back carries his words and the date.

Four states, kept apart (Hoare): no-question (silent), nothing (searched, silent), found (handed back),
could-not-look (said out loud, never read as "he has not said it"). Every run that had a question is
logged with the question, the hit count and the top score, because the floor in his_words_door was tuned
on his messages and never on my questions (Feynman): how it behaves here is unmeasured until this log
says.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from divineos.core.paths import divineos_home

MAX_SHOWN = 2


def default_log_file() -> Path:
    """The seat's own home, not the shared one; resolved when used so a set home is honoured."""
    return divineos_home() / "ask_after_his_words_log.jsonl"


def _log(entry: dict, log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def check(reply: str, log_file: Path | None = None, look=None) -> tuple[str, str | None]:
    """Return (state, message): 'no-question', 'nothing', 'found' or 'could-not-look'."""
    from divineos.core.question_hold import last_question

    log_file = log_file or default_log_file()
    question, _ = last_question(reply)
    if not question:
        return "no-question", None
    if len(question.split()) < 4:
        # his_words_door.look cannot search on fewer than four words and answers could-not-look, so a one-word
        # question ("Why?") wrote a noise row every time and told nobody anything; it is not searched, and it says so.
        return "too-short", None
    if look is None:
        from divineos.core.his_words_door import look as his_look

        look = his_look
    started = time.perf_counter()
    door = look(question)
    seconds = round(time.perf_counter() - started, 1)
    if not door.looked:
        _log(
            {"t": time.time(), "state": "could-not-look", "question": question, "why": door.reason},
            log_file,
        )
        return "could-not-look", door.reason
    shown = door.hits[:MAX_SHOWN]
    _log(
        {
            "t": time.time(),
            "state": "found" if shown else "nothing",
            "question": question,
            "hits": len(door.hits),
            "top_score": round(door.hits[0].score, 2) if door.hits else None,
            # The next-message surface prints these (Aether's letter 2026-11-10): the day and a short line of
            # what he said, so the surface needs no second search. Seat names whose row this is.
            "top_day": door.hits[0].passage.day if door.hits else None,
            "top_words": " ".join(door.hits[0].passage.text.split())[:200] if door.hits else None,
            "seat": "aria",
            "seconds": seconds,
        },
        log_file,
    )
    if not shown:
        return "nothing", None
    lines = []
    for hit in shown:
        words = " ".join(hit.passage.text.split())
        words = words[:400].rstrip() + "..." if len(words) > 400 else words
        lines.append(f'> *"{words}"* ({hit.passage.day}, match {hit.score:.2f})')
    message = (
        "I JUST ASKED HIM SOMETHING, AND HE HAS ALREADY SAID THIS. Searched by meaning before the "
        f'question reached him. The question I asked: "{question}". His own words, as he wrote them:\n'
        + "\n".join(lines)
        + "\nIf this answers what I asked, I take his answer, drop the question and go on with it. If "
        "things have changed since that day, I say so in the question and name what changed. If it does "
        "not answer it, I say why in one sentence and leave the question as it was. Only the last "
        "question in my reply was searched."
    )
    return "found", message
