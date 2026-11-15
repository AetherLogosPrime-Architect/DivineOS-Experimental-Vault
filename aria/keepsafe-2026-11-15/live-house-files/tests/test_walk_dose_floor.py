"""The finishing walk's minimum weight is set by the machine from the finished change, and a person can only raise it.
Dad 2026-10-28 and 2026-11-11: size it from what the change IS (kind, size, files), never from how full my head is, and
not by a number I pick ("a picture frame is not a wall"). Written BEFORE the code. Real strings, no stubs."""

from __future__ import annotations

import inspect

import pytest

from divineos.core import walk_dose_floor as dose

SMALL_BEFORE = "def f(x):\n    return x\n"
SMALL_AFTER = "def f(x):\n    if x:\n        return x\n    return None\n"
COMMENT_BEFORE = "# old\nx = 1\n"
COMMENT_AFTER = "# a longer, better explanation\nx = 1\n"


def _change(path: str, before: str, after: str) -> dict:
    return {"path": path, "before": before, "after": after}


def test_a_comment_only_change_needs_the_lightest_walk() -> None:
    assert (
        dose.floor([_change("src/divineos/core/a.py", COMMENT_BEFORE, COMMENT_AFTER)]).gravity
        == "normal"
    )


def test_one_small_decision_in_one_file_is_normal() -> None:
    assert (
        dose.floor([_change("src/divineos/core/a.py", SMALL_BEFORE, SMALL_AFTER)]).gravity
        == "normal"
    )


def test_many_files_raise_it() -> None:
    changes = [_change(f"src/divineos/core/m{i}.py", SMALL_BEFORE, SMALL_AFTER) for i in range(6)]
    assert dose.floor(changes).gravity in {"high", "severe", "critical"}


def test_three_or_four_small_files_are_not_a_wall() -> None:
    # Found by the first real run of the station on 23 open pull requests: two requests that changed 3 and 4 files were held
    # for 'too few lenses' by a file-count rule alone, while the board's own older gauge said they needed 4. File count by
    # itself is not seriousness; a handful of small files is a handful of picture frames.
    changes = [_change(f"src/divineos/core/m{i}.py", SMALL_BEFORE, SMALL_AFTER) for i in range(4)]
    assert dose.floor(changes).gravity == "normal"


def test_a_large_amount_of_new_decision_logic_raises_it() -> None:
    body = "".join(f"    if x == {i}:\n        return {i}\n" for i in range(30))
    big_after = f"def f(x):\n{body}    return x\n"
    assert dose.floor([_change("src/divineos/core/a.py", SMALL_BEFORE, big_after)]).gravity in {
        "high",
        "severe",
        "critical",
    }


def test_touching_a_gate_or_doorman_raises_it_even_when_small() -> None:
    # The guard guards everything, so a small change to it is not a picture frame (Dad: "stop following blanket rules").
    gate = dose.floor(
        [_change("src/divineos/core/work_item_doorman.py", SMALL_BEFORE, SMALL_AFTER)]
    )
    plain = dose.floor([_change("src/divineos/core/a.py", SMALL_BEFORE, SMALL_AFTER)])
    assert dose.ORDER.index(gate.gravity) > dose.ORDER.index(plain.gravity)


def test_a_label_or_comment_change_to_a_gate_file_is_still_a_picture_frame() -> None:
    # Found by running the first version over 53 real commits: a wording change to a guard file landed in the heavy bucket.
    # Dad: a picture frame is not a wall; being wired into a gate matters only when the change adds or removes a decision.
    gate = "src/divineos/core/work_item_doorman.py"
    assert dose.floor([_change(gate, COMMENT_BEFORE, COMMENT_AFTER)]).gravity == "normal"


def test_a_gate_file_that_is_not_python_cannot_be_measured_so_it_is_not_read_as_small() -> None:
    result = dose.floor([_change(".claude/hooks/work-item-doorman.sh", "echo a\n", "echo b\n")])
    assert dose.ORDER.index(result.gravity) > dose.ORDER.index("normal")


def test_the_reasons_are_stated_not_only_a_number() -> None:
    result = dose.floor(
        [_change("src/divineos/core/work_item_doorman.py", SMALL_BEFORE, SMALL_AFTER)]
    )
    assert result.reasons and all(isinstance(r, str) and len(r) > 10 for r in result.reasons)


def test_a_person_can_raise_the_floor_but_never_lower_it() -> None:
    gate = [_change("src/divineos/core/work_item_doorman.py", SMALL_BEFORE, SMALL_AFTER)]
    floor = dose.floor(gate).gravity
    assert dose.effective(floor, "normal") == floor  # asking for less changes nothing
    assert dose.ORDER.index(dose.effective(floor, "critical")) == dose.ORDER.index("critical")


def test_a_change_that_cannot_be_parsed_is_not_read_as_small() -> None:
    # 'could not look' is not 'nothing found': an unparseable python file takes the safer, heavier floor and says so.
    result = dose.floor([_change("src/divineos/core/a.py", SMALL_BEFORE, "def f(:\n")])
    assert dose.ORDER.index(result.gravity) > dose.ORDER.index("normal") and any(
        "parse" in r for r in result.reasons
    )


