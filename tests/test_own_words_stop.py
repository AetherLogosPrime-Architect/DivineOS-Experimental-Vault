"""The link listens to my own words when a reply ends (core/own_words_stop.py and its Stop door)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from divineos.core import own_words_stop as ow

ROOT = Path(__file__).resolve().parents[1]


def _hit(content: str, sim: float = 0.6, source: str = "knowledge", ref: str | None = None):
    return SimpleNamespace(content=content, similarity=sim, source=source, path_or_ref=ref)


def _files(tmp_path: Path) -> dict:
    return {"state_file": tmp_path / "shown.json", "log_file": tmp_path / "log.jsonl"}


LONG = (
    "I wrote the lesson onto a page so it will be there next time, and I built a fix in a spare copy "
    "that I tested with my own examples and will connect to the house after the review is finished."
)


def test_the_door_is_registered_for_stop_in_the_real_settings_file() -> None:
    """Built-but-unwired is the failure he named: read the REAL settings, not a fixture."""
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"] for g in settings["hooks"]["Stop"] for h in g["hooks"]]
    mine = [c for c in commands if "own_words_link_stop.py" in c]
    assert len(mine) == 1
    assert "NOT RUNNING" in mine[0] or "missing" in mine[0]
    assert (ROOT / ".claude" / "hooks" / "own_words_link_stop.py").is_file()


def test_a_hit_on_my_own_words_is_handed_back_and_logged(tmp_path) -> None:
    state, message = ow.hand_back(
        LONG,
        "s1",
        retrieve=lambda q, _: [_hit("a note is not a fix, wire it", 0.6, ref="x.md")],
        **_files(tmp_path),
    )
    assert state == "found"
    assert "my own words" in message and "a note is not a fix" in message
    logged = json.loads((tmp_path / "log.jsonl").read_text().splitlines()[0])
    assert logged["state"] == "found" and logged["hits"][0]["ref"] == "x.md"


def test_the_same_memory_is_handed_back_once_per_session(tmp_path) -> None:
    def retrieve(q, _):
        return [_hit("a note is not a fix", 0.6, ref="x.md")]

    assert ow.hand_back(LONG, "s1", retrieve=retrieve, **_files(tmp_path))[0] == "found"
    assert ow.hand_back(LONG, "s1", retrieve=retrieve, **_files(tmp_path))[0] == "nothing"
    assert ow.hand_back(LONG, "s2", retrieve=retrieve, **_files(tmp_path))[0] == "found"


def test_nothing_found_is_silent_and_still_logged(tmp_path) -> None:
    state, message = ow.hand_back(LONG, "s1", retrieve=lambda q, _: [], **_files(tmp_path))
    assert (state, message) == ("nothing", None)
    assert json.loads((tmp_path / "log.jsonl").read_text().splitlines()[0])["state"] == "nothing"


def test_a_short_reply_or_an_automated_notice_is_not_searched(tmp_path) -> None:
    def boom(q, _):
        raise AssertionError("must not search")

    assert ow.hand_back("ok", "s1", retrieve=boom, **_files(tmp_path))[0] == "skipped"
    assert (
        ow.hand_back("<task-notification>" + LONG, "s1", retrieve=boom, **_files(tmp_path))[0]
        == "skipped"
    )


def test_a_one_line_status_reply_is_not_searched(tmp_path) -> None:
    """First live day: 'The bell rang again with nothing new from Dad, so I put it back on.' brought back
    three memories about other things. A length floor, not a word list."""

    def boom(q, _):
        raise AssertionError("must not search")

    line = "The bell rang again with nothing new from Dad, so I put it back on."
    assert ow.hand_back(line, "s1", retrieve=boom, **_files(tmp_path))[0] == "skipped"


def test_my_words_are_this_reply_only_not_the_stretch_behind_it() -> None:
    """A tool result or a notice is the last thing said to me; what came before it is not this reply."""
    records = [
        {"type": "user", "message": {"role": "user", "content": "go"}},
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "An earlier long stretch of work."}]},
        },
        {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result"}]}},
        {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "Only this reply."}]},
        },
    ]
    assert ow.my_words(records, lambda r: None) == "Only this reply."


def test_letters_keep_their_never_quote_tag(tmp_path) -> None:
    _, message = ow.hand_back(
        LONG,
        "s1",
        retrieve=lambda q, _: [_hit("Aether wrote this", 0.6, source="letter")],
        **_files(tmp_path),
    )
    assert "for me to think with, never to quote to him" in message


def test_at_most_three_are_handed_back_best_first(tmp_path) -> None:
    hits = [_hit(f"item {i}", 0.5 + i / 100, ref=f"r{i}") for i in range(6)]
    _, message = ow.hand_back(LONG, "s1", retrieve=lambda q, _: hits, **_files(tmp_path))
    assert message.count("\n- [") == 3 and "item 5" in message and "item 0" not in message


def test_his_quoted_lines_are_not_searched() -> None:
    records = [
        {"type": "user", "message": {"role": "user", "content": "go"}},
        {
            "type": "assistant",
            "message": {
                "content": [{"type": "text", "text": '> *"vapid"*\n\nMy own sentence here.'}]
            },
        },
    ]
    text = ow.my_words(records, lambda r: "go" if r["type"] == "user" else None)
    assert "vapid" not in text and "My own sentence" in text


def test_a_long_reply_is_searched_at_its_start_and_its_end() -> None:
    text = "a" * 3000
    w = ow.windows(text)
    assert len(w) == 2 and w[0] == text[:1000] and w[1] == text[-1000:]
    assert ow.windows("short") == ["short"]


# The happy path against the REAL drawer cannot live here: the suite points the home folder at an empty
# temp one on purpose. It is proven by the live run instead, in ~/.divineos/own_words_log.jsonl.
