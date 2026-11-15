"""No fix without a root cause: a decision edit to a file with an open failure fact is refused until a root-cause record
cites something READ after the failure, and that thing is the failing file or its test.

MINE, I built it, and why. Dad, 2026-11-10, in his own words: "if you have nothing forcing a root cause investigation..
you have no business fixing anything", and "you are only held from building until the build flow is setup to where
it cannot be skipped or ignored". The shape he named, month after month: he points at a missing step, the step is done
once, nothing records why it was skipped, nothing makes it unskippable, and the skip returns. Doing the step is the
placation. Plan, walks and measurements: docs/drafts/no_fix_without_a_root_cause_the_house_forces_it_draft_2026-11-11.md
(walk-f7b48c9845f9 and walk-ef0a5826cba2). The refusing door WRITES the failure fact at the moment of refusal, so it is
never re-derived from transcripts later.

Facts only, never his words: a failure fact is a refusal of a build-flow step by the work-item door, tied to a named
file. Per seat, per file: a fact on file A never holds file B, and one seat's fact never holds the other's edit. The
record must cite a path that is the failing file or its test (tests/test_<stem>.py), read (Read, Grep or Glob) strictly
AFTER the failure in the action stream, which is the one thing I did not write. Every evaluation writes a liveness row
FIRST, before anything that can fail, so a door that dies mid-evaluation still leaves a row (Aether's thin spot).

Not in this slice, stated so it is not mistaken for done: the recurrence half (the same refusal on the same file
reopening a closed record) is Aether's; a failed test as a failure fact is not wired; a decision written through a
Bash redirection is not seen by this check.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from divineos.core.walk_after_his_message import _edits_of, _relative_house_path, decision_delta

STORE = Path.home() / ".divineos" / "failure_facts.jsonl"
LIVENESS = Path.home() / ".divineos" / "root_cause_door_liveness.jsonl"
MIN_TEXT = 40
TAIL_BYTES = 3_000_000
READ_TOOLS = ("Read", "Grep", "Glob")


@dataclass(frozen=True)
class Result:
    state: str  # 'accepted' | 'refused'
    why: str = ""


def seat_of(repo_root: Path) -> str:
    return os.environ.get("DIVINEOS_SEAT") or (
        "aria" if "aria" in str(repo_root).lower() else "aether"
    )


def _append(row: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def _rows(path: Path) -> list[dict]:
    """A missing file is no rows; a file that cannot be READ raises, so 'nothing found' and 'could not look' stay two
    states (walk-010a093d2520, Hoare). The caller that stands aside says so."""
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _fires_log() -> Path:
    """The router's one log, resolved at call time (the override is for tests). ONE record, not two (Aether 2026-11-11)."""
    override = os.environ.get("DIVINEOS_HOOK_FIRES_LOG")
    if override:
        return Path(override)
    return (
        Path(os.environ.get("DIVINEOS_HOME") or str(Path.home() / ".divineos")) / "hook_fires.jsonl"
    )


SURFACE = "work_item_doorman"


def record_failure(kind: str, file: str | None, seat: str) -> bool:
    """Append the build-flow door's refusal to the router's log, in its row shape plus file and seat.
    A refusal with no file owes nothing, so it is not recorded (the first boundary test)."""
    if not file:
        return False
    _append(
        {
            "t": round(time.time(), 3),
            "event": "PreToolUse",
            "surface": SURFACE,
            "state": "refused",
            "file": file,
            "seat": seat,
            "kind": kind,
        },
        _fires_log(),
    )
    return True


def open_facts(file: str, seat: str, store: Path | None = None) -> list[dict]:
    """The door's refusals for this file and seat that no root-cause record has closed. The refusal lives in the
    router's log; the store keeps only the closing records, so a refusal is never copied."""
    closes = [
        r
        for r in _rows(store or STORE)
        if r.get("status") == "closed" and r.get("file") == file and r.get("seat") == seat
    ]
    last_close = max((r["t"] for r in closes), default=0.0)
    return [
        r
        for r in _rows(_fires_log())
        if r.get("surface") == SURFACE
        and r.get("state") == "refused"
        and r.get("file") == file
        and r.get("seat") == seat
        and r["t"] > last_close
    ]


def _test_of(rel: str) -> str:
    return f"tests/test_{Path(rel).stem}.py"


def _read_after(transcript_path: str, evidence: str, since: float, repo_root: Path) -> bool:
    """True when the action stream shows a Read, Grep or Glob of this path strictly after `since`."""
    path = Path(transcript_path)
    size = path.stat().st_size
    with path.open("rb") as fh:
        fh.seek(max(0, size - TAIL_BYTES))
        raw = fh.read().decode("utf-8", errors="replace")
    wanted = {evidence, str((repo_root / evidence)).replace("\\", "/")}
    for line in raw.splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("type") != "assistant" or not rec.get("timestamp"):
            continue
        when = datetime.fromisoformat(rec["timestamp"].replace("Z", "+00:00")).timestamp()
        if when <= since:
            continue
        for item in (rec.get("message") or {}).get("content") or []:
            if (
                isinstance(item, dict)
                and item.get("type") == "tool_use"
                and item.get("name") in READ_TOOLS
            ):
                args = item.get("input") or {}
                touched = {
                    str(args.get(k) or "").replace("\\", "/")
                    for k in ("file_path", "path", "pattern")
                }
                if wanted & touched or any(w and w in t for w in wanted for t in touched):
                    return True
    return False


