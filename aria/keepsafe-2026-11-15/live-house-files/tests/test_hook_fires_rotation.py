"""The router's firing log is trimmed by the house's own rotation, and a refusal is never what gets trimmed.

Dad, 2026-11-11: "why is the notebook 200k lines?" and "is this a temporary file? or something that builds every day?".
It builds every day (about 22,000 rows) and nothing emptied it: hook_fires.jsonl was on none of the four policies, and
the root-cause check re-reads the whole file on every decision edit. Three quarters of it is the words nothing-to-say.

The walk (walk-4d4e6d6a08b9) set the shape: quiet states fold to a count in the roster, every other state is signal and
is never dropped, because the root-cause check finds an open refusal by reading this log and a trimmed refusal would
mark a fix as investigated by deleting the evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

from divineos.core import log_rotation as lr

NAME = "hook_fires.jsonl"


def _row(surface: str, state: str, t: float = 1.0, **extra: object) -> dict:
    return {"t": t, "event": "PreToolUse", "surface": surface, "state": state, **extra}


def _write(home: Path, rows: list[dict]) -> Path:
    path = home / NAME
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return path


def _policy() -> lr.LogPolicy:
    found = [p for p in lr.POLICIES if p.filename == NAME]
    assert found, "hook_fires.jsonl has no rotation policy, so it grows forever"
    return found[0]


def _kept(path: Path) -> list[dict]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def test_the_log_has_a_rotation_policy_and_the_sleep_cycle_reaches_it(tmp_path: Path) -> None:
    _policy()
    _write(tmp_path, [_row("a", "nothing-to-say")])
    names = [r.name for r in lr.rotate_all(home=tmp_path, min_bytes=0)]
    assert NAME in names


def test_quiet_rows_fold_to_counts_and_leave_the_log(tmp_path: Path) -> None:
    rows = (
        [_row("door_a", "nothing-to-say")] * 3
        + [_row("door_a", "none")]
        + [_row("door_a", "refused", file="x.py")]
    )
    path = _write(tmp_path, rows)
    result = lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    assert result.rotated
    assert [r["state"] for r in _kept(path)] == ["refused"]
    roster = json.loads(lr.roster_path(tmp_path, NAME).read_text(encoding="utf-8"))
    assert roster["door_a"]["nothing-to-say"] == 3
    assert roster["door_a"]["none"] == 1
    assert roster["door_a"]["refused"] == 1, (
        "the signal row is counted too, so the tally is the whole story"
    )


def test_an_old_unclosed_refusal_survives_any_amount_of_quiet(tmp_path: Path) -> None:
    refusal = _row(
        "work_item_doorman", "refused", t=5.0, file="src/divineos/core/x.py", seat="aether"
    )
    path = _write(
        tmp_path, [refusal] + [_row("q", "nothing-to-say", t=float(i)) for i in range(60_000)]
    )
    lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    assert any(
        r.get("file") == "src/divineos/core/x.py" and r["state"] == "refused" for r in _kept(path)
    )


def test_every_non_quiet_state_is_kept(tmp_path: Path) -> None:
    states = ["spoke", "refused", "errored", "refused-downgraded", "undeclared"]
    path = _write(tmp_path, [_row("d", s) for s in states] + [_row("d", "nothing-to-say")])
    lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    assert [r["state"] for r in _kept(path)] == states


def test_a_row_with_no_state_is_kept_because_unclassified_is_signal(tmp_path: Path) -> None:
    path = _write(
        tmp_path, [{"t": 1.0, "event": "Stop", "surface": "s"}, _row("d", "nothing-to-say")]
    )
    lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    assert [r.get("surface") for r in _kept(path)] == ["s"]


def test_an_empty_log_and_a_one_row_log_rotate_without_error(tmp_path: Path) -> None:
    (tmp_path / NAME).write_text("", encoding="utf-8")
    assert lr.rotate_log(_policy(), home=tmp_path, min_bytes=0).name == NAME
    _write(tmp_path, [_row("d", "refused", file="a.py")])
    assert lr.rotate_log(_policy(), home=tmp_path, min_bytes=0).rotated


def test_a_second_rotation_adds_to_the_counts_instead_of_replacing_them(tmp_path: Path) -> None:
    _write(tmp_path, [_row("d", "nothing-to-say")] * 4)
    lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    _write(tmp_path, [_row("d", "nothing-to-say")] * 6)
    lr.rotate_log(_policy(), home=tmp_path, min_bytes=0)
    roster = json.loads(lr.roster_path(tmp_path, NAME).read_text(encoding="utf-8"))
    assert roster["d"]["nothing-to-say"] == 10
