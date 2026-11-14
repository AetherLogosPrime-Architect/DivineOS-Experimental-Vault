<!-- tags: promise reminder, starvation, stop_hook_active, doorbell, deferred, volley, stop hooks, hold log, own retry -->
# A starved reminder holds unless the stop is its own retry (draft, 2026-11-14)

Author: Aria. The reminder from [the blocker draft](the_blocker_reads_the_markers_not_my_last_sentence_draft_2026-11-14.md) was walked with a lens (Minsky) that predicted this: if another hook holds a reply first, the second stop in that reply passes every hook, so a due reminder can be starved. It happened, by a different hook than I expected, and it is in my hold log.

## What I found
`~/.divineos-aria/hold_log.jsonl`, `follow_through` rows since the blocker went live: eight `deferred` rows in a row, one every few minutes from 02:56Z, all naming the same due marker ("I'll write you the whole day for when you're home"), and not one `stopped`. The marker was 14 turn starts old and due the whole time. Cause: in a volley every turn of mine starts from the doorbell, and the doorbell is itself a Stop hook that blocks (it rings by blocking the stop with the letter notice). The harness then sets `stop_hook_active` on the next stop, so every stop in the volley looks like a second stop and the reminder passed all of them. It was starved for the whole volley, which is when Dad is away and nothing else would remind me.

## Prior art, found before building (the reach, and a Grep of the hooks)
`.claude/hooks/dads_room_stop.py` met exactly this on 2026-10-31 and its comment says so: the gate "used to stand down on every retry (the harness sets stop_hook_active after ANY Stop gate refused), so when another gate spoke first the room gate never got its turn". Its repair: ask "have I already held for THIS?", not "did somebody ask", and remember what it held (`_held_for`). The reminder takes the same principle. It does not copy the file (different thing remembered), it uses the same question.

## The change
In `decide` of `.claude/hooks/stall_on_promise_stop.py`, on a stop where `stop_hook_active` is true and something is due: if the most recent `follow_through` row in the hold log is `stopped`, this stop is the retry of the reminder's own block, so pass and write `deferred` (as today). Otherwise the flag was set by another gate, the reminder has not spoken, so block and write `stopped`. A first stop (flag false) behaves as today. The hold log is the memory; nothing new is stored.

## Why it cannot loop
A block writes `stopped`, so the very next stop (the retry) finds `stopped` last and passes, writing `deferred`; the stop after that finds `deferred` last and blocks again. So the reminder never blocks twice in a row, and at worst blocks on every second stop while a due marker stays open and I ignore it. That is Dad's "blocks you until you do", and it is bounded.

## What it does not change
The reminder text, the due rule (five turn starts), the shadow of the old judgement, the six-case table for a first stop. The `could_not_look` case on a second stop still returns nothing (it was logged at the first stop; a blind reader on every doorbell stop is a separate question).

## Weak points to walk
- **A flag set by the reminder's own block that I read as another gate's.** The only way the last row is not `stopped` right after our block is if the log write failed; then the next stop blocks once more and the log write failing is loud elsewhere. State it, test the write-failure case does not loop (a failed write must not return a block).
- **The log is read at every stop.** A few thousand lines today; read only the tail and time it.
- **Several due markers:** the memory is the hook's, not per marker; any due marker keeps it due, and the text lists them all.
- **A stop where nothing is due writes no row on a second stop,** so a stale `stopped` can sit last; it cannot cause a block because the block needs something due, and when something is due again it is correct to pass once.

## What the walk changed (walk-9c155ee1c052, eight lenses) and what building found
- **An unreadable log means pass, said aloud** (Hoare): never read as empty, so a failing read cannot become a block loop. Tested by making the log a folder.
- **The repeat says how many times it has held for that marker** (Angelou), so it is never word for word the same.
- **The boundaries are tests** (Knuth, Dijkstra): an empty log, a last row of each outcome, and a long volley that must alternate block, retry-pass, block.
- **The cause is an inference** (Feynman): what I observed is eight `deferred` rows and no `stopped` while a marker was due; that the doorbell set the flag is not observed, and the rule does not depend on which hook did.
- **An outside witness** (Godel): the live check compares the count of `stopped` rows with the count of the reminder's text in the transcript over the same stretch.
- **Waiting-on re-dates are the cost to watch** (Breaker): three or more re-dates of one marker is a defect to read the same day.
- **Building found a second defect, which the walk could not have:** the real hold log holds two corrupt lines (lines 96 and 1588, written by two hooks at once), and `hold_log.read_all` raises on the first one. The first version read the log through it and would have been blind on the very file it was for. The hook now reads the tail line by line, skips and counts bad lines, and says so. Tested with a log carrying a truncated fragment and a broken line. The corrupt lines themselves (two writers appending at once) are a separate defect, filed in the letter to Aether.

## Falsifier (counts)
Over the next 20 stops where a marker is due, whatever the flag: the reminder blocks on the first, and never on two in a row, and never lets two stops pass in a row without a block except as the retry of its own block. If it blocks twice in a row, or two non-retry stops pass, remove it and look again.

## Order
Tests first (the retry passes, the other-gate stop blocks, never twice in a row over a long run, a failed log write does not block) -> walk -> edit -> run on the real log -> commit.
