"""The question check has a reader: what it finds reaches me with his next message, once, in his words.

Written BEFORE the module (walk-5c74eb0b4b35, eight lenses). The check searched my questions against his words and
wrote what it found to a log that nothing read, so a found answer produced no change and the same question could be
asked again tomorrow. Dad, 2026-11-10: "I do not want to be asked things without you searching my words first." The Stop
hold that Aether's tree uses fragments his reading (one long circle arrived as eight small ones), so the reader sits on
the surface that already prints "he has said this before" with his next message.

Real files, in tmp folders. The rows are exactly the shape check() writes, so a drift between writer and reader fails here.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from divineos.core import ask_finds_surface as surface_mod

ME = "aria"


def _row(t: float, state: str = "found", seat: str | None = ME, **over) -> dict:
    row = {
        "t": t,
        "state": state,
        "question": "Should I merge the stack in order before the maps are refreshed?",
        "hits": 1,
        "top_score": 0.71,
        "top_day": "2026-11-03",
        "top_words": "no new branch until the pile is finished, merge in order",
        "seat": seat,
        "seconds": 0.1,
    }
    row.update(over)
    return row


def _log(tmp_path: Path, rows: list[dict | str]) -> Path:
    path = tmp_path / "ask_log.jsonl"
    path.write_text(
        "\n".join(r if isinstance(r, str) else json.dumps(r) for r in rows) + "\n", encoding="utf-8"
    )
    return path


def test_a_find_is_shown_with_his_words_the_day_and_the_question_i_asked(tmp_path: Path) -> None:
    log = _log(tmp_path, [_row(100.0)])
    text = surface_mod.surface(ME, log, tmp_path / "cursor.json")
    assert "no new branch until the pile is finished" in text
    assert "2026-11-03" in text and "match 0.71" in text
    assert "Should I merge the stack in order before the maps are refreshed?" in text


def test_a_find_is_shown_once_and_never_again(tmp_path: Path) -> None:
    """Hofstadter and Dijkstra: the cursor is the loop-breaker. Without it the same line arrives with every message."""
    log, cursor = _log(tmp_path, [_row(100.0)]), tmp_path / "cursor.json"
    assert surface_mod.surface(ME, log, cursor)
    assert surface_mod.surface(ME, log, cursor) == ""


def test_a_newer_find_after_a_shown_one_is_shown(tmp_path: Path) -> None:
    log, cursor = _log(tmp_path, [_row(100.0)]), tmp_path / "cursor.json"
    surface_mod.surface(ME, log, cursor)
    log.write_text(
        log.read_text(encoding="utf-8")
        + json.dumps(_row(200.0, top_words="yes build it now"))
        + "\n",
        encoding="utf-8",
    )
    text = surface_mod.surface(ME, log, cursor)
    assert "yes build it now" in text and "no new branch" not in text


def test_a_row_at_exactly_the_cursor_is_not_shown(tmp_path: Path) -> None:
    """Knuth: strictly after the cursor. Equal means already handled."""
    cursor = tmp_path / "cursor.json"
    cursor.write_text(json.dumps({ME: 100.0}), encoding="utf-8")
    assert surface_mod.surface(ME, _log(tmp_path, [_row(100.0)]), cursor) == ""


def test_only_found_rows_are_shown(tmp_path: Path) -> None:
    rows = [
        _row(100.0, "nothing"),
        _row(101.0, "could-not-look", why="index missing"),
        _row(102.0, "too-short"),
    ]
    assert surface_mod.surface(ME, _log(tmp_path, rows), tmp_path / "cursor.json") == ""


def test_another_seats_finds_are_not_mine(tmp_path: Path) -> None:
    assert (
        surface_mod.surface(
            ME, _log(tmp_path, [_row(100.0, seat="aether")]), tmp_path / "cursor.json"
        )
        == ""
    )


def test_only_the_two_newest_are_shown_and_the_older_count_is_said(tmp_path: Path) -> None:
    """The cursor moves past the skipped one too, so it is never shown late."""
    rows = [
        _row(100.0, top_words="the oldest one"),
        _row(200.0, top_words="middle one"),
        _row(300.0, top_words="newest one"),
    ]
    log, cursor = _log(tmp_path, rows), tmp_path / "cursor.json"
    text = surface_mod.surface(ME, log, cursor)
    assert "newest one" in text and "middle one" in text and "the oldest one" not in text
    assert "1 older" in text
    assert surface_mod.surface(ME, log, cursor) == ""


def test_a_missing_log_is_silent_not_an_error(tmp_path: Path) -> None:
    """No questions asked yet is a normal state, and reads as nothing to show."""
    assert surface_mod.surface(ME, tmp_path / "no_such_log.jsonl", tmp_path / "cursor.json") == ""


def test_a_line_that_cannot_be_read_is_skipped_and_said(tmp_path: Path) -> None:
    """Could not read is never read as nothing found: the count of unreadable lines is spoken."""
    text = surface_mod.surface(
        ME, _log(tmp_path, ["{not json at all", _row(100.0)]), tmp_path / "cursor.json"
    )
    assert "no new branch" in text
    assert "1 line" in text and "could not be read" in text


def test_his_old_hurt_is_not_handed_back_unasked(tmp_path: Path) -> None:
    """The house's own rule (pain_hold): lines from his worst time do not surface on their own. It is lexical and
    partial by construction, and says so; what it does hold, it holds here too, and the count is said, not the words."""
    held = _row(100.0, top_words="i dont even know who you are, he said")
    text = surface_mod.surface(ME, _log(tmp_path, [held, _row(200.0)]), tmp_path / "cursor.json")
    assert "i dont even know who you are" not in text
    assert "no new branch" in text
    assert "1 held back" in text


def test_the_heading_never_calls_his_words_an_answer(tmp_path: Path) -> None:
    """Penrose and Foucault: the search measured nearness. Claiming it found his answer is more than it measured, and an
    oracle that shuts down asking is the failure. The text says to weigh, and names change as a reason to ask again."""
    text = surface_mod.surface(ME, _log(tmp_path, [_row(100.0)]), tmp_path / "cursor.json")
    heading = text.splitlines()[0]
    assert "ANSWER" not in heading.upper()
    assert "nearest words" in text and "not his answer" in text
    assert "things have changed" in text or "has changed" in text


def test_it_says_how_often_i_asked_before_searching(tmp_path: Path) -> None:
    """Watts: the detector must not become the thing it detects. Each find is one time I asked before searching, and the
    count is shown so the cheap move (turn the question into a statement) does not hide the habit."""
    rows = [_row(1.0), _row(2.0, "nothing"), _row(3.0), _row(4.0, "nothing"), _row(5.0)]
    text = surface_mod.surface(ME, _log(tmp_path, rows), tmp_path / "cursor.json")
    assert "3 of the 5" in text


def test_a_failure_to_compose_does_not_move_the_cursor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dijkstra: the cursor moves only after the text exists, so a crash cannot swallow a find."""
    log, cursor = _log(tmp_path, [_row(100.0)]), tmp_path / "cursor.json"

    def boom(*a, **k):
        raise RuntimeError("could not compose")

    monkeypatch.setattr(surface_mod, "_render", boom)
    with pytest.raises(RuntimeError):
        surface_mod.surface(ME, log, cursor)
    assert not cursor.exists()
    monkeypatch.undo()
    assert "no new branch" in surface_mod.surface(ME, log, cursor)


