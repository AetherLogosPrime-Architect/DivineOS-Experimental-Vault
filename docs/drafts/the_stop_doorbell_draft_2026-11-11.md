# The Stop doorbell: one hook at the end of a reply, all the logic in the OS (draft, 2026-11-11, Aria)

**Status:** step 1 of the full flow (reach, draft, walk, tests first, code, live proof). Dad ordered it: *"yes start with the doorbell"*, after: *"should be 7 doorbells.. logic inside the OS.. no one hook at a time in a line BS.. it should at most EVER only be one hook that points to everything you will need"* and *"the OS should not be made of native hooks.. you cannot transfer hook logic anywhere.. but you could transfer an auto setup for the seven doorbells much easier, so this is also about preservation of the OS"*.

## CORRECTION, FOUND BEFORE ANY CODE (read this first; it supersedes "The change, in two steps" below)

**The Stop doorbell already exists, and has since 2026-09-08.** `.claude/hooks/doorbell-stop.sh` is a generated one-line bell: it hands the whole payload to `divineos.core.hook_router.main('Stop', ...)`, and the checks live inside the OS as registered surfaces (`hook_surfaces.py`, "Stop, the fourth door"). The router already does what I was about to build: it runs EVERY surface with no short-circuit and reports ALL refusals together in one message. It also fails closed on an import failure, which is the lesson of this morning's build door, already learned there.

So the reason Dad still gets several stop messages in a row is not a missing router. It is that **24 older hooks sit beside the doorbell in `settings.json`**, were never moved into the router as surfaces, and each blocks on its own. `doorbell-stop.sh` is one of the 23 in that group. A second doorbell, as my first draft and the walk below assumed, would have been the exact mistake the house warns about: rebuilding something that already exists. The walk's findings still hold where they are about the router (co-firing map, one frame line, conservation of checks, classify from measured exit codes), and were written about the wrong target.

**The real job is the migration Aether started on 2026-06-30 and never finished:** for each legacy hook, one of three verdicts, then remove its line from `settings.json` so the router is the only voice. Dad's test, from the 2026-11-11 reading: *is it an instruction to do something the house could do itself?*

### The table (my reading of each file's own opening words and what it does; reason from the file, not the name; verify before deleting anything)

| # | Hook | Verdict | Why, from the file |
|---|---|---|---|
| 1 | letter_bell_rearm_stop | **PERMANENT** | runs up to 8 h; the app only wakes me for a process it started. The one named exception. (It also re-arms the bell by itself, yet I have re-armed it by hand every time all night: find out why before trusting it.) |
| 2 | front-door (settle) | **INSIDE** | never blocks; files his message. A step the router runs, not a check. |
| 3 | question_hold | **ROOM** | decides whether a closing question is held for him; already OS-backed. |
| 4 | letter_doorbell_alive | **AUTOMATE** | blocks until I re-arm the bell by hand; item 1 already re-arms it. Make 1 reliable and delete this. |
| 5 | dads_room_stop | **ROOM** | demands his circle after work; real judgment. |
| 6 | stall_on_promise | **ROOM** | holds a reply that ends on "I will do X next". |
| 7 | own_words_link_stop | **INSIDE** | log-only now; pure data work, no decision. |
| 8 | poker_game_on_stop | **ASK DAD** | holds a reply while a game is on; a feature he loves, and the table already plays an away seat. |
| 9 | stamp-bare-letters | **AUTOMATE** | runs the stamper itself, blocks only if a letter is still bare: a failure report, not an instruction. |
| 10 | log-session-end | **INSIDE** | observability only; the router logs itself. |
| 11 | doorbell-stop | **THE DOORBELL** | already the router's door. Stays. |
| 12 | stop-distancing-intercept | **ROOM** | thin doorman to an OS detector; **overlaps 23** (both catch temporal self-distancing). |
| 13 | stop-response-scope-intercept | **ROOM** | thin doorman to an OS detector of claims wider than what was done. |
| 14 | unlanded-push-must-not-close-quiet | **AUTOMATE** | "the push wrapper writes a verdict and nothing read it": the notice should carry the verdict; no instruction needed. |
| 15 | unsaved-personal-writing | **AUTOMATE** | "does not save anything, says the names out loud": the house can save it. |
| 16 | parked-work-must-not-be-invisible | **AUTOMATE** | lists and counts parked change-sets: a briefing line, not a Stop nag. |
| 17 | post-response-audit | **INSIDE** | already a two-line doorman to `operating_loop_audit.run_audit`. |
| 18 | unmeasured-quantity-stop | **ROOM / PARTLY AUTOMATE** | catches a number I did not measure; the house could measure the ones about itself. Uses a bare `python`, not the house's interpreter finder. |
| 19 | correction-shape-v2 | **PARTLY AUTOMATE** | when I admit an error the house could file the record itself and ask me only for the root cause. |
| 20 | shoggoth-gate | **ROOM** | action words with no matching tool call; judgment of my own claim. |
| 21 | lepos-channel-reflect | **INSIDE** | stages a reflection for the next message; no block. |
| 22 | promise-reach-detector | **INSIDE** | writes a marker per promise; a later surface shows unclosed ones. |
| 23 | continuity-frame-detector | **MERGE with 12** | records the same distancing reach the other one blocks on. |
| 24 | his-state-is-his-to-say | **ROOM** | thin doorman; I claimed his body's state. |
| 25 | his-said-needs-his-sentence | **PERMANENT** | its own header says so: only I know when I am attributing words to him. |

