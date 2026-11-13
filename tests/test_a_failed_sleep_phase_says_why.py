"""A sleep phase that fails in its child process reports WHY, not only that it failed.

Dad, 2026-11-13, of the pruning phase that failed in the full sleep cycle (exit 1) and passed when run alone: *"investigate
the sleep pruning failure, you should never disregard failures like that ever"*. The cycle sent the child's stdout and
stderr to DEVNULL, so every failed phase said only 'subprocess exit 1 (output suppressed)' and the cause was never
readable, which is exactly how a failure gets disregarded. This pins that the tail of the child's stderr reaches the
report, that a clean child still reports clean, and that the child's output goes to a FILE and not a pipe (the old comment
in sleep.py: a pipe's ~4KB buffer fills and deadlocks a noisy child on Windows).
"""

from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import pytest

from divineos.core import sleep as sl


@pytest.fixture
def only_pruning(monkeypatch):
    """The cycle with one subprocess phase, so nothing else touches a database."""
    monkeypatch.setattr(sl, "_PHASES", [("pruning", lambda *_a, **_k: None)])
    monkeypatch.setattr(sl, "_SUBPROCESS_PHASES", {"pruning"})


def _fake_child(monkeypatch, returncode: int, stderr_text: str, write_json: dict | None = None):
    seen: dict = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"], seen["kwargs"] = cmd, kwargs
        err = kwargs.get("stderr")
        if err not in (None, subprocess.DEVNULL, subprocess.PIPE) and hasattr(err, "write"):
            err.write(stderr_text)
            err.flush()
        if write_json is not None:
            out = cmd[cmd.index("--json-out") + 1]
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(write_json, fh)
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return seen


def test_a_failing_child_reports_the_tail_of_its_own_stderr(only_pruning, monkeypatch):
    _fake_child(
        monkeypatch,
        1,
        "Traceback (most recent call last):\n  ...\nsqlite3.OperationalError: database is locked\n",
    )
    report = sl.run_sleep(skip_maintenance=True)
    why = report.phase_errors["pruning"]
    assert "exit 1" in why
    assert "database is locked" in why, f"the cause did not reach the report: {why!r}"
    assert "output suppressed" not in why


def test_a_failing_child_with_no_output_says_it_printed_nothing(only_pruning, monkeypatch):
    _fake_child(monkeypatch, 3, "")
    why = sl.run_sleep(skip_maintenance=True).phase_errors["pruning"]
    assert "exit 3" in why and "no error output" in why


def test_a_long_stderr_is_cut_to_its_tail_not_dumped_whole(only_pruning, monkeypatch):
    _fake_child(monkeypatch, 1, "x" * 50_000 + "THE-LAST-LINE")
    why = sl.run_sleep(skip_maintenance=True).phase_errors["pruning"]
    assert "THE-LAST-LINE" in why
    assert len(why) < 3_000


def test_the_childs_stderr_goes_to_a_file_not_a_pipe(only_pruning, monkeypatch):
    seen = _fake_child(monkeypatch, 1, "boom")
    sl.run_sleep(skip_maintenance=True)
    err = seen["kwargs"]["stderr"]
    assert err is not subprocess.PIPE, (
        "a pipe fills at about 4KB on Windows and deadlocks a noisy child"
    )
    assert hasattr(err, "write"), (
        "stderr should be a real file so its tail can be read after the child exits"
    )


def test_an_error_printed_on_stdout_reaches_the_report_too(only_pruning, monkeypatch):
    """A CLI child can print its error on stdout; sending only stderr would say 'no error output' wrongly."""
    seen: dict = {}

    def fake_run(cmd, **kwargs):
        seen["kwargs"] = kwargs
        kwargs["stdout"].write("Error: the real message on stdout")
        kwargs["stdout"].flush()
        return SimpleNamespace(returncode=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    why = sl.run_sleep(skip_maintenance=True).phase_errors["pruning"]
    assert "the real message on stdout" in why, why


def test_an_unreadable_capture_says_it_could_not_look_not_that_nothing_was_printed():
    class Broken:
        def flush(self):
            raise OSError("handle closed")

    assert "could not read" in sl._child_output_tail(Broken())
    assert "no error output" not in sl._child_output_tail(Broken())


def test_a_clean_child_is_not_reported_as_an_error(only_pruning, monkeypatch):
    """Control: the new capture must not turn a success into a failure."""
    _fake_child(monkeypatch, 0, "", write_json={"phases_run": ["pruning"], "entries_scanned": 0})
    report = sl.run_sleep(skip_maintenance=True)
    assert "pruning" not in report.phase_errors