def file_root_cause(
    file: str,
    text: str,
    evidence: str | None,
    seat: str,
    transcript_path: str,
    store: Path | None = None,
    repo_root: Path | None = None,
) -> Result:
    """File the root-cause record that closes every open refusal for this file and seat, or refuse and say why."""
    root = repo_root or Path(__file__).resolve().parents[3]
    store = store or STORE
    facts = open_facts(file, seat, store)
    if not facts:
        return Result(
            "refused",
            f"there is no open failure fact for {file} for this seat, so there is nothing to close",
        )
    if len((text or "").strip()) < MIN_TEXT:
        return Result(
            "refused",
            f"the root cause needs at least {MIN_TEXT} characters; a label is not a cause",
        )
    if not evidence:
        return Result(
            "refused", "the record must cite a path that was read after the failure; none was given"
        )
    if not (root / evidence).is_file():
        return Result("refused", f"the cited path {evidence} does not exist")
    if evidence not in (file, _test_of(file)):
        return Result(
            "refused",
            f"the cited path must be the failing file or its test ({file} or {_test_of(file)}), not {evidence}",
        )
    latest = max(f["t"] for f in facts)  # evidence must postdate the MOST RECENT refusal, strictly
    try:
        seen = _read_after(transcript_path, evidence, latest, root)
    except OSError as exc:
        return Result("refused", f"the transcript could not be read to check the evidence: {exc}")
    if not seen:
        return Result(
            "refused",
            f"{evidence} was not read after the failure at {latest:.0f}; the record must cite something looked at AFTER it",
        )
    # One closing row closes every older refusal for the file and seat (a file collects many: one door refused 291 times).
    _append(
        {
            "t": time.time(),
            "seat": seat,
            "file": file,
            "status": "closed",
            "by": "root-cause",
            "text": text.strip(),
            "evidence": evidence,
            "closes": len(facts),
        },
        store,
    )
    return Result("accepted")


EDIT_TOOLS = ("Edit", "Write", "MultiEdit")


def liveness_started(tool_name: str, seat: str, liveness: Path | None = None) -> None:
    """The first thing the door does for an edit call, before anything that can fail (Aether's thin spot: a door that
    errors before writing is blind exactly when it is broken). Only edit calls, so the row count stays readable."""
    if tool_name in EDIT_TOOLS:
        _append(
            {"t": time.time(), "seat": seat, "state": "started", "tool": tool_name},
            liveness or LIVENESS,
        )


def check_edit(
    tool_name: str,
    tool_input: dict,
    repo_root: Path,
    seat: str,
    store: Path | None = None,
    liveness: Path | None = None,
) -> tuple[str, str]:
    """('owed', message) when this edit adds or removes a decision in a file with an open failure fact; else ('not-applicable', '')."""
    for path, before, after in _edits_of(tool_name, tool_input):
        rel = _relative_house_path(path, repo_root)
        if rel is None or not decision_delta(before, after):
            continue
        facts = open_facts(rel, seat, store)
        if facts:
            _append(
                {
                    "t": time.time(),
                    "seat": seat,
                    "state": "owed",
                    "file": rel,
                    "refusals": len(facts),
                },
                liveness or LIVENESS,
            )
            return "owed", (
                f"{rel} was refused by the build-flow door earlier in this stretch of work, and this edit adds or removes a "
                "decision in it. A fix needs its root cause first: read the failing file or its test now, then file the "
                f"record: .venv/Scripts/python.exe -m divineos.core.root_cause_before_fix --file {rel} --evidence {rel} "
                '--text "<what actually caused it, at least 40 characters>". It must cite something read AFTER the '
                "failure, and it has to be the failing file or its test. This exists because he had to ask where the build "
                "flow was, watch the step be done once, and see the skip return."
            )
    if tool_name in EDIT_TOOLS:
        _append({"t": time.time(), "seat": seat, "state": "not-applicable"}, liveness or LIVENESS)
    return "not-applicable", ""


def _latest_transcript(repo_root: Path) -> str:
    folder = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(repo_root))
    files = sorted(folder.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return str(files[-1]) if files else ""


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="File the root cause for a file that failed, before fixing it."
    )
    parser.add_argument("--file", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--text", required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[3]
    result = file_root_cause(
        args.file, args.text, args.evidence, seat_of(root), _latest_transcript(root), repo_root=root
    )
    print(f"{result.state}: {result.why}".rstrip(": "))
    return 0 if result.state == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
