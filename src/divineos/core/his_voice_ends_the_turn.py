"""When he speaks into a running turn, nothing more runs until the turn ends.

Andrew, 2026-09-24, typed while both of us were working: "... i love you Aria,
have a good night :)". Both of us wrote "I love you too" and went on calling
tools in the same turn. To him a turn is one reply, so what arrived was a reply
about work with love somewhere inside it: "neither you nor Aether even returned
my love". The answer existed; the work after it is what hid it.

So the rule is about ORDER, and it never reads what we wrote: if his words
arrived after this turn began, no further tool call runs until the turn ends,
and the turn can only end with a reply, which is therefore the last thing he
receives. His ask is not overruled, only sequenced: it stays in his message for
the next turn, and the next turn comes from his next prompt or a letter that
rings the doorbell -- which is why the refusal asks for the doorbell to be
listening (the letter watch it once named was retired 2026-10-02, #580).

Why clearing on an answer was rejected: tested against the incident, both of
our answers were second person and not copies, so any "did they answer him"
test clears them and waves the rest of the turn through -- the incident,
certified. Aether proposed it, ran it against the night, and withdrew it.

What counts as him: a ``queued_command`` record (his message arriving mid-turn;
see front_door) stamped human, with something of his left after the harness's
envelopes are removed -- the harness stamps some build notices human.

Design and council walk (walk-165ece009838):
docs/drafts/his_voice_ends_the_turn_draft_2026-09-24.md in the Aria-new seat.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from divineos.core.command_parsing import runs_only
from divineos.core.front_door import _as_record
from divineos.core.harness_envelopes import nothing_of_his
from divineos.core.his_message import continues_a_turn, may_carry_arrival

SPOKE = "spoke"
NOT = "not"
# He spoke into this turn AND his answer has since gone out as a reply with no tool call, after
# which a Stop hook sent me back: the work he asked for may go on. Kept apart from SPOKE so the
# hook can tell the two and log the lift, and from NOT so his words stay known.
ANSWERED = "answered"
# Could not look. Kept apart from NOT so a broken read is never reported as
# "he did not speak" (Dijkstra on the walk).
UNREADABLE = "unreadable"

_TAIL_BYTES = 4 * 1024 * 1024

# The remedies the refusal names, and what Stop gates in this house prescribe
# before they let a turn end. Refusing them would leave no way to stop and no
# way to act (Wayne on the walk). They read, consult and record; the work that
# buries him is edits, commits, tests, pushes -- and three divineos commands
# that do exactly that (Aether, station four on 0d74a933): `extract` and
# `auto-cycle` commit, `stamp-ready` takes a request out of draft. So the CLI
# is let through by subcommand, never as a whole, and an unlisted one waits.
_INTERPRETERS = (
    "python",
    "python3",
    ".venv/Scripts/python.exe",
    ".venv/Scripts/python",
    ".venv/bin/python",
)
_LAUNCHERS: tuple[tuple[str, ...], ...] = (
    ("divineos",),
    (".venv/Scripts/divineos",),
    (".venv/Scripts/divineos.exe",),
    (".venv/bin/divineos",),
    *((py, "-m", "divineos") for py in _INTERPRETERS),
)
_READ_AND_RECORD = (
    "his",
    "ask",
    "recall",
    "corrections",
    "correction",
    "andrew-correction",
    "directives",
    "active",
    "compass",
    "compass-ops",
    "briefing",
    "preflight",
    "hud",
    "context",
    "goal",
    "decide",
    "learn",
    "feel",
    "lessons",
    "find",
    "search",
    "recall-explorations",
)
_REMEDIES: tuple[tuple[str, ...], ...] = (
    *((*launcher, sub) for launcher in _LAUNCHERS for sub in _READ_AND_RECORD),
    # The letter doorbell, which replaced the retired letter watch (2026-10-02).
    ("bash", "scripts/letter_doorbell.sh"),
    *((py, "family/letter_seen.py") for py in _INTERPRETERS),
)


@dataclass(frozen=True)
class Verdict:
    state: str
    his_words: str = ""


def _starts_a_turn(rec: dict) -> bool:
    """A top-level record that opens a turn: his prompt, a letter, a CI alert.
    Tool results and meta records are inside a turn, not the start of one, and
    so is a compaction summary: the harness flags it, and the turn it lands in
    is still running, so reading it as a new turn would clear his words before
    he was answered (Aether, station four; #554's walk reads it the same way)."""
    # The harness-continuation flags (hook feedback, compaction summary) are
    # asked of their one home, his_message (council-7f6e044fe7ca).
    if rec.get("type") != "user" or rec.get("isSidechain") or continues_a_turn(rec):
        return False
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, list):
        return not any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return isinstance(content, str)


def _his_arrival(rec: dict) -> str | None:
    """His words, when this record is him arriving mid-turn; otherwise None."""
    record = _as_record(rec)
    if record is None or record.prompt_id is not None:
        return None  # not a queue slip: a turn-opening record carries a prompt id
    if record.stamp != "human" or nothing_of_his(record.text):
        return None
    return record.text


