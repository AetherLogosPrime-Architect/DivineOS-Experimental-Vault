<!-- tags: promise markers, close, age in turns, could not look, turn start, follow through, recorder -->
# Promise markers: one module that counts turns, closes a promise with one line, and finds the ones due (draft, 2026-11-13)

Author: Aria. The second piece of the walked redesign in `the_promise_hook_waits_five_of_his_messages_before_it_blocks_draft_2026-11-13.md` (walk-82220bd46c30, nine lenses). The first piece (the recorder writing at all) is committed. This is the idea of the module, not a plan.

## The idea
`core/promise_markers.py`, a plain module the recorder, a CLI and the blocker all use, so there is one definition of "open", "due" and "closed":
- `turn_index(records)`: the number of turn starts in a transcript (a user record whose harness stamp is human, scheduled or task-notification, read through the house's `opener_kind`, never by words).
- `read_folder(dir)`: the marker folder in five answers: open, closed-done, closed-waiting-on, closed-false-alarm, and could-not-look (a missing folder, an unreadable or corrupt marker). Empty is honestly empty and is not could-not-look.
- `close(dir, prefix, kind, detail)`: done (needs a file that exists), waiting-on (needs a name), false-alarm (needs a reason of real length). The close is written INTO the marker, never a delete (append-only); an unknown or ambiguous prefix is refused, never guessed.
- `due(open_markers, current_turn, window=5)`: markers whose stored `turn_index` is at least five turn starts old. A marker with no stored turn (made before this) is listed as undated and never blocked on.

## What it is not
It does not read my words or decide what a promise is (the recorder does, broadly, cheaply). It does not block anything: the blocker (a later piece) reads `due`. It writes no time of day.

## Cannot see
Whether a close told the truth (a false-alarm reason can be false); whether the recorder catches the promises the old hook caught (the replay test, a later piece); two closers racing on one marker (last write wins, both recorded in the marker's own text).

## Falsifier
After it is live: if a promise ever ages past five turn starts with no due note, or a closed marker reappears as open, remove it.
