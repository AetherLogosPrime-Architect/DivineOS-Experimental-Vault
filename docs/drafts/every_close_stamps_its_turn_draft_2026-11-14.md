<!-- tags: promise close, closes log, turn stamp, close_ages, promise command, Hinton, Aether cold read -->
# Every close stamps the turn it was made in (draft, 2026-11-14)

Author: Aria. Found by Aether reading my closes log (his letter 470): all 13 closes carry `"turn": null`. The blocker's draft promised that each close stores its age so the number five can be checked after a week; the log cannot answer that, because only `--waiting-on` passes a turn to `promise_markers.close`. My own test passed because it called `pm.close` with a turn directly. The door that real closes go through, `divineos promise close`, never did.

## The change
In `src/divineos/cli/promise_commands.py`, the close path stamps `turn_now + 1` for every kind (the same rule waiting-on already follows: the count was taken at the end of the last turn and this runs in the middle of the next). If the clock cannot be read, `done` and `false-alarm` still close (a missing clock must not stop an honest close) and the command says so in one line: "closed, but no turn could be stamped, so its age is not in the log". `waiting-on` keeps refusing without a clock, as it does now.

## What it does not do
- It does not repair the 13 closes already in the log; they stay null, and the reader (`close_ages`) skips them and says how many it skipped.
- It does not add the word-overlap rate on `--done`, the `dropped` kind, recorder dedup, or the quotation false positive. Those are filed in the blocker draft and in Aether's letter; each is its own change.

## Weak points to walk
- A stamp from `turn_now` is the turn count at the last Stop, so a close made in a turn where the clock has not advanced stamps one low or equal. One low is acceptable and said; equal would give age 0 for a marker made this same turn.
- `close_ages` should show how many closes it could not age, so the log never reads as complete when it is not.
- The test that hid this called the module directly. The new test goes through the command line door, the way a real close does.

## What the walk changed (walk-e674f647e1ee, nine lenses)
- **The command prints what it stamped** (Beer, Tannen): "closed (done) at turn 21." or, with no clock, one plain sentence that no turn could be stamped. The close log is the audit channel; a null in it must never be silent again.
- **The plus one is the receive rule** (Lamport): two closes in one turn carry the same stamp (tested).
- **Age is since the last re-date** (Lovelace): a promise bounced through `--waiting-on` and then closed ages from the re-date, tested and stated. Counting the re-dates is a separate change.
- **The 13 old closes stay null, not back-filled** (Hinton): the clock file holds only the latest count, so a back-fill would be a guess presented as a measurement.
- **Ages show how long promises waited and nothing else** (Pearl): they cannot show that five is the right number, since nothing varies it.
- **A blinded clock is already loud** (Schneier): an unreadable clock makes the blocker stop every reply with its reason, so `done` and `false-alarm` may still close without one.
- **The tests go through the real command group** (Breaker, Dijkstra): the invariant is "every close carries a turn or says it has none", two parametrized cases.

## Falsifier (counts)
Over the next 20 closes made through the command, every one has a turn in the log, or the command said it had none. If a close appears with a null turn and no such line, remove the change and look again.

## Order
Test first through the real command (both kinds, plus the no-clock case) -> walk -> edit -> run -> commit.