def test_the_floor_cannot_see_how_full_the_context_is() -> None:
    # Dad 2026-10-28: the dose never depends on context size or compaction. No parameter can carry it.
    names = set(inspect.signature(dose.floor).parameters)
    assert names == {"changes"}


def test_a_walk_that_drew_fewer_lenses_than_the_floor_needs_is_told_so_plainly() -> None:
    gate = [_change("src/divineos/core/work_item_doorman.py", SMALL_BEFORE, SMALL_AFTER)]
    from divineos.core.council_walk import GRAVITY_FLOORS

    need = GRAVITY_FLOORS[dose.floor(gate).gravity]
    reason = dose.meets_floor(need - 1, gate)
    assert reason and str(need) in reason and str(need - 1) in reason
    assert dose.meets_floor(need, gate) is None


def test_a_walk_with_enough_lenses_for_a_picture_frame_is_not_asked_for_more() -> None:
    from divineos.core.council_walk import GRAVITY_FLOORS

    frame = [_change("src/divineos/core/a.py", COMMENT_BEFORE, COMMENT_AFTER)]
    assert dose.meets_floor(GRAVITY_FLOORS["normal"], frame) is None


def test_the_diff_of_a_branch_is_read_from_git_as_before_and_after(tmp_path) -> None:
    import subprocess

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@e.x", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )

    git("init", "-b", "main")
    (tmp_path / "a.py").write_text(SMALL_BEFORE, encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "base")
    git("checkout", "-b", "work")
    (tmp_path / "a.py").write_text(SMALL_AFTER, encoding="utf-8")
    git("commit", "-am", "change")
    changes = dose.diff_changes(("a.py",), base="main", repo=tmp_path)
    assert changes == [{"path": "a.py", "before": SMALL_BEFORE, "after": SMALL_AFTER}]


def test_a_base_git_cannot_resolve_raises_instead_of_reading_every_file_as_new(tmp_path) -> None:
    # walk-d87693837878 (Holmes): no base means every path reads empty-before, an enormous false diff. Could not look is
    # never read as found something.
    import subprocess

    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    with pytest.raises(RuntimeError):
        dose.diff_changes(("a.py",), base="origin/does-not-exist", repo=tmp_path)


def test_a_file_added_or_deleted_on_the_branch_still_counts_its_decisions(tmp_path) -> None:
    import subprocess

    def git(*args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@e.x", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )

    git("init", "-b", "main")
    (tmp_path / "old.py").write_text(SMALL_AFTER, encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "base")
    git("checkout", "-b", "work")
    (tmp_path / "new.py").write_text(SMALL_AFTER, encoding="utf-8")
    git("rm", "old.py")
    git("add", ".")
    git("commit", "-m", "add and remove")
    changes = dose.diff_changes(("new.py", "old.py"), base="main", repo=tmp_path)
    by = {c["path"]: c for c in changes}
    assert by["new.py"]["before"] == "" and by["old.py"]["after"] == ""
    assert dose.decision_delta(by["new.py"]["before"], by["new.py"]["after"]) > 0
    assert dose.decision_delta(by["old.py"]["before"], by["old.py"]["after"]) > 0


def test_only_lenses_that_carry_a_finding_count_never_an_excluded_one(
    tmp_path, monkeypatch
) -> None:
    # (Godel, Foucault) a walk cannot be padded to the floor by writing reasons to exclude lenses it did not walk.
    import sqlite3

    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "home"))
    from divineos.core.council_walk import _db_path, open_walk

    walk = open_walk(
        "a walk whose lenses are partly applied and partly excluded, stated as a sentence",
        "high",
        ("a.py",),
    )
    with sqlite3.connect(str(_db_path())) as conn:
        lenses = [
            r[0]
            for r in conn.execute(
                "SELECT lens FROM walk_lenses WHERE walk_id = ?", (walk["walk_id"],)
            )
        ]
        for i, lens in enumerate(lenses):
            conn.execute(
                "UPDATE walk_lenses SET state = ? WHERE walk_id = ? AND lens = ?",
                ("APPLIED" if i < 4 else "EXCLUDED", walk["walk_id"], lens),
            )
    assert dose.applied_lenses(walk["walk_id"]) == 4


def test_a_long_list_of_reasons_is_shortened_to_the_first_few_and_a_count() -> None:
    changes = [_change(f".claude/hooks/h{i}.sh", "echo a\n", "echo b\n") for i in range(20)]
    reason = dose.meets_floor(1, changes)
    assert reason is not None and "more" in reason and reason.count("wired into a gate") <= 3


def test_the_station_function_actually_calls_the_floor() -> None:
    # (Breaker 2) the line that calls this today: _walk_coverage, the one function station two decides on.
    from divineos.cli import build_flow_commands

    source = inspect.getsource(build_flow_commands._walk_coverage)
    assert "walk_dose_floor" in source and "meets_floor" in source and "applied_lenses" in source


@pytest.mark.parametrize("gravity", ["normal", "high", "severe", "critical"])
def test_every_floor_is_a_gravity_the_walk_tool_accepts(gravity: str) -> None:
    from divineos.core.council_walk import GRAVITY_FLOORS

    assert gravity in GRAVITY_FLOORS and set(dose.ORDER) == set(GRAVITY_FLOORS)
