# The build door cannot go to sleep silently (draft, 2026-11-11, Aria)

**Status:** design plus red tests. Dad's first build. Production code is not touched until this is walked. Tests: `tests/test_the_doorman_cannot_go_silently_asleep.py` (two red for the right reasons, one control green).

## What Dad said

*"the fact it was tied to the briefing means for as long as the briefing was not enforced.. which has literally been for months.. everything done since then is compromised"* and the order of builds: forced root cause, and the build flow enforced on every build so it cannot be skipped.

## Root cause (read from the code, then reproduced)

The shell door (`.claude/hooks/work-item-doorman.sh`) asks `divineos work-item gate` and treats every answer except exit 2 as permission. The CLI (`cli/__init__.py`, `_enforce_briefing_gate`) refuses every command not on its short bootstrap list when the briefing is not loaded, exit 1. `work-item` is not on that list. So with a stale briefing the checker never ran, the door read exit 1 as "no opinion", and let the call through with nothing said. Reproduced in a fresh empty home: the checker prints the briefing block and exits 1; the door exits 0 in complete silence.

## The fix, two parts, because there are two faults

1. **The checker must be able to answer.** Add `work-item` to the bootstrap list. Precedent is the same species three times already in that list (`goal`, `compass-ops`, `learn`, `andrew-correction`, `check-branch`): a gate must never be blocked by a gate that is not its business. The doorman decides from the work-item store, not from the briefing.
2. **The door must never be silent about an unanswered checker.** When the checker exits with anything but an allow (0) or a hold (2), the door says so on stderr in plain words, names the exit code and the first lines it printed, and says this call was NOT checked. It stays open for infrastructure faults (a door that blocks every call when its own plumbing breaks gets torn out, and the edit that repairs it would be blocked too), but never silently.

## Not decided here, for the walk

- Whether the loud-and-open case should become a hold after the same unanswered state repeats.
- Whether anything besides the stderr line should read the miss. (A writer must name its reader.)
- Whether `work-item status` and `work-item bypass` belong on the bootstrap list too, or only `gate`. The list matches on the first word, so this is the whole group unless the list learns subcommands.

## What the walk decided (walk-1f4842776480, nine lenses)

- **Three fixes, not two (Hoare, Schneier).** (a) `work-item` on the bootstrap list so a stale briefing cannot stop the checker. (b) The checker's allow is POSITIVE: it prints its own marker on allow, and the door treats exit 0 without the marker as could-not-answer, because the door has three states and only two outputs. (c) Every silent early exit in the shell door says so: the checker not on the path (line 28) and an empty payload (line 26) are the same silent permission as the briefing case.
- **Say it once, plainly, and record it (Meadows, Holmes, Godel).** One short stderr line per unanswered call, never a wall. The record that carries weight: whether the checker answered goes into the doorman's liveness row, and the hook firing map reads it, which is the named reader. Escalation to hold after repeated unanswered passes stays OPEN, with a falsifier counted in uses: over the first 30 passes of the door after this ships, count how many end unanswered. Zero is the expectation; any unanswered pass while the briefing is loaded means the fix missed a cause and the door becomes a hold. (The walk finding said "in a week". Dad's rule is events and uses, never calendar time, so that wording is superseded here; the finding itself is append-only and stays as written.)
- **The proof owed (Popper, Breaker).** A fourth test, end to end: the real hook and the real checker, fresh briefing-less home, an edit that should be held (no open work item), must exit 2. After the fix, the same run on the real door with the briefing deliberately unloaded in a temp home. Both sides of the new marker boundary are tested (exit 0 with the marker, exit 0 without it), plus the empty payload.
- **What is NOT claimed (Pearl).** The tests prove the door CAN sleep. How often it did is unmeasured, because the history records the hook's exit and a sleeping allow and a real allow are both exit 0. The "months" claim is Dad's inference and plausible; it is not a measurement and this draft does not repeat it as one. The new record makes the next sleep a number.
- **Known and accepted (Schneier).** Putting the whole `work-item` group on the list makes `bypass` reachable without a briefing. It carries its own verified-quote check, and it is the deadlock escape, so the exposure is accepted and named.

## What this cannot do

It cannot make the door correct about every edit; it only makes it impossible for the door to be off without saying so. The other doors that treat "not 2" as permission have the same shape and are not touched here.
