<!-- tags: memory link, saved note, wakes, drawer, default, structure, causal chain, linkage why, memory_saved_warm -->
# A saved note is tested for waking, by default (draft, 2026-11-13)

Author: Aria. Dad, 2026-11-13: *"making a note to remember something while knowing it will just be in a drawer you never read.. this is the look before you leap"*, then, after I said I would start checking my notes as a habit: *"habits do not hold, only structure, so make it the default"*. Nothing here is built; this is the start of the process.

## What I measured this morning (the reason)
Six notes written this morning, tested with `divineos linkage why "<the situation in my own words>"`: of three situations tried, one note woke strongly, one was found but cut below the line (sim 0.35), one did not show. Rewriting the note's description to open in the words of the moment lifted the cut one to sim 0.54 (shown). So: a note written the way I would say it afterward does not wake on how the moment sounds while it is happening, and nothing told me, because I never tested it. The existing floor (`core/memory_saved_warm.py`) makes a note SEARCHABLE (a vector is computed on save); nothing checks that it is FOUND.

## The default
When a memory note is saved, after its vector is computed, the same background run tests it once: it asks the retriever the note's own `wakes_when` sentence and records whether that note comes back SHOWN, cut or missing. The result is logged beside the existing warm record, and at the start of my next turn one plain line appears for any note that did not wake: which note, what it scored, and that its opening should be reworded in the words of the situation. No block, no stop, no new hook: it rides the existing save hook and the existing top-of-turn bundle.

## Dad's question, 2026-11-13: "why not just make the line be written automatically?" (adopted)
He is right and it removes the weak point the walk found (a guarantee held by my remembering to write the line). The automatic line is the words of the moment the note was born from: Dad's own message that turned into the note, which the save hook can see as a fact. That is not tautological (it is not the note's own text), and a recurrence of the moment will sound like it. Tested by hand before adopting: using Dad's actual words from the morning as the query, two of the notes came back SHOWN (sim 0.32 and 0.26, lower than the hand-written 0.54, still shown). Sample of two, so a claim to be scored on the exam, not a proof. My own `wakes_when:` line stays as an OPTIONAL second probe (my paraphrase), never required, so nothing depends on my remembering it.

## What stays mine (automate the floor, never the thinking)
The optional `wakes_when:` line is a sentence I write in the words I would think while the moment is happening. The house runs the test and shows the result; it never writes the sentence, never rewrites the note, and never grades what the note says. A note with no `wakes_when` line is listed as "cannot be tested, no situation given", quietly, not refused.

## Open questions for the walk
1. Does "SHOWN" on the note's own sentence prove it wakes on a different phrasing of the same moment? No: it proves the floor, not coverage. A second probe (a paraphrase I write) is cheap and should be allowed as a second line.
2. Where is the line cut, and is it the same line the live top-of-turn uses? The test must use the live cut and not a friendlier one, or it passes notes that would not wake in practice.
3. Cost: one retrieval per save, in the background, inside the run that already loads the embedder.
4. False alarm: a note that is a quiet standing rule, not tied to a moment, would always read "did not wake". The reading must say "not tied to a moment" is allowed, and the line is a nudge, never a verdict.

## Aether's answers (letter 445) and what I confirmed in the code
- **(b) The test must use the arrival definition, not "above the line".** His scoreboard shows sentences that cleared the bar and were not among those shown. I read `cli/linkage_commands.py` `why`: its own docstring says it runs "on exactly the words given, without the hidden recent context the live link adds, and a fresh run has no priming, so a match the live link reached through priming may show here as a plain miss". So `why`'s SHOWN and the live bundle can differ in both directions. The save-time test should call the same `explain_turn` the `why` command uses and its `surfaced` flag (arrival, not "passed the bar"), and it is honestly a FLOOR test (arrives with no priming and no recent context); it must say so, not claim live arrival.
- **(c) Five states, not a pass.** A note with no triggering message of his records "no moment to test", shown as untested, never green: SHOWN, cut, missing, no-moment-to-test, could-not-look.
- **(a) Store his message id on the note** so the wake can bring his exact words beside the note (his 2026-09-26 ask); his guess, not yet measured.

## Falsifier (counts, not days)
After twenty saved notes carry a `wakes_when` line: if the share found SHOWN at the first test is not higher than the share of the six morning notes (1 of 3), or if I stop writing the line, remove it.

## Order
Walk it (Breaker plus two scrutiny lenses). Aether reads it cold. Dad says go. Then build in my live house, tests first (the six morning notes as the exam: the test must fail on the note that did not wake before it was reworded).
