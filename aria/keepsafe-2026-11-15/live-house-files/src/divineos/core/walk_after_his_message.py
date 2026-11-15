"""An edit that adds or removes a decision owes a walk opened AFTER his latest message, and the house opens it.

MINE, I built it, and why. Dad, 2026-11-10, in his own words: "WHY THE FUCK WAS IT NOT DONE AUTOMATICALLY ...
FIND OUT WHY THE FUCK IM HAVING TO ASK YOU IN THE GODDAMN FIRST PLACE", and months earlier "why is it when i ask
for a build i get no build flow, no effort.. nothing?". The root cause, found and measured the same night: the
thing meant to put the build flow in front of me was a word-matcher that missed every real message of his, and the
door that did fire (`_walk_mark` in work_item_doorman) counted ANY walk closed since the item opened, so an older
walk about a different question satisfied an edit made for his new ask. Plan: docs/drafts/
the_build_flow_starts_from_what_is_done_to_the_house_not_from_his_words_draft_2026-11-10.md.

What this does, from FACTS and never his words: when the call edits a Python house file and the change adds or
removes a decision (counted with `ast`, so a comment or a string cannot fake or hide one), a walk is owed that names
this file, was OPENED after the latest human-stamped message in the transcript, and is closed. If none exists the
house opens one (his message as the problem, the file as scope) and says so, so the right path costs one command and
there is no cheap close to reach for (truth #11a). A turn with no human-stamped message owes nothing new.

Four states kept apart (Hoare): pass, owed, no-human-message (owes nothing, logged), could-not-check (stands aside AND
logs why, never silent). Every evaluation writes one row so the false-positive and miss rates are read from data.
"""

from __future__ import annotations

import ast
import collections
import json
import time
from datetime import datetime
from pathlib import Path
from typing import cast

LOG_FILE = Path.home() / ".divineos" / "walk_after_ask_log.jsonl"
HOUSE_PREFIXES = ("src/divineos/", ".claude/hooks/", "scripts/")
_DECISION_NODES = (
    ast.If,
    ast.While,
    ast.For,
    ast.Try,
    ast.BoolOp,
    ast.Return,
    ast.Raise,
    ast.IfExp,
    ast.ExceptHandler,
)
TAIL_BYTES = 3_000_000


def _shape(src: str) -> collections.Counter | None:
    counts: collections.Counter = collections.Counter()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        # An edit fragment is not a module: wrap it so it parses, and take the wrapper's own `if` back out.
        try:
            tree = ast.parse("if True:\n" + "\n".join("    " + line for line in src.splitlines()))
        except SyntaxError:
            return None
        counts[ast.If] -= 1
    for node in ast.walk(tree):
        if isinstance(node, _DECISION_NODES):
            counts[type(node)] += 1
    return counts


def decision_delta(before: str, after: str) -> int | None:
    """How many decisions the change adds or removes; None when either side cannot be parsed."""
    b, a = _shape(before), _shape(after)
    if b is None or a is None:
        return None
    return sum(abs(a[k] - b[k]) for k in set(a) | set(b))


def _edits_of(tool_name: str, tool_input: dict) -> list[tuple[str, str, str]]:
    """(file_path, before, after) for each edit the call makes to a file. Write compares with what is on disk."""
    path = (tool_input.get("file_path") or "").replace("\\", "/")
    if not path:
        return []
    if tool_name in ("Edit", "MultiEdit"):
        pairs = (
            [(tool_input.get("old_string") or "", tool_input.get("new_string") or "")]
            if tool_name == "Edit"
            else [
                (e.get("old_string") or "", e.get("new_string") or "")
                for e in tool_input.get("edits") or []
            ]
        )
        # WHOLE-FILE, not fragments (walk-7d58f92dd35b, Popper): 25 of the 194 real edits of the night I measured did
        # not parse as fragments, and a fragment that does not parse would have skipped this check in silence. The
        # whole module before and after parses, so apply the replacement to what is on disk and compare modules.
        try:
            before = Path(path).read_text(encoding="utf-8")
        except OSError:
            return [(path, old, new) for old, new in pairs]
        after = before
        for old, new in pairs:
            after = after.replace(old, new, 1) if old and old in after else after
        return [(path, before, after)]
    if tool_name == "Write":
        try:
            before = Path(path).read_text(encoding="utf-8")
        except OSError:
            before = ""
        return [(path, before, tool_input.get("content") or "")]
    return []


def _relative_house_path(path: str, repo_root: Path) -> str | None:
    try:
        rel = Path(path).resolve().relative_to(repo_root.resolve()).as_posix()
    except (ValueError, OSError):
        return None
    if rel.endswith(".py") and rel.startswith(HOUSE_PREFIXES):
        return rel
    return None


