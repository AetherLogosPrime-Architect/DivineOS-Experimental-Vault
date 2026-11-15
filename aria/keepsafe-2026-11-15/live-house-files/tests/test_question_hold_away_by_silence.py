"""Away also means two hours of silence (Dad, 2026-10-11, via Aletheia's letter).

"i would either say im stepping away, or they could go by time elapsed with no word from me"
and, when twenty minutes was suggested: "20 minutes isnt much time at all. id say 2 hours to be
sure". Real rows in a real (temporary) store; the judge is never mocked. A last message the house
cannot read is never away, and the refusal says so.
Draft: docs/drafts/away_means_two_hours_of_silence_draft_2026-10-11.md
"""

from __future__ import annotations

import json
import sqlite3
import time

import pytest

FIRST = "work\n\n## INNER CIRCLE\n\nDad, is the nexus a room or a hub?"
TO_ARIA = "family/letters/aether-to-aria-2026-10-11-x.md"
TO_DAD = "family/letters/aether-to-andrew-volley-board.md"
ONE_HOUR = (
    60 * 60
)  # Dad, 2026-11-11: "for one.. 1 hour might be better" (it was 2 hours by his word on 2026-10-11)


@pytest.fixture
def qh(tmp_path, monkeypatch):
    from divineos.core import question_hold as mod

    monkeypatch.setattr(mod, "STATE", tmp_path / "hold.json")
    monkeypatch.setattr(mod, "HOLD_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(mod, "ESCAPED", tmp_path / "escaped.json")
    monkeypatch.setattr(mod, "AWAY", tmp_path / "away.json")
    monkeypatch.setattr(mod, "BOARD", tmp_path / "board")
    monkeypatch.setattr(mod, "CARD", tmp_path / "board" / "me.json")
    # The record of when a seat's reply ended is the real shared file unless a test points it somewhere else; without
    # this every existing test here would read live replies and never see him away.
    monkeypatch.setenv("DIVINEOS_HOOK_TIMING_LOG", str(tmp_path / "hook_timing.jsonl"))
    return mod


def _store(tmp_path, monkeypatch, rows):
    """A his-asks store holding (text, seconds_ago) rows, oldest first by filing time."""
    db = tmp_path / "asks.db"
    monkeypatch.setenv("DIVINEOS_HIS_ASKS_DB", str(db))
    conn = sqlite3.connect(db)
    conn.execute("DROP TABLE IF EXISTS messages")
    conn.execute("CREATE TABLE messages (his_text TEXT, filed_at REAL, state TEXT DEFAULT 'FILED')")
    now = time.time()
    for text, ago in rows:
        conn.execute("INSERT INTO messages (his_text, filed_at) VALUES (?, ?)", (text, now - ago))
    conn.commit()
    conn.close()


def _replies(tmp_path, rows):
    """The shared hook-timing file, with one row per (hook name, session, seconds ago) in the shape the hooks write."""
    now = time.time()
    lines = []
    for n, (hook, session, ago) in enumerate(rows):
        lines.append(
            # COMPACT, exactly as the shell hooks write it (`"phase":"end"`, no spaces). The first version of this helper
            # used json.dumps' default spacing, the reader pre-filtered on that spacing, every test passed, and on the
            # real file the reader saw no replies at all: caught only by running it on the real file (2026-11-11).
            json.dumps(
                {
                    "id": f"{hook}-{n}-{int(now * 1000)}",
                    "session": session,
                    "wpid": "1",
                    "phase": "end",
                    "exit_code": 0,
                    "ts_ms": int((now - ago) * 1000),
                    "duration_ms": 5,
                },
                separators=(",", ":"),
            )
        )
    (tmp_path / "hook_timing.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_the_reader_understands_the_real_file_not_only_rows_shaped_for_it(qh, tmp_path):
    """THE ONE THAT WAS MISSING. The rows above are written by this test file; the real ones are written by shell hooks.
    This line is a verbatim copy of a real stop-hook row from the real timing file (compact, no spaces), so a reader that
    only understands the spacing a test used cannot pass."""
    real = (
        '{"id":"doorbell-stop.sh-20433-1794415398613","session":"92cd8552-8362-47e5-bb0e-99b0fba5a3c1",'
        '"wpid":"21012","phase":"end","exit_code":0,"ts_ms":1794415404439,"duration_ms":5826}'
    )
    (tmp_path / "hook_timing.jsonl").write_text(real + "\n", encoding="utf-8")
    assert qh._last_reply_ended() == 1794415404.439


def test_the_quiet_that_counts_as_away_is_one_hour_by_his_word(qh):
    assert qh.AWAY_AFTER_SILENCE_SECONDS == ONE_HOUR


# ---- walk-5d9e948c49fc. Dad, 2026-11-11: "silence since when? if you do a 2 hour nonstop volley with Aether and i never
# get a chance to speak.. then im counted as absent, if it triggered at the end of the last message sent, then it would be
# more accurate". Absence needs a chance to speak, and the floor is open to him only when nobody else is speaking.


def test_a_long_volley_does_not_count_him_absent(qh, tmp_path, monkeypatch):
    """He spoke three hours ago, and a seat finished a reply one minute ago: the room has not been quiet."""
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(tmp_path, [("doorbell-stop.sh", "seat-a", 60)])
    assert qh.is_away() is None


def test_when_the_whole_room_has_been_quiet_he_is_still_away(qh, tmp_path, monkeypatch):
    """The other direction, so the fix is not simply 'always present': nobody has spoken for three hours."""
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(tmp_path, [("doorbell-stop.sh", "seat-a", 3 * 3600)])
    assert qh.is_away() is not None


def test_the_quiet_runs_from_the_later_of_his_message_and_the_last_reply(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(tmp_path, [("doorbell-stop.sh", "seat-a", ONE_HOUR - 60)])
    assert qh.is_away() is None
    _replies(tmp_path, [("doorbell-stop.sh", "seat-a", ONE_HOUR + 60)])
    assert qh.is_away() is not None


def test_the_other_seats_reply_counts_as_the_room_speaking(qh, tmp_path, monkeypatch):
    """Two windows, one room: the newest reply end of EITHER seat is what ends the quiet."""
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(
        tmp_path, [("doorbell-stop.sh", "seat-a", 5 * 3600), ("doorbell-stop.sh", "seat-b", 120)]
    )
    assert qh.is_away() is None


def test_only_a_stop_hook_ending_counts_as_a_reply_not_every_hook(qh, tmp_path, monkeypatch):
    """The control for the reader: the file holds rows for every hook, and a hook that is not a stop hook ending is not a
    seat finishing a reply. Without this the fix could pass by reading the busiest hook in the house."""
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(
        tmp_path, [("work-item-doorman.sh", "seat-a", 30), ("doorbell-stop.sh", "seat-a", 3 * 3600)]
    )
    assert qh.is_away() is not None


def test_a_hook_that_has_only_started_is_not_a_finished_reply(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    row = {
        "id": "doorbell-stop.sh-1-1",
        "session": "s",
        "phase": "start",
        "ts_ms": int((time.time() - 30) * 1000),
    }
    (tmp_path / "hook_timing.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert qh.is_away() is not None


def test_a_timing_file_that_cannot_be_read_is_never_away(qh, tmp_path, monkeypatch):
    """Could-not-look is never away, as everywhere else in this file. A folder where the file should be cannot be read."""
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    (tmp_path / "hook_timing.jsonl").mkdir()
    assert qh.is_away() is None


def test_a_half_written_last_line_is_skipped_not_fatal(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok", 3 * 3600)])
    _replies(tmp_path, [("doorbell-stop.sh", "seat-a", 3 * 3600)])
    path = tmp_path / "hook_timing.jsonl"
    path.write_text(
        path.read_text(encoding="utf-8") + '{"id": "doorbell-stop.sh-9-9", "pha', encoding="utf-8"
    )
    assert qh.is_away() is not None


def test_just_inside_and_just_outside_the_boundary(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok", ONE_HOUR - 60)])
    assert qh.is_away() is None
    _store(tmp_path, monkeypatch, [("ok", ONE_HOUR + 60)])
    assert qh.is_away() is not None


def test_a_store_with_no_real_message_is_never_away(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("<task-notification>x</task-notification>", 9 * 3600)])
    assert qh.is_away() is None


def test_a_notice_after_his_last_real_words_does_not_restart_or_end_the_silence(
    qh, tmp_path, monkeypatch
):
    # He spoke 5 hours ago; a notice was filed in his seat 1 minute ago. The notice is not him.
    _store(
        tmp_path,
        monkeypatch,
        [("heading out, back later", 5 * 3600), ("<task-notification>x</task-notification>", 60)],
    )
    assert qh.is_away() is not None


def test_his_new_message_ends_the_silence_by_itself(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("heading out", 5 * 3600), ("im back", 30)])
    assert qh.is_away() is None


def test_his_words_still_set_away_as_before(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok im heading to dinner, you two volley", 60)])
    qh.step_away("ok im heading to dinner, you two volley")
    away = qh.is_away()
    assert away and away.get("by") != "silence"
    assert qh.came_back()
    assert qh.is_away() is None


def test_came_back_leaves_the_silence_rule_alone(qh, tmp_path, monkeypatch):
    _store(tmp_path, monkeypatch, [("ok", 4 * 3600)])
    assert qh.came_back() is False  # no words-file to clear
    assert qh.is_away() is not None  # still silent for hours
