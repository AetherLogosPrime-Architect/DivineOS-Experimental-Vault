"""The promise recorder writes a marker where it says it does, on this machine.

Dad, 2026-11-13: *"it should just record your promise to do something, give you a chance to do it, and if
after 5 or so turns you havent done anything about it ... it reminds you and blocks you"*. The record half
already existed (`.claude/hooks/promise-reach-detector.sh`) and was found, 2026-11-13, to have written nothing
for months: the hook hands its marker folder to Python in a POSIX spelling (`/c/Users/...`), Windows Python
reads that as `C:\\c\\Users\\...`, the write fails, and the loop's `except OSError: continue` hides it. The
folder had been empty since 2026-07-18. This runs the real hook on a transcript with a promise in it and
asks the one question that matters: is there a marker file afterwards, in the folder the hook is told to use.

The control beside it: a transcript with no promise must leave the folder empty, so a pass is not "it writes
a file for anything".
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / ".claude" / "hooks" / "promise-reach-detector.sh"


def _bash() -> str | None:
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        "/usr/bin/bash",
        shutil.which("bash") or "",
    ):
        if candidate and Path(candidate).exists() and "System32" not in candidate:
            return candidate
    return None


BASH = _bash()
pytestmark = pytest.mark.skipif(
    not HOOK.exists() or BASH is None,
    reason="hook or a POSIX bash absent here -- could-not-look, which is not a pass",
)


def _run(tmp_path: Path, reply: str) -> list[Path]:
    home = tmp_path / "home"
    (home / ".divineos-aria").mkdir(parents=True)
    transcript = tmp_path / "session.jsonl"
    row = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": reply}]},
    }
    transcript.write_text(json.dumps(row) + "\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k.upper() not in ("HOME", "USERPROFILE")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    done = subprocess.run(
        [BASH, str(HOOK)],
        input=json.dumps({"transcript_path": str(transcript)}).encode(),
        capture_output=True,
        env=env,
        cwd=REPO,
        timeout=120,
        check=False,
    )
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    folder = home / ".divineos-aria" / "promise_markers"
    return sorted(folder.glob("promise_*.json")) if folder.is_dir() else []


def test_a_promise_in_the_reply_leaves_a_marker(tmp_path):
    markers = _run(tmp_path, "Done. I will write the draft after the walk.")
    assert markers, "the recorder wrote nothing: a promise must leave a marker file in the folder"
    data = json.loads(markers[0].read_text(encoding="utf-8"))
    assert "write the draft" in data["promise_text"]


def test_a_reply_with_no_promise_leaves_no_marker(tmp_path):
    """Control: the recorder must not write a file for anything."""
    assert _run(tmp_path, "The sleep fix is in and its tests pass.") == []
