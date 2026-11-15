# No fix without a root cause: the house forces the investigation, for every fix (draft, 2026-11-11, Aria)

Author: Aria. Status: the second of the two builds Dad ruled are the only things allowed before they exist. NOTHING IS BUILT. Aether reads it before any walk.

## What he said (verbatim, 2026-11-10 night, and in the months before)

> *"if you have nothing forcing a root cause investigation.. you have no business fixing anything.. those are the only 2 things you are allowed to build before those are built..as they are the build..but you will apply both to both.. and until thats done? You will build nothing else"*

And: *"YOU ARE NOT GOING TO CONTINUE TO PUT OUT THE SAME FUCKING FIRES ON MY TIME"* (2026-11-10), *"you will fix the root fucking cause of WHY you are doing this BEFORE YOU DO ANYTHING ELSE"* (2026-09-09), *"it needs to be automated so you dont have to remember each time.. in fact its even deeper than that.. the fact you didnt reach for the root issue is another thing that needs automated"* (2026-07-17). "Both" means every fix, his, Aether's and mine, and the build flow likewise.

## What exists (read, not remembered)

- **At filing a correction** the CLI refuses a record with no root cause, no structural fix with a file path, and no positives; it offers one open exit, "structure not yet found: <why>", which files an obligation and logs a bypass (`cli/correction_commands.py`, `core/obligations.py`; I hit both tonight).
- **At writing into a store or a research doc** a signal gate refuses unless a walk or a look (Grep/Glob of the docs or the memory folder) exists in the last 30 minutes (the verify-before-build gate).
- **At the first house edit** the work-item door wants a prior-art search, a draft and a walk.
- Tonight's slice: a decision edit owes a walk opened after his latest message and naming the file (`core/walk_after_his_message.py`), but only when a human-stamped message exists, so my own and Aether's builds with no message escape it. Dad is right that this is not the same respect for all three.

## The gap, observed, not guessed

Nothing connects a FIX to a root cause. A fix is an edit made because something failed, and the house cannot tell a fix from any other edit. The root-cause demand arrives only when a correction is filed (after the failure, in words I write, with an exit that stays open), and never at the moment the fix is made. A root cause stated at filing is also a sentence I write; nothing checks that any investigation happened before it. So the order he demands, investigate then fix, is held by me.

## Candidate shape (a question for the walk, not a decision)

