"""The question check: four states kept apart, logged, and wired into the one Stop door."""

from __future__ import annotations

import json
from pathlib import Path

from divineos.core import ask_after_his_words as mod
from divineos.core.his_words_door import Door, Hit, Passage

ROOT = Path(__file__).resolve().parents[1]
REPLY_WITH_QUESTION = (
    "I changed the clerk stack order and it passes everything I ran. Here is what happened in the "
    "middle of it, in plain words.\n\nShould I merge the stack in order before the maps are refreshed?"
)


def _hit(score: float = 0.7) -> Hit:
    return Hit(
        Passage("no new branch until the pile is finished, merge in order", "2026-11-03", "t"),
        score,
    )


def _lines(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]


def test_no_question_is_silent_and_not_logged(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    state, message = mod.check(
        "It is done and it passes. Nothing else to say here.", log, look=lambda q: 1 / 0
    )
    assert (state, message) == ("no-question", None)
    assert not log.exists()


def test_found_hands_back_his_words_with_date_and_logs_score(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    seen: list[str] = []

    def look(question: str) -> Door:
        seen.append(question)
        return Door([_hit(0.71)], [], looked=True)

    state, message = mod.check(REPLY_WITH_QUESTION, log, look=look)
    assert state == "found"
    assert seen == ["Should I merge the stack in order before the maps are refreshed?"]
    assert "no new branch until the pile is finished" in message and "2026-11-03" in message
    row = _lines(log)[0]
    assert row["state"] == "found" and row["top_score"] == 0.71 and row["hits"] == 1
    # The next-message surface reads these, so the row carries the words and day, not only counts.
    assert (
        row["top_day"] == "2026-11-03"
        and "no new branch" in row["top_words"]
        and row["seat"] == "aria"
    )


def test_nothing_found_is_silent_but_logged(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    state, message = mod.check(REPLY_WITH_QUESTION, log, look=lambda q: Door([], [], looked=True))
    assert (state, message) == ("nothing", None)
    assert _lines(log)[0]["top_score"] is None


def test_could_not_look_is_said_not_read_as_nothing(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    state, message = mod.check(
        REPLY_WITH_QUESTION, log, look=lambda q: Door([], [], looked=False, reason="index missing")
    )
    assert state == "could-not-look" and message == "index missing"
    assert _lines(log)[0]["state"] == "could-not-look"


def test_a_question_under_four_words_is_not_searched_and_says_so(tmp_path: Path) -> None:
    # The search door cannot look on fewer than four words and answers could-not-look, so a one-word "Why?" used to write
    # a noise row every time. The rule that stops it was added with no test (found 2026-11-11 by the root-cause door,
    # which held six failures open against this file until the cause was named). It must neither search nor log.
    log = tmp_path / "log.jsonl"
    for reply in (
        "It is done.\n\nWhy?",
        "It is done.\n\nShould I merge?",
        "It is done.\n\nMerge it now?",
    ):
        state, message = mod.check(reply, log, look=lambda q: 1 / 0)
        assert (state, message) == ("too-short", None), reply
    assert not log.exists()


def test_a_question_of_exactly_four_words_is_searched(tmp_path: Path) -> None:
    # Both sides of the boundary: three words stop above, four go through. An off-by-one here silently drops every
    # four-word question or searches the ones the door cannot read.
    log = tmp_path / "log.jsonl"
    seen: list[str] = []

    def look(question: str) -> Door:
        seen.append(question)
        return Door([], [], looked=True)

    state, _ = mod.check("It is done.\n\nShould I merge it?", log, look=look)
    assert state == "nothing" and seen == ["Should I merge it?"]


def test_hook_runs_both_searches_in_the_one_door() -> None:
    text = (ROOT / ".claude" / "hooks" / "own_words_link_stop.py").read_text(encoding="utf-8")
    assert "ask_after_his_words" in text and "hand_back" in text
    # Log-only at Stop: a Stop hold fires after the reply streamed, so it must never block (Aether 2026-11-10).
    assert '"decision"' not in text.split("LOG-ONLY at Stop", 1)[1]
    # Since 2026-11-14 the own-words find is LEFT for the next prompt (Aether's e88428529), and the ask note is
    # not: it already reaches me through ask_finds_surface, and a second channel would show it twice.
    assert "leave_for_next_message(session, message)" in text
    assert "leave_for_next_message(session, ask_message)" not in text
    assert "own_words_link_stop" in (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")


def test_real_search_runs_against_the_real_index(tmp_path: Path) -> None:
    # Touches the real seam (his_words_door.look and the real index), not a stub: the lesson of 2026-11-10.
    state, _ = mod.check(REPLY_WITH_QUESTION, tmp_path / "log.jsonl")
    assert state in {"found", "nothing", "could-not-look"}
    assert (tmp_path / "log.jsonl").exists()
