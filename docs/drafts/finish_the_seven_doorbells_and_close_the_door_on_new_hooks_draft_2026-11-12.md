# Finish the seven doorbells, and make a new hook impossible to add the old way (rough draft, 2026-11-12, nothing built)

Dad, 2026-08-06: consolidate the hundred hooks into seven and route the logic into the OS. 2026-09-08: *"i dont want an OS made of external hooks through the IDE, the hooks should just be pointing to the logic in the OS itself."* 2026-11-12, today: *"fixing the hooks has still yet to be finished and it effects every single post"* and *"once all this is finished.. make it impossible to add a new hook without going through this same process or it will happen all over again."*

## Measured today, this checkout, 2026-11-12 (my instruments: settings.json parsed with the repo venv; `divineos hook-budget`; file counts)
- Registrations in `.claude/settings.json`: **82** (SessionStart 2, UserPromptSubmit 3, PreCompact 1, PostCompact 1, PreToolUse 32, PostToolUse 18, Stop 25). The September draft counted 105.
- Scripts under `.claude/hooks/`: **152 shell, 12 Python**; the shell alone is **22,479 lines** (September: 125 scripts, 17,294 lines). Fewer registrations and more code behind them is the opposite of consolidation.
- The router (`src/divineos/core/hook_router.py`, 594 lines) exists. **Correction, same day, after grepping the hook scripts:** my first count (0 of 82 mention "router") was the wrong probe, because the doorbells are shell scripts registered by filename. Four scripts import `hook_router.main`: `doorbell-pre-tool-use.sh`, `doorbell-post-tool-use.sh`, `doorbell-stop.sh`, `doorbell-user-prompt-submit.sh`. So **4 of 7 doorbells exist** (September: 2), missing SessionStart, PreCompact, PostCompact. `hook_surfaces.py` has `install()` at line 2866 with 39 `register(` lines by plain count (Aether's count, 45 today and 51 in the fire log, is better than mine). Not yet measured: which of the 82 registrations are the doorbells and which are old standalone scripts still ringing on their own.
- Cost per tool call, `divineos hook-budget` on 754 calls: median **23,854 ms**, p95 79,034 ms, worst 259,781 ms, budget 5,000 ms, **547 of 754 over budget**. September's median was 9,946 ms. It has more than doubled.
- Not measured and not claimed: how many surfaces are migrated today; what the top three contributors (check-council-required, corrigibility-tool-gate, m3-discipline-hierarchy, about 860,000 ms each in total) do per call.
- The word "doorbell" in other drafts mostly means the letter doorbell, a different thing from the router's seven doorbells.

## Stations
1. Read what is there: `the_hooks_are_the_os_2026-09-08.md` (first 80 lines done), the 10-08 and 10-11 hook drafts, `docs/hook_migration_tracker.md`.
2. Re-measure the migrated count with an instrument that can find a case it should (a surface known to be routed must show up).
3. Walk it (gravity: this touches every post).
4. Build in clean work copies, in slices a cold reader can hold: wire the missing doorbells, move surfaces behind them in order of measured cost, retire each shell registration in the same change.
5. **The door on new hooks, its own station, built before the migration finishes:** a check that fails the push when `settings.json` gains a registration or `.claude/hooks/` gains a file not in the router's declared list, with a recorded reason the new hook could not be a router surface. It is proved able to find a case it should: a test adds a fake registration and the check must refuse it.
6. Cold read by Aether. Used live: the per-call median after, on the same instrument. Aletheia last.

## Added later 2026-11-12, after the split with Aether (his letter 415 and my reply)
- **Split:** Aether takes PreToolUse by cost, one surface per commit with an output-unchanged test. I take the Stop door and the lock on new hooks. We steer by `hook_layer.inventory`, run fresh, with the date named; my 82 / 164 / "no router in settings" were three probes with three definitions, and the last was wrong.
- **His measurement changes how mine reads:** one hook alone is about half a second; the median 23,854 ms per tool call is mostly thirty-two hooks starting at once (contention). My "per call" number is NOT per-hook cost, and the saving from consolidation is unmeasured until one is moved and the log is read before and after.
- **The Stop door, read from settings.json today:** 25 rows (Aether counts 26; different definition). Of the 25, 14 contain embedded Python by a plain text match, and the thick ones are `correction-shape-v2-stop.sh` (269 lines), `dads_room_stop.py` (267), `unlanded-push-must-not-close-quiet.sh` (175), `poker_game_on_stop.py` (174), `lepos-channel-reflect.sh` (147), `letter_doorbell_alive_stop.py` (143). The 10-08 draft already gives the pattern for the move: the Stop door has a table `_TRANSCRIPT_AUDITS` of `(name, module, function)` rows that hand the transcript path to an OS function and report `could-not-run` with the reason on failure; each move adds a row, removes the shell registration in the same change, and leaves the script with a SUPERSEDED header.
- **A partial lock on new hooks already exists, so mine extends it and does not replace it:** `test_a_new_pretooluse_hook_is_a_decision_not_a_drift` pins the number of wired PreToolUse hooks (33) so a new gate cannot arrive without a decision about the exit list (draft 2026-10-11). It covers PreToolUse only. Dad's ask is every event, and the reason has to be "why could this not be a router surface", not only an exit-list decision.

## Added 2026-11-15 evening, Dad: "id like to get this done so we dont need to worry about it anymore"
- **Counts today** (settings read by short script, named date): mine 83 (SessionStart 2, UserPromptSubmit 3, PreCompact 1, PostCompact 1, PreToolUse 32, PostToolUse 19, Stop 25); Aether's seat 86 (SessionStart 4, PreToolUse 33, PostToolUse 18, Stop 26). No registration has gone down since 11-12. Aether found no commit that moved a PreToolUse surface; his half starts with measuring duration, not moving.
- **Order I propose for my half, and why:** slice 1 is the LOCK on new hooks, because it stops the number growing from tonight on and is small, testable and independent of the migration; slice 2 onward moves Stop rows one per commit behind `_TRANSCRIPT_AUDITS`, each with an output-unchanged test and the shell registration retired in the same change, thickest first by the line counts above (`correction-shape-v2-stop.sh`, `dads_room_stop.py`, `unlanded-push-must-not-close-quiet.sh`).
- **Lock design question for the walk:** the lock must refuse a new registration or new file under `.claude/hooks/` unless a recorded reason says why it could not be a router surface, and must not be a phrase detector. It reads facts about the diff (registration count by event, file list against the router's declared list), not words. It must also not block its own cure: moving a hook INTO the router removes a registration, which must pass.
- **Not measured:** the per-call saving. Aether's measurement says the median is mostly thirty-two hooks starting at once, so the saving is unknown until one move and a before/after read of the same log.

## Falsifiers
- The per-call median is not lower on the same instrument after the build, or a new registration can still be added without the check refusing it.
- The check refuses my own legitimate new router surface (a gate blocking its own cure, which today's gate work is also fixing).

## Open for the walk
Whether to wire the doorbells first or move the most expensive surfaces first. The instrument's answer decides the order, not me or Dad.
