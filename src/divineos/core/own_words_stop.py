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
from divineos.core.paths import divineos_home

# The embedder keeps its first 256 tokens, about this many characters. A long reply is searched in two
# windows (its start and its end) so a reply that turns halfway still gets heard.
MIN_REPLY_WORDS = max(MIN_SIGNAL_WORDS, 25)
WINDOW_CHARS = 1000
MAX_ITEMS = 3


# The seat's OWN data home, not the shared ~/.divineos: both seats run as one Windows user, so a hardcoded
# Path.home() put both in one file (Aria 2026-11-14: divineos_home() resolves each seat to its own folder).
def default_state_file() -> Path:
    return divineos_home() / "own_words_shown.json"


def default_log_file() -> Path:
    return divineos_home() / "own_words_log.jsonl"


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


SESSION_KEEP_SECONDS = 24 * 3600


def _read_state(state_file: Path) -> dict:
    """An unreadable file reads as empty: that fails toward repeating memories, never toward silence."""
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _load_shown(session_id: str, state_file: Path) -> set[str]:
    entry = _read_state(state_file).get(session_id)
    if isinstance(entry, dict):  # current format: {"keys": [...], "t": last save}
        entry = entry.get("keys", [])
    return set(entry) if isinstance(entry, list) else set()  # a plain list is the old format


def _save_shown(
    session_id: str, shown: set[str], state_file: Path, now: float | None = None
) -> None:
    """Keep EVERY live session's list, not just this one.

    Both seats run as the same Windows user and share ~/.divineos, so the old one-session-at-a-time
    write erased the other seat's list on every save (found 2026-11-14: only the other seat's session
    was in the file) and the same memories were handed back again and again. A session idle for more
    than a day is dropped; a quiet one inside the day is kept. An entry with no time (old format) is
    stamped now when first seen, so it ages out like any other. The write goes to a temp file and is
    swapped in, so a torn write cannot corrupt both seats. Two saves in the same instant can still
    lose one update; that race is accepted and named here rather than hidden.
    """
    now = time.time() if now is None else now
    state_file.parent.mkdir(parents=True, exist_ok=True)
    kept: dict = {}
    for sid, entry in _read_state(state_file).items():
        if sid == session_id:
            continue
        if isinstance(entry, list):
            entry = {"keys": entry, "t": now}
        if isinstance(entry, dict):
            stamped = {"keys": entry.get("keys", []), "t": entry.get("t", now)}
            if now - float(stamped["t"]) <= SESSION_KEEP_SECONDS:
                kept[sid] = stamped
    kept[session_id] = {"keys": sorted(shown), "t": now}
    temp = state_file.with_name(state_file.name + ".tmp")
    temp.write_text(json.dumps(kept), encoding="utf-8")
    temp.replace(state_file)


def _log(entry: dict, log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def hand_back(
    text: str,
    session_id: str,
    state_file: Path | None = None,
    log_file: Path | None = None,
    retrieve=None,
) -> tuple[str, str | None]:
    """Return (state, message). state is 'found', 'nothing', 'skipped' or 'could-not-look'."""
    state_file = state_file or default_state_file()
    log_file = log_file or default_log_file()
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