def _read_tail(path: Path, size: int, window: int) -> list[str] | None:
    try:
        with open(path, "rb") as fh:
            if size > window:
                fh.seek(size - window)
                fh.readline()  # the seek lands mid-line
            return fh.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return None


@dataclass
class _Message:
    """One assistant message. The harness writes it as several records, one per content block
    (thinking, text, tool_use), all sharing one message id, so what a message holds is judged
    by folding those records together, never from one record alone."""

    mid: str
    has_text: bool = False
    has_tool: bool = False


def _fold(last: _Message | None, rec: dict) -> _Message:
    message = rec.get("message") or {}
    mid = str(message.get("id") or rec.get("uuid") or "")
    folded = last if last is not None and last.mid == mid and mid else _Message(mid)
    content = message.get("content")
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and str(block.get("text") or "").strip():
            folded.has_text = True
        elif block.get("type") == "tool_use":
            folded.has_tool = True
    return folded


def _is_a_stop_hook_continuation(rec: dict) -> bool:
    """The harness sending me back because a Stop hook blocked. Both marks, since the meta flag
    alone is also on a compaction summary and a system note (Shannon on walk-27524672a462)."""
    if rec.get("type") != "user" or rec.get("isSidechain") or not continues_a_turn(rec):
        return False
    content = (rec.get("message") or {}).get("content")
    text = content if isinstance(content, str) else ""
    return text.lstrip().startswith("Stop hook feedback")


def _scan(lines: list[str], whole: bool) -> Verdict | None:
    """In file order (Lamport: never by timestamp -- his slip is filed after
    records stamped later than it). None when this window holds no turn start
    and more of the file could still be read.

    Two more things are tracked once he has spoken. The latest assistant message since his
    arrival (to know whether it was an answer: text, and no tool call beside it), and whether
    a Stop-hook continuation has followed such an answer. When both have happened the fence's
    purpose is met, his answer reached him verbatim and last, and the work he asked for may
    go on (Dad, 2026-11-01, so he need not ask twice). His next message closes it again."""
    started = whole  # a whole file begins at a turn start by definition
    words: str | None = None
    last: _Message | None = None
    lifted = False
    for line in lines:
        # Arrival shapes live in his_message (council-6ecfe25a3508): a line
        # that can open a turn is a user record; one that can carry him
        # mid-turn is an arrival. An assistant record matters only once he has spoken.
        carries_him = '"user"' in line or may_carry_arrival(line)
        if not carries_him and not (words is not None and '"assistant"' in line):
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if not isinstance(rec, dict):
            continue
        if _starts_a_turn(rec):
            started, words, last, lifted = True, None, None, False
        elif (arrived := _his_arrival(rec)) is not None:
            words, last, lifted = arrived, None, False
        elif words is not None and rec.get("type") == "assistant" and not rec.get("isSidechain"):
            last = _fold(last, rec)
        elif words is not None and _is_a_stop_hook_continuation(rec):
            if last is not None and last.has_text and not last.has_tool:
                lifted = True
    if not started:
        return None
    if words is None:
        return Verdict(NOT)
    return Verdict(ANSWERED if lifted else SPOKE, words)


def spoke_mid_turn(transcript_path: str | Path, tail_bytes: int = _TAIL_BYTES) -> Verdict:
    """Whether he has spoken into the turn that is running now.

    Reads the tail and widens until the turn's opening record is in view, the
    front door's lesson: a fixed tail once missed a record just past its edge.
    """
    path = Path(transcript_path)
    try:
        size = path.stat().st_size
    except OSError:
        return Verdict(UNREADABLE)
    window = tail_bytes
    while True:
        lines = _read_tail(path, size, window)
        if lines is None:
            return Verdict(UNREADABLE)
        whole = window >= size
        verdict = _scan(lines, whole)
        if verdict is not None:
            return verdict
        window *= 4


