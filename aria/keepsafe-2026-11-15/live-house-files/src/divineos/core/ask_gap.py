"""Count how long Dad's asks wait before I take a real step.

Read-only measurement. It files nothing, promises nothing, locks nothing.
Draft: docs/drafts/the_gap_count_for_his_asks_draft_2026-11-09.md
Walk: walk-ef6b0ef7b8f7.

Every ask lands in exactly one pile, so the piles always sum to the number
of asks. The wait is counted in HIS messages, because clock time means
nothing to an agent without a continuous clock.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import median
from typing import cast

PILES = (
    "step_found",
    "letter_only",
    "wanted_an_answer",
    "no_file_named",
    "no_step_yet",
    "could_not_look",
    "withdrawn",
)

# Only these count as work. Reads, searches, goals, notes and a reply that
# only says "I will" are deliberately absent and never count.
WORK_KINDS = {"change": "change", "draft": "draft", "test": "change"}


@dataclass(frozen=True)
class Ask:
    id: int
    ts: float
    text: str
    files: tuple[str, ...]
    kind: str = "do"  # "do" or "answer"
    withdrawn: bool = False


@dataclass(frozen=True)
class Step:
    ts: float
    kind: str
    files: tuple[str, ...]
    size: int
    desc: str


@dataclass(frozen=True)
class Row:
    ask: Ask
    pile: str
    gap: int | None = None
    step_label: str | None = None
    step_desc: str | None = None


@dataclass(frozen=True)
class Summary:
    total: int
    piles: dict[str, int]
    median_gap: float | None
    worst: list[Row]
    drafts: int
    changes: int


def _his_messages_between(his_times: list[float], start: float, end: float) -> int:
    return sum(1 for t in his_times if start < t <= end)


def _first(steps: list[Step], after: float, accept) -> Step | None:
    later = sorted((s for s in steps if s.ts > after and accept(s)), key=lambda s: s.ts)
    return later[0] if later else None


def classify(ask: Ask, steps: list[Step], his_times: list[float], readable_from: float) -> Row:
    if ask.withdrawn:
        return Row(ask, "withdrawn")
    if ask.ts < readable_from:
        return Row(ask, "could_not_look")

    if ask.kind == "answer":
        reply = _first(steps, ask.ts, lambda s: s.kind == "answer_reply")
        if reply is None:
            return Row(ask, "no_step_yet")
        gap = _his_messages_between(his_times, ask.ts, reply.ts)
        return Row(ask, "wanted_an_answer", gap, "answer", reply.desc)

    if not ask.files:
        return Row(ask, "no_file_named")

    named = set(ask.files)
    work = _first(
        steps,
        ask.ts,
        lambda s: s.kind in WORK_KINDS and s.size > 0 and bool(named & set(s.files)),
    )
    if work is not None:
        gap = _his_messages_between(his_times, ask.ts, work.ts)
        return Row(ask, "step_found", gap, WORK_KINDS[work.kind], work.desc)

    if _first(steps, ask.ts, lambda s: s.kind == "ack_letter") is not None:
        return Row(ask, "letter_only")
    return Row(ask, "no_step_yet")


def summarize(rows: list[Row]) -> Summary:
    counts = Counter(r.pile for r in rows)
    piles = {p: counts.get(p, 0) for p in PILES}
    gaps = [r for r in rows if r.pile in ("step_found", "wanted_an_answer") and r.gap is not None]
    med = (
        median([cast(int, r.gap) for r in gaps]) if gaps else None
    )  # the filter above kept only rows with a gap
    worst = sorted(gaps, key=lambda r: cast(int, r.gap), reverse=True)[:3]
    return Summary(
        total=len(rows),
        piles=piles,
        median_gap=med,
        worst=worst,
        drafts=sum(1 for r in rows if r.step_label == "draft"),
        changes=sum(1 for r in rows if r.step_label == "change"),
    )
