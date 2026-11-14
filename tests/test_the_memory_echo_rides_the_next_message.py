"""The memory echo rides in with his next message instead of stopping me after the reply.

Dad, 2026-11-12: the trouble is the LINE of stops, and the OS should hand me the memory before I write. On
2026-11-14, 108 of 252 Stop deliveries on my seat (43%) were the memory-link echo. The Stop door now leaves
its message in a small pending store in the seat's own home; the next prompt's memory-link surface takes it,
prints it once, and clears it. A drop in stops with nothing arriving would be a shelf, so these tests pin the
ARRIVAL as well as the removal.
"""

from __future__ import annotations

from types import SimpleNamespace

from divineos.core import own_words_stop as ow
from divineos.core.hook_surfaces import memory_link_surface

DAY = 24 * 3600
ECHO = (
    "WHAT I JUST SAID BROUGHT THIS UP. The memory link searched my own words, not his, and this is what it "
    "holds that bears on them:\n- [knowledge, 0.61] a note is not a fix, wire it (x.md)\n"
    "If it bears on what I just said or am about to do, I open its source and act on it now, and tell him "
    "in plain words if it changes anything. It is for me to think with; I never quote it back to him."
)


def _empty_link(monkeypatch):
    import divineos.core.memory_linkage as ml

    monkeypatch.setattr(
        ml, "compose_block", lambda *a, **k: SimpleNamespace(text="", could_not_run=None)
    )


def test_a_message_left_by_the_stop_door_is_printed_once_with_his_next_message(
    tmp_path, monkeypatch
) -> None:
    _empty_link(monkeypatch)
    store = tmp_path / "pending.json"
    monkeypatch.setattr(ow, "default_pending_file", lambda: store)
    ow.leave_for_next_message("s1", ECHO)

    first = memory_link_surface({"prompt": "hello there dad", "session_id": "s1"})
    assert first is not None and first.output
    assert "WHAT MY LAST REPLY BROUGHT UP" in first.output
    assert "a note is not a fix, wire it" in first.output
    assert (
        "act on it now" not in first.output
    )  # the line that made each Stop hold cost another reply
    assert "never quote it back to him" in first.output

    second = memory_link_surface({"prompt": "hello there dad", "session_id": "s1"})
    assert not (second and second.output)


def test_one_sessions_pending_message_is_not_printed_to_another_session(
    tmp_path, monkeypatch
) -> None:
    _empty_link(monkeypatch)
    monkeypatch.setattr(ow, "default_pending_file", lambda: tmp_path / "pending.json")
    ow.leave_for_next_message("seat-a", ECHO)

    other = memory_link_surface({"prompt": "hello there dad", "session_id": "seat-b"})
    assert not (other and other.output)
    mine = memory_link_surface({"prompt": "hello there dad", "session_id": "seat-a"})
    assert mine and "a note is not a fix" in mine.output


def test_an_old_session_is_dropped_and_a_live_one_kept(tmp_path) -> None:
    store = tmp_path / "pending.json"
    ow.leave_for_next_message("old", "stale", store, now=1_000.0)
    ow.leave_for_next_message("live", "fresh", store, now=1_000.0 + DAY + 60)

    assert ow.take_for_next_message("old", store, now=1_000.0 + DAY + 61) == []
    assert ow.take_for_next_message("live", store, now=1_000.0 + DAY + 61) == ["fresh"]


def test_three_items_survive_for_a_live_session_and_take_clears_them(tmp_path) -> None:
    store = tmp_path / "pending.json"
    for n in range(5):
        ow.leave_for_next_message("s1", f"item {n}", store, now=1_000.0 + n)

    assert ow.take_for_next_message("s1", store, now=1_100.0) == ["item 2", "item 3", "item 4"]
    assert ow.take_for_next_message("s1", store, now=1_101.0) == []


def test_an_empty_message_is_never_stored(tmp_path) -> None:
    store = tmp_path / "pending.json"
    ow.leave_for_next_message("s1", "   ", store, now=1_000.0)

    assert ow.take_for_next_message("s1", store, now=1_001.0) == []
    assert not store.exists()


def test_an_unreadable_store_reads_as_nothing_pending_and_a_save_makes_it_whole(tmp_path) -> None:
    store = tmp_path / "pending.json"
    store.write_text("{not json", encoding="utf-8")

    assert ow.take_for_next_message("s1", store) == []
    ow.leave_for_next_message("s1", "after the break", store, now=2_000.0)
    assert ow.take_for_next_message("s1", store, now=2_001.0) == ["after the break"]