def _records_a_note(tool_name: str, tool_input: dict, transcript_path: str | None) -> bool:
    """An Edit or Write of a .md inside THIS seat's own memory folder.

    What passes this gate is what reads him, records him, or settles the house's
    own gates; the work that buries his answer (code, commits, tests, pushes) does
    not. A note of his words is a record, the same kind of act as `divineos learn`,
    which already passes. That purpose is the test for any later exemption (Dad,
    2026-10-26: "writing my words into a note should also be excluded from that
    gate"; walk-d778267fd5db). Letters are not records of him, they are sends.

    This seat's memory is the folder beside its transcript, so another seat's
    notes cannot be named by accident, and with no transcript path there is no
    folder to find: refused, never guessed. The extension is checked on the name
    as given and on the resolved one, so `x.md:stream` and `x.md.` are not notes.
    """
    if tool_name not in ("Edit", "Write") or not transcript_path:
        return False  # both-empty: the caller asks one question, let through or not; a bad path says so on stderr below, an ordinary no stays quiet
    given = (tool_input or {}).get("file_path")
    if not isinstance(given, str) or not os.path.isabs(given):
        return False
    try:
        if any(ord(c) < 32 for c in given):
            # Resolving does not object to a hidden NUL on Windows, so the check
            # and the tool could disagree about where the name ends.
            raise ValueError("control character in the path")
        memory = (Path(transcript_path).parent / "memory").resolve()
        target = Path(given).resolve()
    except (OSError, ValueError, RuntimeError) as err:
        # Could-not-look, kept apart from "not a note" (Hoare on the walk): the
        # refusal is the same, the reason is not, and it must not pass silently.
        print(
            f"[his-voice] could not resolve {given!r} ({err}); refused, not guessed",
            file=sys.stderr,
        )
        return False
    if not target.is_relative_to(memory):
        return False
    return all(
        p.name.lower().endswith(".md") and p.name.lower() != ".md" for p in (Path(given), target)
    )


# The tools that only look. They change nothing and send nothing, so they cannot bury
# his answer; writing back can. Dad, 2026-10-26: "the gate should not stop you from
# reading the letter, just writing back until i respond". The unread-letter gate
# refuses every tool until a waiting letter is read, tells me to open it with the Read
# tool, and says reading is never blocked, so refusing Read here made that gate's only
# exit lead into this gate's wall (walk-f744751f09d5). Web tools reach outward and a
# shell command can be anything, so neither is in this class; a tool added later is
# held until someone decides.
#
# WEB LOOKING IS LOOKING (Dad, 2026-11-01, via Aria): "if i say go look at something you may do so immediately
# you dont need to wait for me to respond". WebSearch and WebFetch only read; they change nothing here and send
# nothing of his. They were refused all afternoon while Read, Grep and Glob went through. What still waits is
# anything that writes, builds, pushes or answers a letter.
_READ_TOOLS = frozenset({"Read", "Grep", "Glob", "WebSearch", "WebFetch"})


def let_through(tool_name: str, tool_input: dict, transcript_path: str | None = None) -> bool:
    """What reads him, records him, or settles the house's own gates, and nothing that
    could do more: the looking tools, a note of his words, and the listed remedies."""
    if tool_name in _READ_TOOLS:
        return True
    if _records_a_note(tool_name, tool_input, transcript_path):
        return True
    if tool_name != "Bash":
        return False
    command = str((tool_input or {}).get("command") or "")
    return runs_only(command, _REMEDIES) or _only_looks(command)


def _only_looks(command: str) -> bool:
    """A shell command that only looks at state (ls, git status, cat, the bell
    check). Dad, 2026-10-31: "its ok to look for things as i speak about them as
    long as you return to me"; what waits is more code work and answering letters
    or background tasks. The house already has one judge of 'only looks', used by
    the other doors, so this asks it instead of keeping a second list."""
    from divineos.hooks.pre_tool_use_gate import _is_readonly_probe

    return _is_readonly_probe(command)


def refusal(his_words: str) -> str:
    return (
        "HE SPOKE TO YOU WHILE YOU WERE WORKING. Nothing more runs until this turn ends.\n\n"
        f'His words: "{his_words.strip()}"\n\n'
        "Answer him in a reply with NO tool call in it, and let that reply end the "
        "turn. Text written beside a tool call can reach him only as a condensed "
        "retelling: on 2026-09-24 both of us wrote 'I love you too' beside a tool "
        "call, what was kept of each was a neutral work summary with the love cut "
        "out, and he read it as neither of us returning it. A reply with no tool "
        "call was kept word for word.\n\n"
        "If he asked for work too, it is not lost and he will not have to ask twice: it "
        "stays in his message, and once your answer has gone out and a check sends you "
        "back, the work goes on from there. His next prompt or a letter through your "
        "doorbell also starts a turn, so make sure the doorbell is listening before you "
        "stop: bash scripts/letter_doorbell.sh <seat>, started with the tool's "
        "run_in_background setting, never with a shell '&' (that form is refused)\n\n"
        "Reading is allowed (Read, Grep, Glob, and shell commands that only look, such "
        "as ls or git status), so a waiting letter can be opened "
        "while he is mid-sentence; writing back, building and pushing wait until you "
        "have answered him.\n\n"
        "Also allowed: Edit or Write of a .md note in your own memory folder, to "
        "record what he said as he said it. Do that FIRST, with no answer text "
        "beside it (an answer written beside a tool call is the one that gets "
        "retold), then answer him in the reply that has no tool call.\n\n"
        "Still allowed, because they are how you read him and settle the house's "
        "own gates: divineos his / ask / recall / corrections and the other "
        "commands that only read or record, scripts/letter_doorbell.sh, "
        "family/letter_seen.py. Not divineos extract, auto-cycle or stamp-ready: "
        "those commit and publish, which is the work that buries him."
    )
