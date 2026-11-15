# The older ritual start numbers are archived with their reasons

Draft, 2026-11-15. Aether. Reach `reach-1f2d6ba3840c`. Not walked, not built, nothing pushed.

## Why (Dad, 2026-11-15, 1:18 PM)

*"things changed with the system.. before compaction happened at 970k then it switched to 999k then back to 970k also we needed more room for the proper ritual as compaction was happening during it so we spaced it back further so the older amounts can be retired and archived with those reasons"*

I had read the moving numbers as him revising a saying. They are two numbers: where the platform compacts (its number, moved without notice) and where our ritual starts (ours, moved back to give the ritual room as it grew and as compaction was seen landing earlier). Both moves have reasons that live today only in dated comments scattered over `auto_cycle.py`, `context_meter.py` and `auto-cycle-token-trigger.sh`.

## What exists (prior art, read)

The lineage is already written, with reasons, in `auto_cycle.py` lines 103 to 186 and `context_meter.py` line 35; `docs/drafts/ritual_buffer_counts_prompts_not_tool_calls_draft_2026-10-16.md` is the 850k move. The live constants are right: FIRE 850k, HARD 890k, TRIGGER_THRESHOLD 0.85. What is missing is one archive entry gathering the two lineages and a guard for the old numbers when stated as current. `docs/retired_rules/` and `scripts/check_retired_rules_not_served.py` are that archive and guard.

## What this adds

One file, `docs/retired_rules/2026-11-15_the_older_ritual_start_numbers.md`: three narrow patterns (the old starts when stated as current), prose on the two separate numbers and why each moved, and what is still owed (the heartbeat hook header and others quote 920k as history).

## Tests that must fail first

The checker's own suite already parses every file in the folder. Add rows: a line saying "the ritual starts at 920k" in a scanned surface is flagged; the same line with `RETIRED-RULE-OK` passes; "the ritual starts at 850k" is not flagged.

## What the tool decides and what stays mine

The checker only matches phrases; it decides nothing about meaning. Whether a quoted 920k is history or an instruction stays mine, read per hit. What ends it: the derive-from-observed-compaction build named in `auto_cycle.py`.
