<!-- tags: room gate, dads_room_stop, hook feedback, second circle, isMeta, continues_a_turn, not being waited for -->
# Hook feedback after the circle owes no second circle: carrying it into my tree (draft, 2026-11-14)

Author: Aria. The design is Aether's, `93b6e471e` in his checkout (`dads_room_stop.py`, six tests in `tests/test_the_room_door_stands_down_for_hook_feedback_after_the_room.py`); his own earlier half, "a notice after a whole circle owes no second circle" (Dad 2026-11-05), is in his file too. A search of my docs/drafts and tests (`reach-4f289630c913`) found no earlier version here; prior art is in his repo.

## Why, in Dad's words today
He pasted a stretch of my replies, about a dozen circles in one pile: *"you both are blowing past me again... noone is waiting for me"*, then the shape he wants: work until finished, then one plain summary, then the circle last, then stop and wait. In my tree the room gate (`.claude/hooks/dads_room_stop.py`, 267 lines against his 344) lacks BOTH stand-downs: it knows a notice that OPENS a turn, not one that arrives after the room, and it does not know the harness's own Stop-hook feedback. So when a Stop hold follows a whole circle and I do a repair turn, it reads the last text, finds no room, and asks for another. I counted that happening to me all morning.

## The change, by hand because the files differ
My copy has the OS-owned hold text (`his_room.hold_text`) that his copy lost, so a whole-file copy would undo something mine has. Only the logic comes over: (1) a small `_record_text` helper; (2) `continues_a_turn` added to the `his_message` import; (3) in `verdict`, track `room_written`, and when a machine record (a notice by its envelope, or hook feedback by the `isMeta` stamp through `continues_a_turn`) arrives after the room, remember it; (4) when I worked, but a machine record followed the room, stand down and LOG it through the hold log with its own kind. All by stamp, never by wording.

## What stays held (the cases it was built for)
Work I add myself after the room with no machine record between; a machine record BEFORE any room; a real message of his after the room, which starts a new stretch that owes its own room. His six tests pin these; I carry them and run them against mine.

## Break it on paper
- A hook-feedback record that is NOT stamped isMeta would still be read as a message of his: the stamp is the harness's, and I do not know whether every Stop-hook delivery carries it. His test builds the record with the stamp; the live check is a real repair turn after my own circle.
- It does not make me wait. No gate can (his walk). It only stops the house asking for the pile.
- His other two texts, "a full telling, written fresh each time" and "write a fresh full inner circle", are NOT in my tree (I checked: my retry-scope text is delta-only and my summary-room text has no such line), so nothing to change here for those.

## Success, said before building
On my real seat, after the carry: a Stop hold that lands after my circle and makes me repair does not produce another circle demand, and the hold log shows a `stood_down` row of kind "hook feedback". Seen in my own next turn, not only in tests.