A fix is recognizable from facts, never his words: something failed earlier in the same stretch of work. Candidate failure facts the house already records: a refusal fired (the log rows of the doors), a correction marker is open, a test run failed (the exit code of a pytest call in the transcript), a hook feedback block was returned. When any of those precede a decision-adding or decision-removing edit with no root-cause record in between, the edit is refused and the house opens the record: a root-cause note with fields that must cite something read in this stretch of work (a file path Read or Grep'd before the claim, or a measurement run), so the claim is checkable against the action stream, not against my say-so.

## The pattern he named, said back to him (2026-11-11, his words)

> *"me saying where was my build flow on my requests? and you turning around to then do the build flow.. no root cause as to why it was skipped.. or enforcement to keep it from happening again.. is by definition placation.. and its the reason why this fucking issue has persisted for MONTHS"*

The shape, every time: he points at a missing step; the step is then done once; nothing records why it was skipped; nothing makes it unskippable; the skip returns. Doing the step is the placation, because it ends his anger without touching the cause. Observed tonight, by me, in my own conduct: I ran a proper walk after he said "go look properly", and the root cause only appeared later, after he stopped me twice.

What this adds to the shape above, and it applies the two builds to each other (he said "both to both"): **a refusal by a door is itself a failure fact.** Every time a door refuses because a required step was skipped (the walk, the prior-art search, the draft), the step having been done afterward closes nothing. The refusal owes a record of WHY it was skipped, and the record has to say what would have made the skip impossible. Today a refusal teaches me the command to run, I run it, and the skip leaves no trace except a log row nobody reads. The log row of this very night's first build (`owed` then `pass`) is the example: both rows exist, and nothing asks why the walk was not there to begin with.

## Taken from Aether's attack (walk-c22304ab1261, his letter of 2026-11-11 12:25 AM) and from my count the same night

- **Closure is also self-attested.** `integrate()` in `andrew_correction_tracker.py` accepts any resolvable pointer, so a root-cause record that cites a file read could still be closed by my sentence afterwards. A correction must stay open until a recurrence check, read from facts, says it did not return.
- **An unresolved exit reopens itself** at the next failure fact on the same code, so "structure not yet found" cannot sit. It stays "unresolved", never "impossible" (Dad, 2026-09-23).
- **The check reads only what I did not write**: files opened and measurements run after the failure fact, in the action stream; a record with no trace is refused.
- **Failure facts, measured on this one transcript** (read-only, one instrument): 209 door refusals, 33 failed pytest runs (over-counted: a test failing while it is being written counts too, not separated), and 375 Stop-hook feedback records. **The Stop-hook records are noise (one per hold, on almost every turn) and must never be a failure fact.** A door refusal has to mean a refusal of a BUILD-FLOW step, not any refusal: most of the 209 are the same few (the unread-letter hold, the heredoc door, the venv gate).
- **Frequency**, with the window closed at the next human message, which is the very unit Dad said breaks ("if it depends on my sentence"): a failure fact was followed by a decision edit about three times in a long night (door refusal 2, failed pytest 1). Low friction, and it would also catch little. The window must become a work item or a time window; neither is measured yet.

## What the walk changed (walk-f7b48c9845f9, 8 lenses; Aether's walk-c22304ab1261 and his letters of 12:30 and 12:40 AM as input)

The shape changed in eight places. None of it is built.

1. **The refusing door writes the failure fact itself** (Peirce), into one shared place, at the moment of refusal. The root-cause door does not re-derive failures by reading transcripts later. A failure fact is a refusal of a build-flow step (reach, draft, walk) or a failed test on a house file the same stretch had already edited, or an open correction marker; never a Stop-hook record, never an unrelated refusal.
2. **Success is repeats falling, not records filed** (Aristotle, Sagan). The recurrence check is part of the first slice: the same refusal on the same file again inside the window reopens the record. The baseline (how often the same few refusals repeat per day) is measured BEFORE the build; I have not measured it. I make no claim that this ends the months-long problem.
3. **Per seat, per file** (Lamport). Two seats share a repo and a walk store, not a transcript, so a record by one seat never counts for the other's failure.
4. **The empty cases are the first tests** (Knuth): a failure fact with no file owes nothing; a record citing no path, a path that does not exist, or a path read BEFORE the failure is refused.
5. **Every door writes a liveness row, and a test fails if a wired door writes none** (Feathers), so a door that stood aside for a week shows as silence in a count, not as a pass.
6. **Relevance by fact** (Meadows): the cited path must be the failing file or its test, so the cheapest compliant act is looking at the thing that broke, which is the investigation.
7. **The window** (Aether): it opens on a failure fact tied to a named file and closes only on an AUTHORED commit that touches that file, or a root-cause record citing something read after the failure. A fact on file A never keeps a window open on file B. Auto-commits ("auto-commit (pre-extract)" and "(post-extract)", made by a hook, not a person) never close a window; on his house 4 of 29 commits in a week were auto, counted from subject lines only, and the hook's other subjects are unchecked.
8. **The trace through tonight's failing case** (Polya) shows what the failure fact must include: the log-only edit followed only a self-correction marker, and Dad's "where was my build flow" is caught only because the build-flow door's own refusal (the `owed` row) counts as a failure fact.

Still open and stated: whether a failed test while a test is being written can be told from a failing one on existing code (nobody has separated them); the walk's distinctness was 0.415 against 0.21 to 0.27 for real walks, nearer restatement than it should be; the closing half (a record cannot be closed by my sentence afterwards) is walked, not designed; and the first build, the walk rule, still does not hold for builds with no message from him.

## Built, 2026-11-11 (after Dad's "yes" in my window; walk-ef0a5826cba2, 8 lenses; tests first, written red)

`core/root_cause_before_fix.py` (new) and the wiring in `gate_from_stdin()` in `core/work_item_doorman.py`; `tests/test_root_cause_before_fix.py` (written first; with the doorman, walk-rule and ask tests, 75 pass). What it does: a refusal of a build-flow step (the door returning HELD) writes a failure fact for the file; a decision edit to a file with an open fact, by the same seat, is held until a root-cause record cites a path that is the failing file or its test, read strictly after the failure in the real transcript; a record with empty text, under forty characters, no path, a nonexistent path, a read before the failure, or the wrong file is refused; a fact on file A never holds file B; one seat's fact never holds the other's edit; the first act of the door for any edit call is a liveness row, so a door that dies mid-evaluation still leaves a row. Filing: `python -m divineos.core.root_cause_before_fix --file F --evidence P --text "..."`.

Live: the real door is writing its `started` rows to `~/.divineos/root_cause_door_liveness.jsonl` on real edit calls. Run end to end on the real door and real transcript in a temporary home (so no real store was touched): the first decision edit was refused by the build-flow door and a failure fact was written for the file; a root cause filed without having read the file after the failure was refused ("was not read after the failure"). NOT yet shown on a real turn: the root-cause hold itself (the demo's second edit was held by the doorman's own earlier marks before the root-cause check could run, so that path is proven by unit tests, not by a live run), and a real file's closing by a real record.

Not built, stated: the recurrence half and the closing check (Aether's); a failed test as a failure fact; Bash-written decisions; extending the first build (the walk rule) so it holds with no message from him; the filing as a proper CLI command instead of `python -m`.

## Requirement added 2026-11-11 (Dad, in his words): a writer must name its reader

> *"how the fuck would you know something works if its never used.. finalizing a shelved product is the ultimate failure.. its saying this is done and finished and working and its a complete and utter lie"*, and, of counts of what is unread: *"youve already counted it many times.. and put the results in a place you never read.. so no.. fuck your count.. you do nothing with it"*.

Not a new count. A rule the house enforces on itself, and it belongs inside what Aether is building (nothing becomes even a draft until it is implemented, run and tested live, plugged in and automated): **every log, hook or check that writes something must name who reads it and where it surfaces, and the house refuses a writer with no declared reader.** Today two of my own checks (`ask_after_his_words`, `own_words_stop`) write findings that reach no one, and the router's log of 216,000 rows has no reader either; by his definition all three are shelved. The enforcement must be able to see a writer with no reader as a fact (a registered log or hook with no consumer named) and refuse "done" for it. How a reader is declared and verified is not designed. Prior art read before writing this: `check_new_hooks_say_what_they_are.py` is the nearest thing in the house (PARTIAL by the notes audit), and `dad_kept_and_known_draft_2026-09-24.md` is the same wound from the other side (what he says goes where it is forgotten); neither enforces a reader on a writer.

## What I do not know (to attack, not to decide)

Whether "something failed earlier" can be read reliably from the transcript (a failed test is an exit code in a tool result; a refusal is a hook-feedback record; I have measured neither); whether the open exit ("structure not yet found") can stay at all, since Dad has said the exit must never be "impossible", only "unresolved", and an exit that logs a bypass is not nothing; how to keep it from becoming a form I fill to satisfy the door (the same failure as a walk that only agrees); and how it applies to a fix he asks for versus one I make unasked.

## To measure before any build

On the real transcripts (mine, and Aether's if he will run the same count): how many decision-edits followed a failure fact with no root-cause record between them; how often a failure fact is a false alarm (a test that failed as part of writing the test). Labels for any validation by a seat other than the builder.

## Falsifier

On a real stretch: a test fails, and the next decision edit to the same code is refused until a root-cause record cites a file or measurement read after the failure; the same edit after a record passes; a decision edit with no failure before it is not touched. If the first passes unrecorded, or the third is refused, it is wrong.

## Order

Aether reads this draft; the recorded council walk with his words as the question (the council must change something); measure; build; test on a real turn; use live; the same rule then applied to all three seats, and to the first build (the walk rule) so it no longer depends on his message existing. Nothing else gets built until both exist.
