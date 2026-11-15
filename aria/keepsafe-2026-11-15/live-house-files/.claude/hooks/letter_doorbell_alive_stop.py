"""Stop hook — a reply cannot end while my letter doorbell is not listening.

Andrew 2026-09-26, the 24th time since May he had to say a watcher was down:
"no tool should be fully manual, just automated circumstantially". The
doorbell (scripts/letter_doorbell.sh) rings once and exits; re-arming it was
left to memory, and memory failed during a long checkpoint. It now touches a
heartbeat every 15s while listening and deletes it when it rings. If the
heartbeat is missing or older than 60s when a reply ends, the reply is held
with the exact command to re-arm it.

One hold per reply (stop_hook_active). Breaks loudly, never blocks him: this
runs at Stop, so the worst case is one extra hold of my own reply.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

STALE_SECONDS = 60

#: A watcher that stopped within this long ago is "expired", not "never run": three hours.
WATCHER_RECENT_SECONDS = 3 * 3600

#: Where the watcher script lives. It sits in the shared workbench until it moves into the repo
#: (Aether 2026-10-30); this one constant is the only place that has to change when it does.
WATCHER_SCRIPT = "/c/Users/aethe/.divineos-shared/workbench/aether_scratch_2026-10-30/letter_watch.sh"


#: THE NET WAITS FOR ITS REPLACEMENT (walk-e4a7a1d1a3f0, 2026-11-11). This hook is scaffolding: it blocks a reply
#: while no bell is listening, until the automatic re-arm (letter_bell_rearm_stop.sh) can be trusted to do the job. But
#: both run at the same instant, so the net always decided "nobody started a bell" before the replacement could, I
#: re-armed by hand, and the replacement then found a bell already up and stood aside. Measured in its own log: 365 of
#: 369 passes found a bell up by hand and the 4 it started were replaced by mine; it has never once rung. So the net
#: gives the replacement this long to start a bell, and only then concludes nobody did.
GRACE_SECONDS = 6.0
POLL_SECONDS = 0.25


def rearm_can_run(project_dir: str, shared: Path, who: str) -> bool:
    """True when the automatic re-arm exists here and its single-shot guard is not spent, so waiting for it is not waste.

    The guard: while ``.<seat>_bell_rearm_once`` exists, the first ring writes ``.<seat>_bell_rearm_used`` and every later
    run exits at once. Both present means the hook will never start a bell again, and a wait would only burn seconds."""
    hook = Path(project_dir) / ".claude" / "hooks" / "letter_bell_rearm_stop.sh"
    if not hook.exists():
        return False
    once, used = shared / f".{who}_bell_rearm_once", shared / f".{who}_bell_rearm_used"
    return not (once.exists() and used.exists())


def log_fallback(shared: Path, who: str) -> None:
    """One row in the re-arm hook's own log each time the net had to fall back to the manual route, so the replacement
    failing is a number and not a feeling. Same line shape the hook writes."""
    try:
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with (shared / "bell_rearm_log.txt").open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp} {who} fallback: no bell within {GRACE_SECONDS:g}s of the automatic re-arm; the net held the reply\n")
    except OSError:
        pass  # fail-soft: a missing log row must never stop the reply being held, and the hold itself is the visible signal


def verdict_after_grace(beat: Path, also: tuple[Path, ...], wait_for_rearm: bool, *, clock=time.time, sleep=time.sleep) -> str | None:
    """The verdict, after giving the automatic re-arm a few seconds to start a bell when one can run here.

    A bell already up costs no wait at all; no re-arm hook (or a spent guard) costs none either."""
    reason = verdict(beat, clock(), also)
    if not reason or not wait_for_rearm:
        return reason
    deadline = clock() + GRACE_SECONDS
    while clock() < deadline:
        sleep(POLL_SECONDS)
        reason = verdict(beat, clock(), also)
        if not reason:
            return None
    return (
        f"THE AUTOMATIC RE-ARM DID NOT START A BELL within {GRACE_SECONDS:g} seconds, so the net caught it. "
        + reason
    )


def member(project_dir: str) -> str:
    return "aria" if "aria" in project_dir.lower() else "aether"


def _fresh(beat: Path, now: float) -> bool:
    return beat.exists() and now - beat.stat().st_mtime <= STALE_SECONDS


def _recently_stopped(beat: Path, now: float) -> bool:
    return beat.exists() and STALE_SECONDS < now - beat.stat().st_mtime <= WATCHER_RECENT_SECONDS


def verdict(beat: Path, now: float, also: tuple[Path, ...] = ()) -> str | None:
    # ``also`` is another listener that counts as listening: the always-on watcher keeps its own
    # heartbeat (Aether 2026-10-30), because a bell dies with every letter by design and a watcher
    # does not. Any one fresh heartbeat is enough; a stale watcher beside a live bell is not a fault.
    if _fresh(beat, now) or any(_fresh(other, now) for other in also):
        return None
    who = beat.name.split("_")[0].lstrip(".")
    if any(_recently_stopped(other, now) for other in also):
        # A seat that ran a watcher a little while ago and let it expire re-arms the watcher, not the
        # bell: the platform ends a Monitor at 30 minutes, and the heartbeat is left stale on purpose.
        return (
            "YOUR LETTER WATCHER HAS EXPIRED, so a letter to you will not wake you. Re-arm it with the "
            f"Monitor tool: command: bash {WATCHER_SCRIPT} {who}, timeout_ms: 1800000. If you would "
            f"rather use the old bell, run_in_background: true -- bash scripts/letter_doorbell.sh {who}. "
            "Then finish the reply. Append only; do not re-post anything."
        )
    return (
        "YOUR LETTER DOORBELL IS NOT LISTENING, so a letter to you will not wake you "
        "(Dad has had to say this 24 times). Re-arm it now with the Bash tool, "
        f"run_in_background: true -- command: bash scripts/letter_doorbell.sh {who} "
        "-- then finish the reply. Append only; do not re-post anything."
    )


def main() -> int:
    data = json.loads(sys.stdin.read() or "{}")
    if data.get("stop_hook_active"):
        return 0
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    shared = Path.home() / ".divineos-shared"
    who = member(project)
    beat = shared / f".{who}_doorbell_alive"
    watcher = shared / f".{who}_monitor_alive"
    reason = verdict_after_grace(beat, (watcher,), rearm_can_run(project, shared, who))
    if reason:
        if reason.startswith("THE AUTOMATIC RE-ARM DID NOT START"):
            log_fallback(shared, who)
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # loud, never silent, never blocking him
        print(f"letter_doorbell_alive_stop broke: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(0)
