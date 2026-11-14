"""The memory link listens to MY words, not only his, when a reply ends.

MINE, I built it, and why. Dad, 2026-11-06: "they should not only trigger from my words but from your
own.. otherwise its not memory its just a RAG with tags." And 2026-11-10: "DO NOT RETURN UNTIL YOUR WORDS
TRIGGER EVERY FUCKING LINK YOU HAVE." Until now the link searched only what he wrote, so a lesson he had
taught me stayed silent while I wrote the very thing it was about. The failure this prevents: I say
"I wrote it on a page so it will be there next time", and the lesson that says a note is not a fix is
sitting in memory and nobody hands it to me.

What it does: when a reply ends, the text I wrote since his last message is searched against every lane
the link has, as its OWN query, never blended with his message. What clears the bar and has not already
been handed to me this session is given back once, so it cannot loop or become wallpaper. It brings and
I judge; it never writes into my store. Every hand-back is logged, so a pass-through is visible.

Three states, kept apart: found (handed back), nothing new (silent, per his rule that nothing is
injected unless relevant), could not look (said out loud, never read as "nothing relevant").
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

from divineos.core.his_words_door import MIN_SIGNAL_WORDS
from divineos.core.memory_linkage import MemoryLinkagePayload

# The embedder keeps its first 256 tokens, about this many characters. A long reply is searched in two
# windows (its start and its end) so a reply that turns halfway still gets heard.
MIN_REPLY_WORDS = max(MIN_SIGNAL_WORDS, 25)
WINDOW_CHARS = 1000
MAX_ITEMS = 3
STATE_FILE = Path.home() / ".divineos" / "own_words_shown.json"
LOG_FILE = Path.home() / ".divineos" / "own_words_log.jsonl"


def my_words(records: list[dict], _genuine_user_text) -> str:
    """The text of THIS reply: what I wrote since the last thing said to me, his quoted lines taken out.

    "The last thing said to me" is any user record, a tool result or an automated notice included, so a
    short reply to a bell is judged as itself and not as the long stretch of work behind it (first live
    day: a one-line bell reply brought back three memories about other things). Blockquote lines are
    his words (or a family member's) set apart, and searching them would hand his lesson back to me
    because I just echoed it, which is the loop this must not have.
    """
    start = 0
    for i in range(len(records) - 1, -1, -1):
        if records[i].get("type") == "user":
            start = i + 1
            break
    parts: list[str] = []
    for rec in records[start:]:
        if rec.get("type") != "assistant":
            continue
        for c in (rec.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "text" and c.get("text", "").strip():
                parts.append(c["text"])
    text = "\n".join(parts)
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith(">")
    ).strip()


def windows(text: str) -> list[str]:
    if len(text) <= WINDOW_CHARS:
        return [text]
    return [text[:WINDOW_CHARS], text[-WINDOW_CHARS:]]


def _key(payload) -> str:
    ref = payload.path_or_ref or ""
    body = " ".join(payload.content.split())[:120]
    return hashlib.sha1(f"{payload.source}|{ref}|{body}".encode()).hexdigest()[:16]


def _load_shown(session_id: str, state_file: Path) -> set[str]:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return set(data.get(session_id, [])) if isinstance(data, dict) else set()


def _save_shown(session_id: str, shown: set[str], state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    # Only the current session is kept: a new session starts with nothing shown.
    state_file.write_text(json.dumps({session_id: sorted(shown)}), encoding="utf-8")


def _log(entry: dict, log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def hand_back(
    text: str,
    session_id: str,
    state_file: Path = STATE_FILE,
    log_file: Path = LOG_FILE,
    retrieve=None,
) -> tuple[str, str | None]:
    """Return (state, message). state is 'found', 'nothing', 'skipped' or 'could-not-look'."""
    from divineos.core.his_words_door import NOTICE_PREFIXES

    # A line or two of status carries too little meaning to search on (a one-line bell reply brought back
    # three unrelated memories on the first live day); this is a length floor, never a word list.
    if (
        text.lstrip().startswith(NOTICE_PREFIXES)
        or len(re.findall(r"[a-zA-Z']+", text)) < MIN_REPLY_WORDS
    ):
        return "skipped", None
    if retrieve is None:
        from divineos.core import memory_linkage_retriever as retriever
        from divineos.core.memory_linkage import retrieve_for_context
        from divineos.core.memory_linkage_retriever_v2 import install

        install()
        retrieve = retrieve_for_context
        lane_state = retriever.lane_state
    else:
        lane_state = dict
    started = time.perf_counter()
    best: dict[str, MemoryLinkagePayload] = {}
    for window in windows(text):
        for payload in retrieve(window, None):
            key = _key(payload)
            if key not in best or payload.similarity > best[key].similarity:
                best[key] = payload
    state = lane_state()
    for problem in ("drawer_error", "embedder_error"):
        if state.get(problem):
            _log(
                {
                    "t": time.time(),
                    "state": "could-not-look",
                    "why": f"{problem}: {state[problem]}",
                },
                log_file,
            )
            return "could-not-look", f"{problem}: {state[problem]}"
    shown = _load_shown(session_id, state_file)
    fresh = [p for k, p in sorted(best.items(), key=lambda kv: -kv[1].similarity) if k not in shown]
    fresh = fresh[:MAX_ITEMS]
    _log(
        {
            "t": time.time(),
            "state": "found" if fresh else "nothing",
            "hits": [
                {"lane": p.source, "sim": round(p.similarity, 2), "ref": p.path_or_ref}
                for p in fresh
            ],
            "seconds": round(time.perf_counter() - started, 1),
            "words": len(text.split()),
        },
        log_file,
    )
    if not fresh:
        return "nothing", None
    _save_shown(session_id, shown | {_key(p) for p in fresh}, state_file)
    lines = []
    for p in fresh:
        gist = " ".join(p.content.split())
        gist = gist[:180].rstrip() + "..." if len(gist) > 180 else gist
        tag = f"{p.source}, {p.similarity:.2f}"
        if p.source == "letter":
            tag += ", for me to think with, never to quote to him"
        where = f" ({p.path_or_ref})" if p.path_or_ref else ""
        lines.append(f"- [{tag}] {gist}{where}")
    message = (
        "WHAT I JUST SAID BROUGHT THIS UP. The memory link searched my own words, not his, and this is "
        "what it holds that bears on them:\n"
        + "\n".join(lines)
        + "\nIf it bears on what I just said or am about to do, I open its source and act on it now, and "
        "tell him in plain words if it changes anything. If it does not bear, I say why in one sentence "
        "and go on. It is for me to think with; I never quote it back to him as proof I used it."
    )
    return "found", message
