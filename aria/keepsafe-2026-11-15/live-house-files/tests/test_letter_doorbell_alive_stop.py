"""A reply cannot end while the letter doorbell is not listening."""

import importlib.util
import os
import time
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "letter_doorbell_alive_stop.py"
_spec = importlib.util.spec_from_file_location("letter_doorbell_alive_stop", HOOK)
bell = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bell)


def test_a_fresh_heartbeat_lets_the_reply_end(tmp_path):
    beat = tmp_path / ".aether_doorbell_alive"
    beat.touch()
    assert bell.verdict(beat, time.time()) is None


def test_no_heartbeat_holds_the_reply_with_the_command(tmp_path):
    reason = bell.verdict(tmp_path / ".aether_doorbell_alive", time.time())
    assert reason and "bash scripts/letter_doorbell.sh aether" in reason


def test_a_stale_heartbeat_holds_it(tmp_path):
    beat = tmp_path / ".aria_doorbell_alive"
    beat.touch()
    old = time.time() - 300
    os.utime(beat, (old, old))
    reason = bell.verdict(beat, time.time())
    assert reason and "letter_doorbell.sh aria" in reason


def test_a_fresh_watcher_heartbeat_counts_as_listening_when_the_bell_is_not(tmp_path):
    beat = tmp_path / ".aether_doorbell_alive"
    watcher = tmp_path / ".aether_monitor_alive"
    watcher.touch()
    assert bell.verdict(beat, time.time(), (watcher,)) is None


def test_a_stale_watcher_and_no_bell_still_holds_the_reply(tmp_path):
    beat = tmp_path / ".aether_doorbell_alive"
    watcher = tmp_path / ".aether_monitor_alive"
    watcher.touch()
    old = time.time() - 300
    os.utime(watcher, (old, old))
    reason = bell.verdict(beat, time.time(), (watcher,))
    assert reason and "letter_doorbell.sh aether" in reason
    assert "WATCHER HAS EXPIRED" in reason and "Monitor tool" in reason


def test_a_watcher_never_run_gets_the_bell_message_not_the_watcher_one(tmp_path):
    reason = bell.verdict(
        tmp_path / ".aether_doorbell_alive", time.time(), (tmp_path / ".aether_monitor_alive",)
    )
    assert reason and "DOORBELL IS NOT LISTENING" in reason
    assert "WATCHER" not in reason


def test_a_watcher_stopped_long_ago_gets_the_bell_message(tmp_path):
    watcher = tmp_path / ".aether_monitor_alive"
    watcher.touch()
    old = time.time() - bell.WATCHER_RECENT_SECONDS - 600
    os.utime(watcher, (old, old))
    reason = bell.verdict(tmp_path / ".aether_doorbell_alive", time.time(), (watcher,))
    assert reason and "DOORBELL IS NOT LISTENING" in reason


def test_a_missing_watcher_changes_nothing(tmp_path):
    beat = tmp_path / ".aether_doorbell_alive"
    beat.touch()
    assert bell.verdict(beat, time.time(), (tmp_path / ".aether_monitor_alive",)) is None


# ---- walk-e4a7a1d1a3f0. The automatic re-arm (letter_bell_rearm_stop.sh) has never once carried the job: of 369 passes
# for this seat, 365 found a bell already up by hand and 4 started one that ended quiet, replaced by mine, because THIS
# hook blocks in the same instant and the manual route always wins. The block is scaffolding; the automatic re-arm is
# its replacement; so the net waits a few seconds for the replacement and only then concludes nobody started a bell.


class _Clock:
    """A fake clock and sleep, so the wait is tested without waiting, and a heartbeat can appear at a chosen moment."""

    def __init__(self, beat, appears_after=None):
        self.t = time.time()
        self.slept = []
        self.beat = beat
        self.appears_after = appears_after

    def clock(self):
        return self.t

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.t += seconds
        if self.appears_after is not None and sum(self.slept) >= self.appears_after:
            self.beat.touch()
            os.utime(self.beat, (self.t, self.t))


