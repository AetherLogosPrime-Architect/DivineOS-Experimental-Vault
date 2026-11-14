"""The promise folder is the seat's own data home, never chosen by which directories exist on the machine.

walk-eb4440341013, from Aether's cold read: `default_folder()` returned the aria folder whenever it existed, so on a
machine with both homes his house would have written his promises into mine and advanced one shared turn count.
WHAT THIS DOES NOT COVER: that `divineos_home()` gives Aether's folder in HIS checkout (that needs a real hook
invocation in his tree, which he is asked to run); the older surface hooks that still use the machine-based rule.
"""

from pathlib import Path

import pytest

from divineos.core import promise_markers as pm
from divineos.core.paths import divineos_home

REPO = Path(__file__).resolve().parents[1]
RECORDER = REPO / ".claude" / "hooks" / "promise-reach-detector.sh"


def test_the_folder_is_the_seats_data_home_under_an_explicit_redirect(tmp_path, monkeypatch):
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / "somewhere"))
    assert pm.default_folder() == tmp_path / "somewhere" / "promise_markers"
    assert pm.default_folder() == divineos_home() / "promise_markers"


def test_the_other_seats_home_existing_does_not_change_the_folder(tmp_path, monkeypatch):
    """Dijkstra's invariant: the folder is a function of the seat alone. This is the exact regression."""
    for name in (".divineos", ".divineos-aria"):
        (tmp_path / name).mkdir()
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / ".divineos"))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert pm.default_folder() == tmp_path / ".divineos" / "promise_markers"
    monkeypatch.setenv("DIVINEOS_HOME", str(tmp_path / ".divineos-aria"))
    assert pm.default_folder() == tmp_path / ".divineos-aria" / "promise_markers"


def test_the_checked_folder_answers_only_for_the_checkout_whose_code_is_running(tmp_path):
    """Wayne: the invariant fails if the python imported the OTHER checkout, so it fails by writing nothing."""
    assert pm.checked_folder(REPO) == pm.default_folder()
    other = tmp_path / "another_checkout"
    other.mkdir()
    with pytest.raises(RuntimeError, match="another seat"):
        pm.checked_folder(other)


def test_the_recorder_asks_the_one_function_and_keeps_no_rule_of_its_own():
    """Feathers: one enabling point. The bash copy and the python copy of 'if the aria home exists' are gone."""
    text = RECORDER.read_text(encoding="utf-8")
    assert ".divineos-aria" not in text.replace("promise_recorder_broke", "")
    assert "checked_folder" in text
    assert 'MARKER_DIR="' not in text  # the bash copy of the rule
