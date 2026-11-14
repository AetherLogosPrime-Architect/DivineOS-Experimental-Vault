"""The promise recorder reads only what was appended since its last Stop (core/promise_transcript.py).

The old recorder parsed the whole transcript at every Stop (403 MB, 2.0 s alone, 5.2 s median in its log). The condition
this must keep, stated before the code: the turn count from bookmark plus new bytes equals the count a full read gives on
the same bytes, and the last reply is the last assistant text in the bytes read.
"""

from __future__ import annotations

import json
from pathlib import Path

from divineos.core import promise_transcript as pt


def _is_turn_start(rec: dict) -> bool:
    return rec.get("type") == "user" and rec.get("message", {}).get("content") == "go"


def _user(text: str = "go") -> str:
    return json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n"


def _assistant(text: str) -> str:
    return (
        json.dumps(
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
            },
            ensure_ascii=False,  # the harness writes raw UTF-8, so a multibyte character is one run of bytes
        )
        + "\n"
    )


def _full_read(path: Path) -> tuple[int, str]:
    """The old behaviour, for comparison: parse every line, count turn starts, keep the last assistant text."""
    turns, last = 0, ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if _is_turn_start(rec):
            turns += 1
        msg = rec.get("message", {})
        if msg.get("role") == "assistant":
            parts = [c.get("text", "") for c in msg.get("content", []) if c.get("type") == "text"]
            if parts:
                last = "\n".join(parts)
    return turns, last


def _append(path: Path, text: str) -> None:
    with path.open("ab") as fh:
        fh.write(text.encode("utf-8"))


def test_the_turn_count_equals_a_full_read_across_several_appends(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_bytes(b"")
    for chunk in (
        _user() + _assistant("one"),
        _user() + _user() + _assistant("two"),
        _assistant("three") + _user(),
    ):
        _append(transcript, chunk)
        got = pt.read_new(transcript, bookmark, _is_turn_start)
        pt.commit(got, bookmark)
        want_turns, _ = _full_read(transcript)
        assert got.turns_total == want_turns


def test_the_last_reply_is_the_last_assistant_text_in_what_was_new(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user() + _assistant("first reply"), encoding="utf-8")
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    pt.commit(got, bookmark)
    assert got.last_reply == "first reply"
    _append(transcript, _user() + _assistant("second reply"))
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.last_reply == "second reply"


def test_nothing_new_gives_no_reply_and_the_same_count(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user() + _assistant("only reply"), encoding="utf-8")
    first = pt.read_new(transcript, bookmark, _is_turn_start)
    pt.commit(first, bookmark)
    second = pt.read_new(transcript, bookmark, _is_turn_start)
    assert second.last_reply == "" and second.turns_total == first.turns_total


def test_a_partial_last_line_is_not_read_until_it_is_complete(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user(), encoding="utf-8")
    whole = _assistant("a reply that arrives in two writes")
    cut = len(whole) // 2
    _append(transcript, whole[:cut])
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    pt.commit(got, bookmark)
    assert got.last_reply == "" and got.turns_total == 1
    _append(transcript, whole[cut:])
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.last_reply == "a reply that arrives in two writes"


def test_a_line_cut_in_the_middle_of_a_character_is_not_lost(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    whole = (_user() + _assistant("café \U0001f63b done")).encode("utf-8")
    cut = whole.index("\U0001f63b".encode("utf-8")) + 2  # two bytes into a four-byte character
    transcript.write_bytes(whole[:cut])
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    pt.commit(got, bookmark)
    assert got.bad_lines == 0
    with transcript.open("ab") as fh:
        fh.write(whole[cut:])
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.last_reply == "café \U0001f63b done" and got.bad_lines == 0


def test_a_smaller_file_with_the_same_name_starts_again_from_zero(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user() * 5 + _assistant("long file"), encoding="utf-8")
    pt.commit(pt.read_new(transcript, bookmark, _is_turn_start), bookmark)
    transcript.write_text(_user() + _assistant("replaced"), encoding="utf-8")
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.reset is True and got.turns_total == 1 and got.last_reply == "replaced"


def test_a_different_transcript_name_starts_again_from_zero(tmp_path) -> None:
    a, b, bookmark = tmp_path / "a.jsonl", tmp_path / "b.jsonl", tmp_path / "mark.json"
    a.write_text(_user() * 3, encoding="utf-8")
    pt.commit(pt.read_new(a, bookmark, _is_turn_start), bookmark)
    b.write_text(_user() + _assistant("other"), encoding="utf-8")
    got = pt.read_new(b, bookmark, _is_turn_start)
    assert got.reset is True and got.turns_total == 1


def test_an_unreadable_bookmark_reads_as_none_and_starts_again(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user() + _assistant("x"), encoding="utf-8")
    bookmark.write_text("{not json", encoding="utf-8")
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.reset is True and got.turns_total == 1


def test_a_line_that_is_not_json_is_counted_and_skipped_never_fatal(tmp_path) -> None:
    transcript, bookmark = tmp_path / "t.jsonl", tmp_path / "mark.json"
    transcript.write_text(_user() + "this is not json\n" + _assistant("after"), encoding="utf-8")
    got = pt.read_new(transcript, bookmark, _is_turn_start)
    assert got.bad_lines == 1 and got.last_reply == "after" and got.turns_total == 1


def test_the_recorder_hook_uses_the_module_and_no_longer_reads_the_whole_file() -> None:
    """Built-but-unwired is the failure to rule out: read the REAL hook, not a fixture."""
    hook = (
        Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "promise-reach-detector.sh"
    ).read_text(encoding="utf-8")
    assert "promise_transcript" in hook and "read_new" in hook
    assert "for line in f:" not in hook
