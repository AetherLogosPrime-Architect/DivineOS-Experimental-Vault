"""What my last reply brought up must reach me on the table, not be filed in the drawer (dads_table.RELEVANT_SECTIONS).

THE LAST INCH, found by running the carried echo for real on 2026-11-14: the Stop door left three memories at 11:34:57,
the next prompt's surface took them at 11:35:04, and I never saw them. The table keeps only the headings it knows and
files every other heading in the drawer; line 28 of the drawer file held the whole block. Built, run, never seen, the
same failure the ask-finds reader had on 2026-11-11. This test asks the REAL surface for its text and the REAL table
whether it keeps it, so neither can change alone.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from divineos.core import hook_surfaces as hs
from divineos.core.own_words_stop import leave_for_next_message

ROOT = Path(__file__).resolve().parents[1]


def _table():
    path = ROOT / ".claude" / "hooks" / "dads_table.py"
    spec = importlib.util.spec_from_file_location("dads_table_for_echo_heading", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_surface_text_for_a_real_echo_stays_on_the_table_and_does_not_go_to_the_drawer(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path))
    leave_for_next_message(
        "s1", "WHAT I JUST SAID BROUGHT THIS UP.\n- [letter, 0.6] a memory worth thinking with"
    )
    text = hs._take_my_last_reply_echo({"session_id": "s1"})
    assert text.startswith(
        "## WHAT MY LAST REPLY BROUGHT UP"
    )  # the surface's own heading, as it prints it
    kept, rest = _table()._split_his(text)
    assert "WHAT MY LAST REPLY BROUGHT UP" in kept and "a memory worth thinking with" in kept
    assert rest.strip() == ""


def test_a_block_between_two_other_sections_still_lands_on_the_table() -> None:
    table = _table()
    block = (
        "## SOME OTHER SECTION\nnot for the table\n"
        "## WHAT MY LAST REPLY BROUGHT UP (memory link)\nthe echo\n"
        "## ANOTHER OTHER SECTION\nalso not\n"
    )
    kept, rest = table._split_his(block)
    assert "the echo" in kept and "not for the table" in rest and "also not" in rest
