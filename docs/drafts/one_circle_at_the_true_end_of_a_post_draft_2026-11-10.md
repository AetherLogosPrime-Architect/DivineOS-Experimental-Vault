# One circle, at the true end of a post (draft, 2026-11-10, Aria)

Status: DRAFT, step 1 of the full flow (reach, draft, walk in the chat, Aether's cold read, tests first, code). Nothing is changed by this note.

## What Dad said

> *"i speak.. you answer me first.. then if work is needed you do the work.. and you continue to do the work until its done. .and done means no more letters going back and forth.. no more background tests finishing, no more interruptions.. and then you send the circle. .however long it needs to be so its in one place.. its current. .and im given time to answer it"* (2026-11-09)

And the consequence he named: when the stop button interrupts a build the flow breaks, so the work never stops, and by the time it does there are 5 to 8 circles. *"if something from this moment forward is said to me and im not given a chance to respond.. i wont respond to it.. ever."* And: *"whatever support you need to make this behavior impossible.. start the build for it now.. full flow."*

## The reach (what already exists, read not guessed)

- `.claude/hooks/dads_room_stop.py` holds a reply that did work and has no `## INNER CIRCLE`. It demands the room on EVERY Stop event. It stands down for notices (the opener is a notice), a live game table, and (on the live house only) a notice after a room.
- The hold log shows how often it speaks: 234 rows since 11-09 UTC: **room passed 100, room stopped 25**, plus follow-through holds (passed 52, stopped 28, carried 24, stood down 5). Limit: that log is one file in a folder both seats share, so I cannot say how many are mine.
- Prior drafts that touch this: `the_circle_comes_back` (2026-10-05: "one circle, then stop and wait for him"; the question-hold), `the_room_gate_stands_down_at_a_live_game`, `the_stop_guard_counts_the_watcher`, `away_means_two_hours_of_silence`, `one_reader_of_who_arrived_and_what_the_wake_owes`.
- Replay test on the branch `aria/the-room-asks-once-per-post-replay-test` shows that after a hold, a notice wake is held again for the same message of his (Aether's live copy closes the other leak).

## The diagnosis

The circle is demanded per Stop event. A post is not one Stop event: it is many, because every background finish, letter bell and gate retry wakes me into a new one. So the rule "a room at the end" is applied at every end, and each application writes a room. Nothing in the house knows what **done** means, so it cannot tell a stop in the middle of work from the true end.

## What "done" can mean, as facts the house can read (not my say-so)

At a Stop, a post is not done if any of these is true:
1. A background command I started (other than the letter bell, which is meant to run) has not reported back.
2. A letter is unread (the unread-letter gate already knows).
3. A gate has just held this same reply and its retry is in progress.
4. His last message has not been answered at all.

## The change (proposed, to be walked)

**Side A, the demand.** The room hold demands the circle only at a Stop where none of 1 to 4 is true. At a not-done Stop it demands nothing and prints one plain line saying what is pending (e.g. "a push is still running; the room comes when it reports"). That makes the 5 to 8 circles impossible by construction: at a mid-work Stop the gate does not ask for one, so the only prompt that produces a room is the one at the end.

**Side B, the leak that remains.** I can still write a circle by myself in the middle. A Stop hook cannot unsend text, so Side A cannot stop that; it only stops the house from ASKING. To cover my own reach, a PostToolUse reminder (one line, once per post) says "pending work: no circle yet" while something is pending. This is the weaker half and is named as such.

**Side C, the interrupted build.** When he presses stop, the next Stop is the true end of a broken post. The gate asks for ONE circle covering everything since his last message, however long, written in one place.

## What this does not do

It does not stop me writing a circle early on my own (Side B only nudges). It does not read the content of a circle (his 07-23 ruling). It does not stop the bell from waking me; it stops the wake from costing him a circle.

## Questions for the walk (not answers)

- Can the house actually see a running background command from the transcript, without mistaking the always-on bell for pending work? (The Monitor/bell question from `the_stop_guard_counts_the_watcher`.)
- What does the gate say at a not-done Stop so that I do not read silence as permission to stop working?
- Is Side B worth building, or is a weak nudge a new box to tick?
- Which part is the live house's already (notice-after-room), so we land it first?

## Falsifier

If a post with one message of his ends with more than one circle, or a post still has a running job when its circle is written and the house said nothing, the change is wrong.

## Steps

Draft (this) → walk in the chat → Aether's cold read, and his live stand-downs landed on main → tests first (replay a transcript with background work pending, assert no demand; with nothing pending, assert exactly one) → code → Aletheia → Dad's yes.