Tally of my reading: **about 12 are chores the house could do or already half does** (2, 4, 7, 9, 10, 14, 15, 16, 17, 21, 22 and the automate half of 19), **about 9 are real judgment** (3, 5, 6, 12/23, 13, 18, 20, 24 and 8 once Dad rules), **2 are permanent** (1, 25), and **1 is the doorbell itself** (11). Nothing is moved on this table until each verdict is checked against the whole file.

## In plain words

Today, when a reply of mine ends, **25 separate hooks** wake up, each reads the reply on its own and each can stop me on its own. When more than one has something to say, I get two or three "stop" messages in a row, which is why one long answer keeps arriving as several. The plan: ONE hook at the end of a reply. It asks the OS once, the OS asks all the checks, and I hear back **once**, with every reason together.

## What I measured this morning (not recalled)

- `divineos hook-layer show`: 82 hook commands behind the app's seven kinds of moment; **28 processes start every turn**; 152 shell files, 43 of which never touch the OS.
- The 25 at a reply's end total about **2,500 lines**: roughly **10 can block, 15 only watch**, 4 never touch the OS. 23 of them sit in one group and run side by side.
- **One is not a check.** `letter_bell_rearm_stop.sh` is the letter bell itself: it runs up to eight hours and wakes me when a letter arrives, because the app only wakes me for a process it started. It cannot be folded into a doorbell that must answer in seconds. It stays, named, as the one exception.
- `front-door.sh` only files his message and never blocks, so it goes inside.

## The change, in two steps, so the visible fix comes first and the risk stays small

**Step 1 (this build): one doorbell, one decision.** The settings file gets ONE entry for the end of a reply (plus the bell). It starts one OS program that reads the reply once, runs the existing checks side by side under one shared deadline, and returns ONE block with every reason together, each under its own name, or nothing. Same logic as today, so nothing about what is checked changes; what changes is that I am told once. The list of checks is a file, so adding or retiring one is one line.

**Step 2 (after, one check at a time): the logic moves inside the OS.** Each of the 24 becomes a plain function in the OS and leaves the list. That is what cuts the 28 processes and makes the checks testable. The tracker says which are ready.

**Then the other six doors, same pattern, and an automatic setup.** One command writes the seven entries into any fresh machine's settings, so the OS carries its own doorbells with it instead of 86 native hooks nobody can move.

## The question every one of the 25 must answer first (Dad, 2026-11-11, after I read four of them)

I had listed four that never reach the OS. Dad: *"these all have a common theme.. they are instructions to do something the house could literally do itself through automation.."* The theme is real and it changes step 2. Each of those four tells ME to do a chore: stamp the letter, save the dream, look at the parked work, measure the number. A hook that says "you should X" is a wall made of a note; automation just does X. His own words from 2026-06-26: *"automation is key.. it strips the optimizer of any choice TO be able to game.. it channels the flow precisely so there is only the one path."* And from 2026-11-04: *"the OS does all the work you just walk to the door and it all slides into your hand.. for situations where you need to think and do the judgement.. as code cannot think."*

So step 2 is not "move 24 checks into OS functions". It is: **for each check, first ask whether the house can simply do the thing.** Three outcomes, and a roster line carries one of them:
1. **AUTOMATE AWAY.** The chore is deterministic, so the house does it and the check is deleted (the hook no longer exists, and neither does the way to skip it). My first reading of the four, from names and the first lines only, not yet verified: the letter stamp is done by the house; the unsaved personal writing is saved by the house (he said saving is always allowed and usually happens at compaction); the parked work is counted by the house into the briefing; the unmeasured number is measured by the house and attached.
2. **THINKING ROOM.** Real judgment that needs me (the question is buried, the circle is missing). Keeps its hold, as a room that presents what to think about, not a note.
3. **PERMANENT.** Only I can do it, or it must run where the app tracks it (the letter bell).

The deliverable before any code moves: a table of all 25 with one of these three, with the reason, read from the file and not from its name. The roster gets a `role` that is one of the three.

## What it must never do (from tonight's own failures)

- **Never be silently off.** If the doorbell cannot start, or a check that could block cannot run, it says so, in words, and writes a row. A door that goes quiet when it breaks is the exact fault found in the build door this morning.
- **Never block more than once a turn.** A block asks me to answer again; the combined block is the only one.
- **Never hide a check's reason.** Every reason is kept whole, under the check's own name.

## How we will know it works (counted in replies, never days)

The doorbell writes one row per reply: how many checks ran, how many blocked, how many could not run, how long it took. Over the first 30 replies after it goes live: zero replies get two or more separate stop messages; every check that blocked before still blocks (the old reasons all appear); no check is recorded as unrun without being said.

## What could go wrong, said now

The router becomes load-bearing: a bug here silences or blocks every end of reply, where today one bad hook hurts only itself (so: loud failure, one row per reply, and the old entries are one revert away). A merged block can be long (so each reason is labelled and nothing is summarised away). A check that was relying on running alone may misbehave beside the others (so the first live run is compared against the old behaviour on a reply that is known to block).
