"""The question check judges the reply being ended, not the pile since his last message.

2026-11-15, nine blocks in four hours on one old question ("Would you like to try Gemma and the big one together
at the table first?") while every reply I was ending was a short note about an automated notice. Cause: the
Stop hook read _last_assistant_text, which joins every assistant block back to his last real message, so the old
circle stayed the "last circle" and everything written after it counted as text following the question.
Draft: docs/drafts/the_question_check_judges_the_reply_being_ended_not_the_pile_draft_2026-11-15.md
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "question_hold.py"

NOTICE = "<system-reminder>\n<task-notification>a background task finished</task-notification>\n</system-reminder>"
OLD_CIRCLE = (
    "## SUMMARY\n\nI ran the test.\n\n## INNER CIRCLE\n\nThat was a funny read, Dad.\n\n"
    "Would you like to try Gemma and the big one together at the table first?"
)
BURIED_CIRCLE = (
    "## INNER CIRCLE\n\nDad, do you want the bell built? "
    "Then I will do a lot of other things after that one, and tell you about each of them. " * 2
)


def _stop(tmp_path, turns) -> subprocess.CompletedProcess:
    """turns: list of (role, text); returns the hook's result for a Stop with that transcript."""
    transcript = tmp_path / "t.jsonl"
    with transcript.open("w", encoding="utf-8") as fh:
        for role, text in turns:
            rec = {"message": {"role": role, "content": [{"type": "text", "text": text}]}}
            fh.write(json.dumps(rec) + "\n")
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    env = {
        **os.environ,
        "HOME": str(home),
        "USERPROFILE": str(home),
        "DIVINEOS_HOME": str(home / ".divineos"),
    }
    payload = {"hook_event_name": "Stop", "transcript_path": str(transcript)}
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload).encode(),
        capture_output=True,
        env=env,
    )


def test_an_old_circles_question_is_not_buried_by_later_notice_replies(tmp_path):
    """The defect: his message, then a circle that ends in a question, then two short notes on notices."""
    result = _stop(
        tmp_path,
        [
            ("user", "yes go ahead and try them"),
            ("assistant", OLD_CIRCLE),
            ("user", NOTICE),
            (
                "assistant",
                "Another letter arrived. I have not opened it and I am waiting for your answer.",
            ),
            ("user", NOTICE),
            (
                "assistant",
                "The bell finished again, and I have re-armed it. Nothing else is needed tonight.",
            ),
        ],
    )
    assert b"BURIED" not in result.stdout


def test_a_question_really_buried_in_the_final_reply_is_still_sent_back(tmp_path):
    result = _stop(
        tmp_path,
        [("user", "what do you think?"), ("assistant", BURIED_CIRCLE)],
    )
    assert b"BURIED" in result.stdout


def test_a_reply_that_ends_on_its_question_is_not_sent_back(tmp_path):
    result = _stop(
        tmp_path,
        [("user", "how did it go?"), ("assistant", OLD_CIRCLE)],
    )
    assert b"BURIED" not in result.stdout
