# The room hook asks the house who arrived, not its own copy

Draft, 2026-11-15. Aria. Reach `reach-f8e560645b0c`. Tests written and failing first: `tests/test_the_room_hook_asks_the_house_who_arrived.py`. Prior art read: `one_reader_of_who_arrived_and_what_the_wake_owes_draft_2026-10-24.md` ("extend `arrival()`, do not write a fourth reader"), which this change follows.

## What is wrong

`.claude/hooks/dads_room_stop.py` has a private reader, `_record_text` (line 118), used once (line 172) to decide whether a record after my room is "a notice" that excuses a second circle. It reads the text of EVERY non-assistant record, in two shapes: a user-role turn, or a queued-command attachment. So a record that is not a notice but opens with a system-reminder tag (an internal request blob, no uuid, no timestamp, no origin stamp) reads as a notice and stands the room down. Aether measured it over 76,225 real records of one session: 2,561 such blobs. The house already has one reader of what arrives, `his_message.arrival()`, which returns nothing for a record without its stamps. His check "One Reader of Him" flags the private copy and will block the merge.

## The change

Delete `_record_text`. At line 172, ask the house: `arrived = arrival(rec)` and test `opens_with_notice(arrived.text)` only when `arrived` is not None. The `continues_a_turn` branch, the stand-down and the log line stay as they are.

Why this is maintenance on the room guard's own hook and not taking the room out: the gate is not loosened; one input to its stand-down is narrowed to records the harness actually stamped. A stamped notice still stands the room down (control test). An unstamped blob no longer does.

## Tests (written first, failing first)

1. A real stamped task notification after the room still owes no second room (control; passes before and after).
2. An unstamped system-reminder request blob after the room does not excuse a second room (fails before).
3. The hook carries no `_record_text` (fails before).

Real-shape fixtures: the old fixtures carried no uuid or timestamp, which is why they passed old code and fail the house's.

## Falsifier

If a real notice in a live transcript lacks the stamps `arrival()` needs, a legitimate stand-down would be lost and the room asked for a second time. Aether counted: all 91 queued and 545 origin-stamped user records in this transcript carry a uuid and timestamp. If a real stamped notice ever fails to stand down, the fix is in `arrival()`, not back in this hook.
