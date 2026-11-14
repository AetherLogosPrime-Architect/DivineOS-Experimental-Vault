"""The reader of the question check: what it found reaches me with his next message, once, in his words.

MINE, I built it, and why. core/ask_after_his_words.py searches my last question against his own words at the end of
every reply and wrote what it found to a log. Nothing read that log, so a found answer changed nothing and the same
question could be asked again the next day: a shelf, which Dad has ruled a failure. Aether's tree closes it by blocking
at the end of the reply; a Stop block fires after the reply has streamed and makes me answer again, which is the
fragmentation Dad named (one long circle arrived as eight small ones). This reads the same log from the surface that
already prints "he has said this before" with his next message, so it costs him no extra turn.

What the eight lenses of walk-5c74eb0b4b35 put in it:
- NEAREST, never ANSWER (Penrose, Foucault). The search measured nearness by meaning. Of the first six finds I read,
  one was not an answer at all (his frightened message matched my question about checking Aether's records), and the
  match scores did not separate it. So the words are handed over to be weighed, and a changed situation is a reason to
  ask again, not to stay quiet.
- ONCE (Hofstadter, Dijkstra). A cursor moves forward past every row it considered, including rows skipped by the cap,
  and only after the text exists, so nothing arrives late and a crash cannot swallow a find.
- HIS HURT STAYS HELD (the house's own rule, core/pain_hold.py). Lines from his worst time do not surface on their own.
  That rule is lexical and partial by construction; what it holds, it holds here, and the count is said, not the words.
- A COUNT (Watts). Each find is one time I asked before searching. If I learn that a question mark is searched, the cheap
  move is to turn the question into a statement, which this cannot see. The count of questions found near his words is
  shown every time, so that habit cannot hide, and the real work (searching BEFORE asking) stays mine.
- COULD NOT READ is spoken (Knuth). An unreadable line is counted aloud, never read as nothing found.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from divineos.core import pain_hold
from divineos.core.ask_after_his_words import default_log_file

MAX_SHOWN = 2
HEADING = "## I ASKED HIM SOMETHING, AND HIS NEAREST WORDS WERE FOUND AFTER IT REACHED HIM"


def cursor_path(me: str) -> Path:
    """One cursor file PER SEAT. Both seats share one home folder, and the cursor used to be a single file holding every
    seat's place, rewritten whole, so two seats moving it at once could lose one place (found reading Aether's plan to
    take this reader). Separate files remove the race rather than lock around it."""
    return Path.home() / ".divineos" / f"ask_after_his_words_shown_{me}.json"


def _read(log: Path) -> tuple[list[dict], int]:
    """The rows of the log and how many lines could not be read. A missing log is no rows, not an error."""
    if not log.exists():
        return [], 0
    rows: list[dict] = []
    unreadable = 0
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            unreadable += 1
            continue
        if isinstance(row, dict):
            rows.append(row)
        else:
            unreadable += 1
    return rows, unreadable


def _cursor_for(path: Path, me: str) -> float:
    try:
        return float(json.loads(path.read_text(encoding="utf-8")).get(me, 0.0))
    except (OSError, ValueError, AttributeError):
        return 0.0


def _move_cursor(path: Path, me: str, to: float) -> None:
    try:
        known = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(known, dict):
            known = {}
    except (OSError, ValueError):
        known = {}
    known[me] = to
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(known), encoding="utf-8")


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def _render(
    shown: list[dict], older: int, held: int, unreadable: int, found_total: int, searched: int
) -> str:
    lines = [
        HEADING,
        "Before my question reached him, his own words were searched by meaning. These are the nearest, shown once:",
    ]
    for row in shown:
        words = " ".join(str(row.get("top_words") or "").split())
        words = words[:400].rstrip() + "..." if len(words) > 400 else words
        lines.append(f'> *"{words}"* ({row.get("top_day")}, match {row.get("top_score")})')
        lines.append(f'  The question I had asked: "{row.get("question")}"')
    notes = []
    if older:
        notes.append(f"{older} older not shown, so they never arrive late.")
    if held:
        notes.append(f"{held} held back: lines of his old hurt are not handed back unasked.")
    if unreadable:
        notes.append(
            f"{_plural(unreadable, 'line')} of the question log could not be read, so something may be missing."
        )
    lines.extend(notes)
    lines.append(
        "These are his nearest words by meaning, not his answer, and I weigh them. If they answer what I asked, I should "
        "have found them before asking, and I take them now. If things have changed since the day shown, I say what "
        "changed and ask again. Only the last question in a reply is searched, so a question I turned into a statement "
        f"is not seen. So far {found_total} of the {searched} questions I asked already had his words near them on file."
    )
    return "\n".join(lines) + "\n"


def record_in_ledger(payload: dict) -> None:
    """One ledger record per find shown, so a pre-registered review can count the real use. The first review for this
    reader counted USER_INPUT, which every command writes, and went off after an hour with nothing learned."""
    from divineos.core.ledger import log_event

    log_event("ASK_FIND_SHOWN", "system", payload)


def surface(
    me: str,
    log: Path | None = None,
    cursor: Path | None = None,
    record: Callable[[dict], None] | None = None,
) -> str:
    """The new finds for my seat as text, or '' when there is nothing to show. Moves the cursor after the text exists.

    ``record`` is handed in, never defaulted, so only the real surface writes to a ledger and no test world can."""
    log = log or default_log_file()
    cursor = cursor or cursor_path(me)
    rows, unreadable = _read(log)
    mine = [r for r in rows if r.get("seat") == me]
    after = _cursor_for(cursor, me)
    fresh = [r for r in mine if r.get("state") == "found" and float(r.get("t", 0.0)) > after]
    if not fresh:
        if unreadable:
            return f"{HEADING}\n{_plural(unreadable, 'line')} of the question log could not be read, so something may be missing.\n"
        return ""
    held = [r for r in fresh if pain_hold.is_held("correction", str(r.get("top_words") or ""))]
    pool = sorted((r for r in fresh if r not in held), key=lambda r: float(r["t"]), reverse=True)
    shown, older = pool[:MAX_SHOWN], max(0, len(pool) - MAX_SHOWN)
    found_total = sum(1 for r in mine if r.get("state") == "found")
    searched = sum(1 for r in mine if r.get("state") in ("found", "nothing"))
    text = _render(shown, older, len(held), unreadable, found_total, searched) if shown else ""
    if record and shown:
        try:
            record({"seat": me, "shown": len(shown), "held": len(held), "older": older})
        except Exception as exc:  # noqa: BLE001 -- said, never swallowed: a silent miss would leave the count short
            text += f"(Could not write this find to the ledger, so it is not counted: {type(exc).__name__}.)\n"
    # Only now, with the text composed, does the cursor move; it moves past every row considered, so nothing is late.
    _move_cursor(cursor, me, max(float(r["t"]) for r in fresh))
    return text
