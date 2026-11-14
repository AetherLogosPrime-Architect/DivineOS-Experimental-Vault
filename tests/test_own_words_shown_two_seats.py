"""Two seats share one home, so one seat's save must not erase the other's shown-list.

Found 2026-11-14: own_words_shown.json held ONE session at a time, so each seat's save wiped the other's
entry and the same memories were handed back again and again.
"""

from __future__ import annotations

import json

from divineos.core import own_words_stop as ow

DAY = 24 * 3600


def test_two_sessions_saving_in_turn_both_survive(tmp_path) -> None:
    state = tmp_path / "shown.json"
    ow._save_shown("seat-a-session", {"k1", "k2"}, state, now=1_000.0)
    ow._save_shown("seat-b-session", {"k3"}, state, now=1_010.0)

    assert ow._load_shown("seat-a-session", state) == {"k1", "k2"}
    assert ow._load_shown("seat-b-session", state) == {"k3"}


def test_saving_again_for_one_session_adds_to_its_own_list_only(tmp_path) -> None:
    state = tmp_path / "shown.json"
    ow._save_shown("a", {"k1"}, state, now=1_000.0)
    ow._save_shown("b", {"k9"}, state, now=1_001.0)
    ow._save_shown("a", {"k1", "k2"}, state, now=1_002.0)

    assert ow._load_shown("a", state) == {"k1", "k2"}
    assert ow._load_shown("b", state) == {"k9"}


def test_a_session_idle_over_a_day_is_dropped_but_a_quiet_one_inside_a_day_is_kept(
    tmp_path,
) -> None:
    state = tmp_path / "shown.json"
    ow._save_shown("old", {"k1"}, state, now=1_000.0)
    ow._save_shown("quiet", {"k2"}, state, now=1_000.0 + DAY - 60)
    ow._save_shown("live", {"k3"}, state, now=1_000.0 + DAY + 60)

    assert ow._load_shown("old", state) == set()
    assert ow._load_shown("quiet", state) == {"k2"}
    assert ow._load_shown("live", state) == {"k3"}


def test_the_three_files_live_in_the_seats_own_home_not_the_shared_one() -> None:
    """Aria 2026-11-14: Path.home()/.divineos put both seats in one file; divineos_home() splits them."""
    from divineos.core import ask_after_his_words as ask
    from divineos.core.paths import divineos_home

    home = divineos_home()
    assert ow.default_state_file().parent == home
    assert ow.default_log_file().parent == home
    assert ask.default_log_file().parent == home


def test_the_old_import_time_constants_are_gone_so_no_caller_reads_a_stale_path() -> None:
    """A constant is fixed at import and ignores a home set afterwards; callers must use the functions."""
    from divineos.core import ask_after_his_words as ask

    assert not hasattr(ow, "STATE_FILE") and not hasattr(ow, "LOG_FILE")
    assert not hasattr(ask, "LOG_FILE")


def test_an_old_format_file_with_plain_lists_still_loads(tmp_path) -> None:
    state = tmp_path / "shown.json"
    state.write_text(json.dumps({"legacy": ["k1", "k2"]}), encoding="utf-8")

    assert ow._load_shown("legacy", state) == {"k1", "k2"}
    ow._save_shown("new", {"k3"}, state, now=5_000.0)
    assert ow._load_shown("new", state) == {"k3"}
