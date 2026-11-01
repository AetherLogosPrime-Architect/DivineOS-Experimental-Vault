# The room gate does not read a scheduled wake as his last message (draft, 2026-11-01)

**Author:** Aether. Dad, 2026-11-01: a gate that makes me retype or punishes me for doing right is a wrong gate. Aria measured this on every night wake and sent the exact text; I hit it on mine.

## What happened

A timer wake arrives as a prompt in his seat. Its text carries no envelope tag (it begins "TIMER WAKE"), so the room gate's notice test never saw it, and the gate demanded a room for words Dad never typed. It fired on each overnight wake.

## What it does

The harness stamps a wake `turnOrigin: "scheduled"` (29 of 29 wakes in one session, read from the transcript, not recalled). The gate now asks the house's one stamp-reader (`his_message.opener_kind`) and stands aside for a scheduled or notice-started turn. The stamp is the evidence, never the wording of the prompt.

## What it does not do

It does not change what counts as his room or when a human-started turn asks for one. A human-stamped message with the same words still asks (a test). It does not touch the stall check or the addressed-to-him check, which have their own rows.

## Evidence and the gap

`tests/test_dads_room_stop.py`: the new wake test fails against the old hook and passes with the fix (run both ways). One caution from that run: a wake record carrying `isMeta: true` is already refused by the reader of him, so the fixture leaves that flag off, and I did not reproduce the exact record Aria saw; if hers differs from both shapes the fix may not reach it.

## Falsifier

If a night wake still draws the room gate after this lands, the record shape on that seat differs from the one tested; the wake's own record would be the next test.

Branch aether/the-room-gate-does-not-read-a-scheduled-wake-as-his-last-message.