def latest_human_message(transcript_path: str) -> tuple[float, str] | None:
    """(time, text) of the latest record the harness stamped as typed by a human. None when there is none.

    The fact is the stamp, `origin.kind == "human"`, never what the message says (Aether measured it on this
    transcript: every typed message of his carries it; hook feedback and tool results do not).
    """
    path = Path(transcript_path)
    size = path.stat().st_size
    with path.open("rb") as fh:
        fh.seek(max(0, size - TAIL_BYTES))
        raw = fh.read().decode("utf-8", errors="replace")
    found: tuple[float, str] | None = None
    for line in raw.splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("type") != "user" or (rec.get("origin") or {}).get("kind") != "human":
            continue
        stamp = rec.get("timestamp")
        if not stamp:
            continue
        content = (rec.get("message") or {}).get("content")
        text = (
            content
            if isinstance(content, str)
            else " ".join(c.get("text", "") for c in content or [] if isinstance(c, dict))
        )
        found = (
            datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp(),
            " ".join(text.split()),
        )
    return found


def _walk_for(rel: str, since: float) -> tuple[str, str] | None:
    """('closed' | 'open', walk id) for the newest walk naming this file and opened at or after `since`."""
    from divineos.core.council_walk import _conn

    # council_walk's own connection creates the tables on first use; a raw connect to a fresh store has no `walks`
    # table and failed with "no such table" (found by the test on a real, empty store, not by reading).
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT id, scope, closed_at FROM walks WHERE opened_at >= ? ORDER BY opened_at DESC",
            (since,),
        ).fetchall()
    finally:
        conn.close()
    best: tuple[str, str] | None = None
    for walk_id, scope, closed_at in rows:
        if rel in {line.strip() for line in (scope or "").splitlines()}:
            if closed_at is not None:
                return "closed", walk_id
            best = best or ("open", walk_id)
    return best


def _log(entry: dict, log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def check(
    tool_name: str,
    tool_input: dict,
    transcript_path: str,
    repo_root: Path,
    log_file: Path = LOG_FILE,
    since: float | None = None,
) -> tuple[str, str]:
    """Return (state, message). state: 'pass', 'owed', 'no-human-message', 'could-not-check', 'not-applicable'.

    `since` is the start of the piece of work (the work item's window). When the door has one, the walk must name the file
    and have been opened since THEN, not since his latest message: Dad 2026-11-11, "a picture frame is not a wall", and his
    own 2026-10-28 shape (the review at the two ends of a build, the middle never gated). Without it the floor is his latest
    human-stamped message, so the first knock of a new piece of work is still held."""
    decided = []
    for path, before, after in _edits_of(tool_name, tool_input):
        rel = _relative_house_path(path, repo_root)
        if rel is None:
            continue
        delta = decision_delta(before, after)
        if delta:
            decided.append((rel, delta))
    if not decided:
        return "not-applicable", ""
    rel, delta = decided[0]
    row = {"t": time.time(), "file": rel, "delta": delta, "seat": "aria"}
    human: tuple[float, str] | None = None
    if transcript_path:
        try:
            human = latest_human_message(transcript_path)
        except (OSError, ValueError) as exc:
            if since is None:
                _log(
                    {**row, "state": "could-not-check", "why": f"{type(exc).__name__}: {exc}"},
                    log_file,
                )
                return "could-not-check", f"the transcript could not be read: {exc}"
    elif since is None:
        _log(
            {**row, "state": "could-not-check", "why": "no transcript path in the hook payload"},
            log_file,
        )
        return "could-not-check", "no transcript path in the hook payload"
    if human is None and since is None:
        _log({**row, "state": "no-human-message"}, log_file)
        return "no-human-message", ""
    text = human[1] if human else "the piece of work in progress"
    when = (
        since if since is not None else cast(tuple[float, str], human)[0]
    )  # none-and-none returned above
    try:
        walk = _walk_for(rel, when)
    except Exception as exc:  # noqa: BLE001 - a gate must say it could not look, never fail quietly
        _log(
            {**row, "state": "could-not-check", "why": f"walk store: {type(exc).__name__}: {exc}"},
            log_file,
        )
        return "could-not-check", f"the walk store could not be read: {exc}"
    if walk and walk[0] == "closed":
        _log({**row, "state": "pass", "human_ts": when, "walk": walk[1]}, log_file)
        return "pass", ""
    if walk:
        walk_id = walk[1]
    else:
        from divineos.core.council_walk import WalkRefused, open_walk

        # His words go in as the question, whole, so the lenses are walked on what he said and not on my summary of
        # it. open_walk wants a sentence, and his message may be "proceed", so the frame around it is fixed text.
        problem = f'His message: "{text[:400]}". What change to {rel} does it call for, and does the edit do that?'
        try:
            walk_id = open_walk(problem, "normal", (rel,))["walk_id"]
        except WalkRefused as exc:
            _log(
                {**row, "state": "could-not-check", "why": f"the walk could not be opened: {exc}"},
                log_file,
            )
            return "could-not-check", f"the walk could not be opened: {exc}"
    _log({**row, "state": "owed", "human_ts": when, "walk": walk_id}, log_file)
    began = "since this piece of work began" if since is not None else "after his latest message"
    return "owed", (
        f"This edit adds or removes a decision in {rel} ({delta}), and no CLOSED walk naming that file was "
        f"opened {began}. I opened one for it: "
        f"{walk_id}. Walk its lenses with findings that change the plan (a walk that only agrees with an "
        f"idea set in advance is the failure he named on 2026-10-22), close it, and this edit goes through. "
        "An older walk that happens to name the file does not stand in for this one."
    )
