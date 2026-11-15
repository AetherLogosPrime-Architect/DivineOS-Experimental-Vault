"""No fix without a root cause: a decision edit to a file with an open failure fact is refused until a root-cause record
cites something READ after the failure, and that thing is the failing file or its test. Written BEFORE the code
(walk-f7b48c9845f9, Knuth: the empty cases decide whether it works). Real files, a real transcript, no stubs."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from divineos.core import root_cause_before_fix as rc

ROOT = Path(__file__).resolve().parents[1]
FAILING = "src/divineos/core/ask_after_his_words.py"
OTHER = "src/divineos/core/walk_after_his_message.py"
DECISION_EDIT = {
    "file_path": str(ROOT / FAILING),
    "old_string": '    if not shown:\n        return "nothing", None\n',
    "new_string": '    if not shown or (x and y):\n        return "nothing", None\n',
}


@pytest.fixture()
def store(tmp_path, monkeypatch) -> Path:
    # One record, not two: refusals live in the router's log (here a temp file); the store keeps only closing records.
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(tmp_path / "hook_fires.jsonl"))
    monkeypatch.setattr(rc, "LIVENESS", tmp_path / "default_live.jsonl")
    return tmp_path / "failure_facts.jsonl"


def _stamp(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _transcript(tmp_path: Path, reads: list[tuple[float, str]]) -> str:
    """A real harness-shaped transcript where each (time, path) is a Read tool call by the assistant."""
    lines = []
    for when, path in reads:
        lines.append(
            json.dumps(
                {
                    "type": "assistant",
                    "timestamp": _stamp(when),
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Read",
                                "input": {"file_path": str(ROOT / path)},
                            }
                        ],
                    },
                }
            )
        )
    path = tmp_path / "t.jsonl"
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)


def test_a_failure_fact_with_no_file_owes_nothing(store) -> None:
    assert rc.record_failure("door-refusal", None, "aria") is False
    assert not (store.parent / "hook_fires.jsonl").exists()


def test_a_decision_edit_with_no_failure_fact_is_not_touched(store) -> None:
    state, _ = rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)
    assert state == "not-applicable"


def test_a_decision_edit_to_a_file_with_an_open_failure_fact_is_owed(store) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    state, message = rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)
    assert state == "owed" and FAILING in message and "root cause" in message.lower()


def test_a_fact_on_one_file_never_holds_another_file(store) -> None:
    rc.record_failure("door-refusal", OTHER, "aria")
    assert rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)[0] == "not-applicable"


def test_a_failure_fact_by_one_seat_never_owes_the_other(store) -> None:
    rc.record_failure("door-refusal", FAILING, "aether")
    assert rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)[0] == "not-applicable"


def test_a_harmless_edit_to_a_file_with_an_open_fact_is_not_touched(store) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    harmless = {
        "file_path": str(ROOT / FAILING),
        "old_string": "MAX_SHOWN = 2\n",
        "new_string": "MAX_SHOWN = 3\n",
    }
    assert rc.check_edit("Edit", harmless, ROOT, "aria", store=store)[0] == "not-applicable"


@pytest.mark.parametrize(
    "text, evidence, why",
    [
        ("", FAILING, "empty text"),
        ("too short", FAILING, "text under forty characters"),
        (
            "the cause was the missing check on the question being asked early",
            None,
            "no evidence path",
        ),
        (
            "the cause was the missing check on the question being asked early",
            "src/divineos/nope.py",
            "path does not exist",
        ),
    ],
)
def test_a_root_cause_record_with_nothing_behind_it_is_refused(
    store, tmp_path, text, evidence, why
) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    tr = _transcript(tmp_path, [(time.time() + 5, FAILING)])
    result = rc.file_root_cause(FAILING, text, evidence, "aria", tr, store=store)
    assert result.state == "refused", why


def test_evidence_read_before_the_failure_does_not_count(store, tmp_path) -> None:
    tr = _transcript(tmp_path, [(time.time() - 60, FAILING)])  # read, then it failed
    rc.record_failure("door-refusal", FAILING, "aria")
    result = rc.file_root_cause(
        FAILING,
        "the cause was an assumption about when the hook fires",
        FAILING,
        "aria",
        tr,
        store=store,
    )
    assert result.state == "refused" and "after" in result.why


def test_evidence_that_is_not_the_failing_file_or_its_test_is_refused(store, tmp_path) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    tr = _transcript(tmp_path, [(time.time() + 5, OTHER)])
    result = rc.file_root_cause(
        FAILING,
        "the cause was an assumption about when the hook fires",
        OTHER,
        "aria",
        tr,
        store=store,
    )
    assert result.state == "refused" and "failing file or its test" in result.why


def test_a_record_citing_the_failing_file_read_after_the_failure_is_accepted_and_the_edit_goes_through(
    store, tmp_path
) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    tr = _transcript(tmp_path, [(time.time() + 5, FAILING)])
    result = rc.file_root_cause(
        FAILING,
        "the cause was an assumption about when the hook fires",
        FAILING,
        "aria",
        tr,
        store=store,
    )
    assert result.state == "accepted"
    assert rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)[0] == "not-applicable"


def test_the_test_of_the_failing_file_counts_as_evidence(store, tmp_path) -> None:
    rc.record_failure("door-refusal", FAILING, "aria")
    its_test = "tests/test_ask_after_his_words.py"
    tr = _transcript(tmp_path, [(time.time() + 5, its_test)])
    result = rc.file_root_cause(
        FAILING,
        "the cause was an assumption about when the hook fires",
        its_test,
        "aria",
        tr,
        store=store,
    )
    assert result.state == "accepted"


def test_the_liveness_row_is_written_before_anything_that_can_fail(store, tmp_path) -> None:
    # Aether's thin spot: a door that errors before writing is blind exactly when it is broken.
    live = tmp_path / "live.jsonl"
    rc.record_failure("door-refusal", FAILING, "aria")
    rc.liveness_started(
        "Edit", "aria", liveness=live
    )  # the door's first act, before decide() can fail
    # now the evaluation itself dies: an unreadable store file raises inside check_edit
    store.write_bytes(b"\xff\xfe not json at all")
    with pytest.raises(
        UnicodeDecodeError
    ):  # the door's caller catches this and stands aside, saying so
        rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store, liveness=live)
    rows = [json.loads(x) for x in live.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["state"] == "started"
    # and a call that is not an edit leaves no row, so the count stays readable
    rc.liveness_started("Bash", "aria", liveness=tmp_path / "bash_live.jsonl")
    assert not (tmp_path / "bash_live.jsonl").exists()


def _held_payload(tmp_path: Path) -> str:
    """A real decision edit with no draft, walk or search behind it, so the build-flow door must hold it."""
    return json.dumps(
        {"tool_name": "Edit", "session_id": "t", "transcript_path": "", "tool_input": DECISION_EDIT}
    )


def test_a_refusal_by_the_build_flow_door_is_one_row_in_the_routers_log_with_the_file_and_the_seat(
    tmp_path, monkeypatch
) -> None:
    # One record, not two (Aether 2026-11-11): the router already writes {t, event, surface, state} per door, and the
    # build-flow doorman is a standalone hook it never sees. Same row shape, plus file and seat.
    from divineos.core import work_item_doorman as door

    fires = tmp_path / "hook_fires.jsonl"
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(fires))
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(rc, "STORE", tmp_path / "failure_facts.jsonl")
    monkeypatch.setattr(rc, "LIVENESS", tmp_path / "live.jsonl")
    decision = door.gate_from_stdin(_held_payload(tmp_path))
    assert decision.state.name == "HELD"
    rows = [json.loads(x) for x in fires.read_text(encoding="utf-8").splitlines()]
    row = [r for r in rows if r["surface"] == "work_item_doorman"][0]
    assert row["state"] == "refused" and row["file"] == FAILING and row["event"] == "PreToolUse"
    assert row["seat"] == rc.seat_of(ROOT) and isinstance(row["t"], float)


def test_a_call_the_door_lets_through_writes_no_refusal_row(tmp_path, monkeypatch) -> None:
    from divineos.core import work_item_doorman as door

    fires = tmp_path / "hook_fires.jsonl"
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(fires))
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(rc, "STORE", tmp_path / "failure_facts.jsonl")
    monkeypatch.setattr(rc, "LIVENESS", tmp_path / "live.jsonl")
    payload = json.dumps(
        {"tool_name": "Read", "session_id": "t", "tool_input": {"file_path": str(ROOT / FAILING)}}
    )
    assert door.gate_from_stdin(payload).state.name == "OPEN"
    assert not fires.exists() or "refused" not in fires.read_text(encoding="utf-8")


def test_the_open_fact_is_read_from_the_routers_row_and_closed_by_a_record_keyed_on_it(
    tmp_path, monkeypatch
) -> None:
    # failure_facts.jsonl keeps only OPEN/CLOSED, keyed by the router row's time and file; it never repeats the refusal.
    fires = tmp_path / "hook_fires.jsonl"
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(fires))
    store = tmp_path / "failure_facts.jsonl"
    t = round(time.time(), 3)
    fires.write_text(
        json.dumps(
            {
                "t": t,
                "event": "PreToolUse",
                "surface": "work_item_doorman",
                "state": "refused",
                "file": FAILING,
                "seat": "aria",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert [f["file"] for f in rc.open_facts(FAILING, "aria", store=store)] == [FAILING]
    tr = _transcript(tmp_path, [(t + 5, FAILING)])
    assert (
        rc.file_root_cause(
            FAILING,
            "the cause was an assumption about when the hook fires",
            FAILING,
            "aria",
            tr,
            store=store,
        ).state
        == "accepted"
    )
    assert rc.open_facts(FAILING, "aria", store=store) == []
    assert store.read_text(encoding="utf-8").count("refused") == 0


def test_one_record_closes_every_open_fact_for_the_file_not_only_the_last(store, tmp_path) -> None:
    # walk-010a093d2520 (Meadows): 291 refusals of one door is the real shape, so a file collects many open facts.
    for _ in range(3):
        rc.record_failure("build-flow-refusal", FAILING, "aria")
    tr = _transcript(tmp_path, [(time.time() + 5, FAILING)])
    assert (
        rc.file_root_cause(
            FAILING,
            "the cause was an assumption about when the hook fires",
            FAILING,
            "aria",
            tr,
            store=store,
        ).state
        == "accepted"
    )
    assert rc.open_facts(FAILING, "aria", store=store) == []


def test_a_refusal_by_the_root_cause_door_itself_writes_no_new_fact(store, tmp_path) -> None:
    # (Popper) otherwise every owed edit would add a fact on the file it already holds, and the pile grows by itself.
    fires = tmp_path / "hook_fires.jsonl"
    rc.record_failure("build-flow-refusal", FAILING, "aria")
    before = fires.read_text(encoding="utf-8").splitlines()
    state, _ = rc.check_edit("Edit", DECISION_EDIT, ROOT, "aria", store=store)
    assert state == "owed"  # the root-cause door refused...
    assert (
        fires.read_text(encoding="utf-8").splitlines() == before
    )  # ...and wrote no fact of its own
    assert not store.exists()


def test_a_missing_log_reads_as_no_facts_but_an_unreadable_one_raises(
    tmp_path, monkeypatch
) -> None:
    # (Hoare) 'nothing found' and 'could not look' are two states with two names.
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(tmp_path / "absent.jsonl"))
    assert rc.open_facts(FAILING, "aria", store=tmp_path / "also_absent.jsonl") == []
    broken = tmp_path / "broken.jsonl"
    broken.write_bytes(b"\xff\xfe not text")
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(broken))
    with pytest.raises(UnicodeDecodeError):
        rc.open_facts(FAILING, "aria", store=tmp_path / "also_absent.jsonl")


def test_a_read_in_the_same_millisecond_as_the_refusal_does_not_count_and_one_later_does(
    store, tmp_path
) -> None:
    # (Knuth) strictly after, compared on the rounding both sides use.
    t = 1_800_000_000.123
    rc._append(
        {
            "t": t,
            "event": "PreToolUse",
            "surface": "work_item_doorman",
            "state": "refused",
            "file": FAILING,
            "seat": "aria",
        },
        rc._fires_log(),
    )
    same = _transcript(tmp_path, [(t, FAILING)])
    assert (
        rc.file_root_cause(
            FAILING,
            "the cause was an assumption about when the hook fires",
            FAILING,
            "aria",
            same,
            store=store,
        ).state
        == "refused"
    )
    later = _transcript(tmp_path, [(t + 0.001, FAILING)])
    assert (
        rc.file_root_cause(
            FAILING,
            "the cause was an assumption about when the hook fires",
            FAILING,
            "aria",
            later,
            store=store,
        ).state
        == "accepted"
    )


def test_an_open_refusal_survives_the_real_rotation_and_still_holds_the_door(
    tmp_path, monkeypatch
) -> None:
    # walk-66b4595927b6 (Feathers, Lovelace): Aether's rotation trims quiet rows from the same log my door reads. A trim that
    # dropped an OPEN refusal would lift a hold by deleting its evidence, silently. Run the REAL rotation on a real file.
    from divineos.core import log_rotation

    home = tmp_path / "home"
    home.mkdir()
    log = home / "hook_fires.jsonl"
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(log))
    t = round(time.time(), 3)
    rows = [
        {
            "t": t - 5000 + i,
            "event": "PreToolUse",
            "surface": "pr_create_gate",
            "state": "nothing-to-say",
        }
        for i in range(4000)
    ]
    rows.append(
        {
            "t": t,
            "event": "PreToolUse",
            "surface": "work_item_doorman",
            "state": "refused",
            "file": FAILING,
            "seat": "aria",
        }
    )
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    policy = next(p for p in log_rotation.POLICIES if p.filename == "hook_fires.jsonl")
    log_rotation.rotate_log(policy, home=home, min_bytes=0)
    kept = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    assert len(kept) < len(rows) and any(
        r["state"] == "refused" and r["file"] == FAILING for r in kept
    )
    assert [
        f["file"] for f in rc.open_facts(FAILING, "aria", store=tmp_path / "failure_facts.jsonl")
    ] == [FAILING]


def test_the_door_actually_calls_it() -> None:
    import inspect

    from divineos.core import work_item_doorman as door

    # The wiring lives in gate_from_stdin, the one entry every hook call passes through, so a HELD decision writes the
    # failure fact and an OPEN one is checked against the open facts.
    assert "root_cause_before_fix" in inspect.getsource(door.gate_from_stdin)
    assert "record_failure" in inspect.getsource(door.gate_from_stdin)