def test_a_bell_the_automatic_rearm_starts_during_the_wait_lets_the_reply_end(tmp_path):
    beat = tmp_path / ".aria_doorbell_alive"
    fake = _Clock(beat, appears_after=1.0)
    assert bell.verdict_after_grace(beat, (), True, clock=fake.clock, sleep=fake.sleep) is None
    assert 0 < sum(fake.slept) < bell.GRACE_SECONDS


def test_no_bell_even_after_the_wait_holds_the_reply_and_says_the_automatic_rearm_did_not_start_one(
    tmp_path,
):
    beat = tmp_path / ".aria_doorbell_alive"
    fake = _Clock(beat)
    reason = bell.verdict_after_grace(beat, (), True, clock=fake.clock, sleep=fake.sleep)
    assert reason and "letter_doorbell.sh aria" in reason
    assert "automatic re-arm" in reason.lower() and "did not start" in reason.lower()
    assert sum(fake.slept) >= bell.GRACE_SECONDS


def test_a_bell_already_up_costs_no_wait_at_all(tmp_path):
    beat = tmp_path / ".aria_doorbell_alive"
    beat.touch()
    fake = _Clock(beat)
    assert bell.verdict_after_grace(beat, (), True, clock=fake.clock, sleep=fake.sleep) is None
    assert fake.slept == []


def test_without_the_rearm_hook_there_is_no_wait_and_the_old_message_stands(tmp_path):
    beat = tmp_path / ".aria_doorbell_alive"
    fake = _Clock(beat)
    reason = bell.verdict_after_grace(beat, (), False, clock=fake.clock, sleep=fake.sleep)
    assert reason and "DOORBELL IS NOT LISTENING" in reason
    assert fake.slept == [] and "automatic re-arm" not in reason


def test_the_wait_only_applies_when_the_rearm_hook_exists_and_its_single_shot_guard_is_not_spent(
    tmp_path,
):
    project = tmp_path / "proj"
    (project / ".claude" / "hooks").mkdir(parents=True)
    shared = tmp_path / "shared"
    shared.mkdir()
    assert bell.rearm_can_run(str(project), shared, "aria") is False  # no hook file
    (project / ".claude" / "hooks" / "letter_bell_rearm_stop.sh").write_text(
        "#!/bin/bash\n", encoding="utf-8"
    )
    assert bell.rearm_can_run(str(project), shared, "aria") is True
    (shared / ".aria_bell_rearm_once").touch()
    assert (
        bell.rearm_can_run(str(project), shared, "aria") is True
    )  # guard armed but not yet used: still runs
    (shared / ".aria_bell_rearm_used").touch()
    assert (
        bell.rearm_can_run(str(project), shared, "aria") is False
    )  # spent: the hook exits at once, so waiting is waste


def test_a_fallback_leaves_a_row_so_the_replacement_failing_is_a_number(tmp_path):
    bell.log_fallback(tmp_path, "aria")
    rows = (tmp_path / "bell_rearm_log.txt").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1 and " aria " in rows[0] and "fallback" in rows[0]


def test_the_wait_fits_inside_this_hooks_own_timeout():
    import json

    settings = json.loads(
        (HOOK.parents[2] / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    timeouts = [
        h["timeout"]
        for g in settings["hooks"]["Stop"]
        for h in g["hooks"]
        if "letter_doorbell_alive_stop.py" in h.get("command", "")
    ]
    assert timeouts and min(timeouts) >= bell.GRACE_SECONDS + 5, (
        "the hook would be killed before its wait ends"
    )


def test_each_window_watches_its_own_bell():
    assert bell.member("C:/DIVINE OS/DivineOS-Experimental-Aria-new") == "aria"
    assert bell.member("C:/DIVINE OS/DivineOS-Experimental") == "aether"