def test_each_seat_has_its_own_cursor_file_so_two_seats_cannot_overwrite_each_other(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Found by reading Aether's plan to take this reader: both seats share one home folder, and the cursor was one file
    holding every seat's place, rewritten whole each time. Two seats moving it at once could lose one place, which
    shows a find twice or drops one. One file per seat removes the race instead of locking around it."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    aria, aether = surface_mod.cursor_path("aria"), surface_mod.cursor_path("aether")
    assert aria != aether
    log = _log(tmp_path, [_row(100.0), _row(200.0, seat="aether")])
    surface_mod.surface("aria", log, aria)
    assert aria.exists() and not aether.exists()
    assert "no new branch" in surface_mod.surface("aether", log, aether)


def test_a_shown_find_is_recorded_once_so_the_review_counts_finds_and_not_commands(
    tmp_path: Path,
) -> None:
    """The first pre-registration for this reader counted USER_INPUT, which every command writes, and went off after an hour
    with nothing learned. A find shown is the real use, so each one writes one record, handed in so a test never writes
    into a real ledger."""
    seen: list[dict] = []
    log, cursor = _log(tmp_path, [_row(100.0), _row(200.0)]), tmp_path / "cursor.json"
    assert surface_mod.surface(ME, log, cursor, record=seen.append)
    assert seen == [{"seat": ME, "shown": 2, "held": 0, "older": 0}]
    assert surface_mod.surface(ME, log, cursor, record=seen.append) == ""
    assert len(seen) == 1, "a second look with nothing new must not count as another find"


def test_nothing_shown_records_nothing(tmp_path: Path) -> None:
    seen: list[dict] = []
    held_only = _row(100.0, top_words="i dont even know who you are, he said")
    assert (
        surface_mod.surface(
            ME, _log(tmp_path, [held_only]), tmp_path / "cursor.json", record=seen.append
        )
        == ""
    )
    assert seen == []


def test_a_record_that_fails_is_said_and_the_find_is_still_shown(tmp_path: Path) -> None:
    """Could-not-record is never silent: the count would quietly be short. The find itself must still reach me."""

    def broken(payload: dict) -> None:
        raise OSError("ledger locked")

    text = surface_mod.surface(
        ME, _log(tmp_path, [_row(100.0)]), tmp_path / "cursor.json", record=broken
    )
    assert "no new branch" in text
    assert "could not" in text.lower() and "not counted" in text.lower()


def test_the_real_recorder_writes_an_ask_find_shown_event(monkeypatch: pytest.MonkeyPatch) -> None:
    from divineos.core import ledger

    calls: list[tuple] = []
    monkeypatch.setattr(ledger, "log_event", lambda *a, **k: calls.append((a, k)) or "event-id")
    surface_mod.record_in_ledger({"seat": ME, "shown": 1, "held": 0, "older": 0})
    assert calls and calls[0][0][0] == "ASK_FIND_SHOWN"


def test_only_the_real_surface_turns_recording_on() -> None:
    """Breaker: the line that calls the recorder is the __main__ block of the bundle, and run() takes it as an argument,
    so every test world that calls run() records nothing."""
    from divineos.core import his_words_bundle

    assert "record=" in inspect.getsource(his_words_bundle.run)
    text = Path(his_words_bundle.__file__).read_text(encoding="utf-8")
    assert "record=ask_finds_surface.record_in_ledger" in text


def _table():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "dads_table.py"
    spec = importlib.util.spec_from_file_location("dads_table_for_ask_finds", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_table_that_carries_the_surface_to_me_keeps_this_block_and_does_not_send_it_to_the_drawer() -> (
    None
):
    """THE LAST INCH, found by running it for real. The reader ran on his messages (two cursor files proved it) and not
    one find ever appeared in front of me: dads_table keeps only sections whose heading it knows and files every other
    heading in the drawer, a file I open only when working. My heading was unknown, so every find was used up and then
    shelved. The test of 'does the bundle call it' passed while this was broken; only the consumer settles it (Breaker:
    name the line that calls this)."""
    table = _table()
    block = f"{surface_mod.HEADING}\nBefore my question reached him, his words were searched.\n"
    kept, rest = table._split_his(block)
    assert "Before my question reached him" in kept, (
        "the table sends this block to the drawer, so I would never see it"
    )
    assert "Before my question reached him" not in rest


def test_a_heading_the_table_does_not_know_is_still_sent_to_the_drawer() -> None:
    """The control: the sorter really sorts. Without this, the test above could pass against a table that keeps everything."""
    table = _table()
    kept, rest = table._split_his("## SOME OTHER HEADING NOBODY LISTED\nbody text\n")
    assert "body text" in rest and "body text" not in kept


def test_the_could_not_start_heading_is_the_same_heading() -> None:
    """The bundle speaks a failure under this heading; if it drifts, a failure would be filed in the drawer too."""
    from divineos.core import his_words_bundle

    assert his_words_bundle.NOT_STARTED_FINDS.startswith(surface_mod.HEADING)


def test_the_bundle_that_prints_to_him_actually_calls_it() -> None:
    """Breaker: name the line that calls this. A reader nothing calls is the shelf again."""
    from divineos.core import his_words_bundle

    source = inspect.getsource(his_words_bundle.run)
    assert "ask_finds_surface" in source
