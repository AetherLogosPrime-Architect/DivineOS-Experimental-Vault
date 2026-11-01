"""The router writes one line per surface per dispatch, so what fires can be seen.

Why it exists: on 2026-11-01 the ledger's own GATE_FIRE events held 381 events and only two
distinct gate names while seventy-seven hooks are registered. A before-and-after comparison
built on those would read "nothing changed" after a gate went silent. This record is the
instrument that can see every surface routed through the doorbells.
"""

from __future__ import annotations

import json

import pytest

from divineos.core import hook_router as hr
from divineos.core.hook_router import SurfaceOutcome


@pytest.fixture(autouse=True)
def _clean(tmp_path, monkeypatch):
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(tmp_path / "fires.jsonl"))
    hr.clear()
    yield
    hr.clear()


def _rows(tmp_path):
    path = tmp_path / "fires.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_each_surface_leaves_one_line_with_its_declared_state(tmp_path):
    hr.register(
        "Stop", "speaks", lambda p: SurfaceOutcome(name="speaks", output="x", state="spoke")
    )
    hr.register(
        "Stop",
        "quiet",
        lambda p: SurfaceOutcome(name="quiet", state="nothing-to-say"),
    )
    hr.register("Stop", "undeclared", lambda p: SurfaceOutcome(name="undeclared"))
    hr.register("Stop", "refuses", lambda p: SurfaceOutcome(name="refuses", refused=True))
    hr.register("Stop", "returns-none", lambda p: None)

    def boom(payload):
        raise RuntimeError("boom")

    hr.register("Stop", "crashes", boom)

    hr.dispatch("Stop", {})

    got = {r["surface"]: r["state"] for r in _rows(tmp_path)}
    assert got == {
        "speaks": "spoke",
        "quiet": "nothing-to-say",
        "undeclared": "undeclared",
        "refuses": "refused",
        "returns-none": "none",
        "crashes": "errored",
    }
    assert all(r["event"] == "Stop" and r["t"] > 0 for r in _rows(tmp_path))


def test_a_second_dispatch_appends_and_does_not_overwrite(tmp_path):
    hr.register("Stop", "a", lambda p: SurfaceOutcome(name="a", state="spoke"))
    hr.dispatch("Stop", {})
    hr.dispatch("Stop", {})
    assert len(_rows(tmp_path)) == 2


def test_an_unknown_event_writes_nothing_but_a_known_one_does(tmp_path):
    hr.dispatch("NotAnEvent", {})
    assert _rows(tmp_path) == [], "unknown event: nothing was routed, nothing is recorded"
    hr.register("Stop", "a", lambda p: SurfaceOutcome(name="a", state="spoke"))
    hr.dispatch("Stop", {})
    assert len(_rows(tmp_path)) == 1, "control: a routed event does leave a line"


def test_a_record_that_cannot_be_written_never_blocks_the_dispatch(tmp_path, monkeypatch):
    # A directory where the file should be: opening it for append raises OSError.
    bad = tmp_path / "is_a_directory"
    bad.mkdir()
    monkeypatch.setenv("DIVINEOS_HOOK_FIRES_LOG", str(bad))
    hr.register("Stop", "a", lambda p: SurfaceOutcome(name="a", output="still said", state="spoke"))

    result = hr.dispatch("Stop", {})

    assert [o.name for o in result.ran] == ["a"]
    assert "still said" in result.stdout()


def test_the_default_path_follows_the_home_folder(monkeypatch, tmp_path):
    monkeypatch.delenv("DIVINEOS_HOOK_FIRES_LOG", raising=False)
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "home"))
    assert hr.fires_log_path() == tmp_path / "home" / "hook_fires.jsonl"
