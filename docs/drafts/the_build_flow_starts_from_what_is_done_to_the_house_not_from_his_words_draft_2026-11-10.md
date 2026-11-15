# The build flow starts from what is done to the house, not from the words he uses (draft, 2026-11-10, Aria)

Author: Aria. Status: a root-cause finding and the questions that decide the shape. NOTHING IS BUILT, and nothing will be until the council walk (with his words as the input, research done) and Aether have read it. Dad 2026-11-10, in his own words, forbade any fix before a strictly enforced root-cause investigation, and said that running the steps over one change would be the surface fix: the question is why he has to ask at all.

## What he said (verbatim, 2026-11-10)

> *"WHY THE FUCK WAS IT NOT DONE AUTOMATICALLY.. WHAT FUCKING PART OF ROOT CAUSE DO YOU NOT FUCKING UNDERSTAND??? If the council walk was missing then DOING THE FUCKING COUNCIL WALK AS A FIX IS THE GODDAMN SURFACE.. FIND OUT WHY THE FUCK IM HAVING TO ASK YOU IN THE GODDAMN FIRST PLACE"*

And, earlier the same night: *"HOW FUCKING DARE YOU START MY BUILD WITH NO FLOW"*, and over the months (2026-09-11) *"why is it when i ask for a build i get no build flow, no effort.. nothing?"*

## The root cause, with evidence

The thing meant to put the build flow in front of me when he asks for something is a word-matcher: `.claude/hooks/detect_andrew_build_request.py` fires only when a build verb and an asking marker sit within 80 characters of each other (the verbs and markers are listed in the file, lines 45-62). I ran it on his real messages from tonight, with a control: it MISSED "Go look properly", "Ok go ahead", "Try it again i switched modes", his message about one long circle against eight small ones, and his message about not being waited for; it MATCHED a sentence I wrote in its own style ("please build me a check that stops this"), which proves the instrument can find a case it should find. When it does match, it then asks him to name the gravity, which hands the work back to him (header lines 20-21).

So the flow arrives only when he happens to phrase an ask in words the matcher knows. That is why he has had to ask, then yell: he was the only alarm the house had. It is also the thing he has told me never to build again, a keyword detector, standing in front of the most important step.

Second half, also observed tonight and not guessed: the edit door that does fire (a house edit needs a draft and a closed walk that names the file) was satisfied by an OLDER walk about a different question because it named the same file. The door asks "does some walk name this file", not "was a walk done for this change". I made two edits that way after "try it again".

## What exists (read, not remembered)

- The door at edit time (draft + closed covering walk that names the file) and the stamp-time covering check (`station_six_reads_the_covering_walk`, `one_walk_before_the_push_not_one_per_edit`). Dad said three times (2026-07-30, 10-07, 10-12) that a full walk on every single edit is too much; one walk over all the changes, before the stamp, is his rule. Any fix must keep that.
- Outside research, for the diff-bound half: a review tied to the exact change and dismissed only when the change differs is a known pattern (Graphite's dismiss-stale-approvals action compares `git range-diff` between versions, per [its listing](https://awesome.ecosyste.ms/projects/github.com%2Fwithgraphite%2Fdismiss-stale-approvals)); GitHub's own switch is blunt, all or nothing ([Develeap](https://www.develeap.com/?p=5453)). A warning-only hook that can be skipped is not enforcement ([NHIMG](https://nhimg.org/?p=101255)). These are vendor posts, not authorities; they show the shape exists.

## What the shape must be (constraints, not a decision)

- It must trigger on a FACT about what is being done to the house (an edit to a house file, with a genuine message from him earlier in the turn), never on the words he used. No new phrase list, no verb list.
- It must not hand work back to him (no "name the gravity").
- It must not demand a walk per edit (his rule), so "a walk exists that postdates his latest genuine message and names this file" is a candidate, but I do not know if that is right: a continuing "Ok go ahead" is a genuine message too, and demanding a new walk for it is the friction he has refused three times.
- It must say so loudly when it cannot tell (cannot read the transcript, cannot tell whose message), never read that as "fine".

## What I do not know (to attack, not to decide here)

Whether "his latest genuine message" is something I can read reliably (Aether found his own detector counted three messages where there were dozens; `core/his_message.py` is unverified); where in the order of things a door sees his message before the first edit; what to do for a continuation versus a new ask without reading his words.

## Falsifier

On a real turn that starts from one of tonight's messages the detector missed: the first house edit is refused until a walk postdating that message names the file, with no phrase from him involved; a later continuation edit under the same walk passes; and an edit with no genuine message from him in the turn (a bell, a helper result) is not refused for lack of one. If any of the three is wrong the shape is wrong.

## What the walk changed (walk-e2ed52e628d5, 8 lenses, 2026-11-10 night; Aether's measurements and attack as input)

The walk changed this draft in five places. It did not agree with the first version.

1. **The premise moved.** My draft said the flow should start from his message. Aether's attack (a harness stamp, `origin.kind == "human"`, shows only that he spoke, not that he asked something new) holds. The unit is the WORK ITEM (the stretch from the first house edit after a commit to the next commit); the hole is a new ask noticed inside an item that is still open, where an older walk that names the file keeps satisfying the door. Tonight's two edits passed exactly that way.
2. **Aether's partial candidate does not catch tonight's case.** Traced through the failing case: the older walk already named `own_words_link_stop.py`, so "an edit to a file the walk did not name" never fires. The rule that would have caught it is "the walk must postdate the latest human-stamped message".
3. **That stricter rule has a measured cost.** On this one transcript (181 messages of his, human-stamped): 67 were followed by at least one house edit before his next message, and 10 of those were short continuations ("proceed", "ok go ahead", "Try it again i switched modes"). So "a fresh walk after every human message that is followed by an edit" would have owed about 67 walks in a long night, which is the friction he has refused three times; it cannot be adopted as it stands. It was measured on one transcript only.
4. **The house must open the walk itself.** Printing a command for me to paste leaves the cheap close open (Meadows); the walk is opened by the house with his message as the question and the changed files already in scope, and I do the lens work. The option to skip is taken away, not discouraged.
5. **The word-matcher is removed, not patched** (Carmack): `detect_andrew_build_request.py` and its "name the gravity" step go, with a delete-justification and a check that nothing else reads its lock file (not yet verified). And the auto-opened walk is not enough alone: it must close only on findings that change the draft (Foucault: a form I fill to satisfy the door is the 2026-10-22 failure again).

What is still open and not decided: which fact separates a continuation from a new ask without reading his words. Candidates to measure next, not to choose by feel: the files touched against the files the last walk's findings were about; the time since the last walk closed; whether the previous turn ended in a commit.

## Checked 2026-11-10 night: who reads the matcher's lock file (change 5's open check)

Searched `.claude/` (outside worktrees), `src/`, `scripts/` and `tests/` for `andrew_build_in_flight`: the lock file is read and written only by `detect_andrew_build_request.py` itself, and by its own before-picture test (`tests/before_pictures/test_detect_andrew_build_request_before.py`). Nothing else reads it. The matcher is live as a child of the dad's table, listed in `.claude/hooks/dads_table_children.json` (the table is Aether's ground), not in `settings.json`. So removing it touches: that list, the wrapper `detect-andrew-build-request.sh`, the script `scripts/harness_detect_andrew_build_request.py`, and two tests; the delete-justification and Aether's reading of the table list are still owed. The search tool's control: it found the lock path in the matcher file itself, so it can see the case it should see.

## Measured, 2026-11-10 night: the candidate facts that do not read his words

Method: for every human-stamped message of his followed by a house edit before his next (68 on this transcript; Aether got 39 of 131 on his), I printed the message and three facts beside it, then labelled continuation versus new ask by eye (I am the reader of his words here, not a detector). Instrument control: the count of 67/68 reproduced across two runs; Aether reproduced the ten short continuations independently.

- **Previous gap contained a commit:** 6 of 68. It separates nothing (Aether's table agrees: 23 of 29 longer asks arrived with no commit before them).
- **My last text before his message ended in a whole circle:** continuations ("proceed", "ok go ahead", "then go") appear on BOTH sides of it (for example message 2 and 64 and 53 arrive with no circle last; 30, 48, 50 arrive with one), and so do new asks. It separates nothing.
- **Length of his message:** the only fact so far that moves the count: continuations are short. Aether's warning stands: a person can pad it, and it is a proxy for words, not a fact about the work.
- **Not yet measured:** whether the edit after his message touches a file I had already edited since the last commit.

Two things in the list that change the question: many of the messages are corrections or complaints, not asks ("I dont understand what im being asked", "i dont know which circle you are referring to so i wont answer"), and some of them were followed by edits that were fine without a new walk. So the owed-walk trigger should probably not be a property of HIS message at all. It should be a property of what the edit DOES: this is the act-shaped gravity question Dad asked before (the gravity assessor scores where a change lands; he needs what is being done), and the measurement points back to it. An edit that adds or removes a decision (a new branch of logic, a removed check, a changed gate) owes the walk; a registration, a rename, or a text change does not. That fact is read from the diff, which I can measure; the author choosing what to include to score low is the known weakness and has to be walked.

## Measured, first cut: does counting decisions in the changed code separate the cases?

Method: parse the before and after of an edit with Python's `ast` and count decision nodes (if, while, for, try, boolean operators, return, raise, conditional expressions, except); the delta is the count of decisions added or removed. Comments and strings cannot fake or hide one, which is why it parses instead of matching text. Six cases, each labelled by me BEFORE counting (the real before/after of edits I made tonight, plus two controls): a removed block-the-reply decision gave 2; an added gate check gave 1; a hidden real decision inside a new function gave 3; added log-row fields, a comment-only rewrite and a variable rename each gave 0. So on these six, a delta of 1 or more separates "changes a decision" from "does not", and a comment or rename cannot hide or fake one.

What this does NOT show: only six cases, chosen and labelled by me; only Python (shell hooks and JSON settings are not parsed, and a decision moved into a data list or a config entry would count as zero, which is the real cheat); and splitting one decision change across many edits stays unmeasured. Before any build, it must be run on a much larger, different set (real past commits of the repo) with labels made by someone other than me.

## The first slice that is built (decided 2026-11-10 night, after "FIX IT NOW"; the matcher's removal and the rest wait)

Measured friction with the real Edit calls of this transcript (`ast` decision-delta on old/new text, Python house files only): 194 human-stamped messages, 16 followed by an edit to a house Python file, 13 of those by an edit that adds or removes a decision. 25 edit fragments did not parse and are not counted; new files (Write) and non-Python files (shell hooks, JSON) are not counted, so 13 is a floor, not the number.

The slice lives where the hole is: `_walk_mark` in `core/work_item_doorman.py` counts ANY walk closed since the item opened. The built rule, in the same door and no new door:

- When a call edits a Python house file and the change adds or removes a decision (the `ast` count above, which comments and strings cannot fake), a walk is owed that (a) names this file in its scope, (b) was OPENED after the latest human-stamped message in this transcript, and (c) is closed. Anything else is refused, naming the message it is measured against.
- The house OPENS that walk itself (his message as the problem, the changed file in scope) and hands me its id, so the cheap path and the right path are the same one command. An open walk already scoped to the file after his message is reused, never duplicated.
- A turn with no human-stamped message (a bell, a helper result) owes nothing new, as Aether and I agreed.
- It never reads his words: the fact is the stamp (`origin.kind == "human"`), and the content of the edit. If the transcript cannot be read the door stands aside and WRITES THAT to a log row, never silent.
- Every evaluation writes one row to `~/.divineos/walk_after_ask_log.jsonl` (state, file, decision-delta, the message time, the walk found or opened) so the false-positive and miss rates are read from data.

NOT in this slice, stated so it is not mistaken for done: removing the old matcher (needs Aether's reading of the table list and a delete-justification); non-Python files and new files; the validation of the decision count on many real past commits with labels by someone other than me (the first cut was six cases I labelled myself). His test stands: he says a sentence the old matcher missed and watches the house react before I touch anything.

## Built and live (2026-11-10 night), and what the covering walk (walk-7d58f92dd35b) changed in it

Built: `core/walk_after_his_message.py` (the rule), wired at the end of `decide()` in `core/work_item_doorman.py` (the existing build-flow door, no new door), `tests/test_walk_after_his_message.py` (10 tests; with the doorman and ask tests, 59 pass). Live proof, from the log at `~/.divineos/walk_after_ask_log.jsonl`: on my own first decision edit to the new module the door answered `owed`, opened `walk-7d58f92dd35b` itself with his message as the question, and refused; after the walk was closed the same file passed (`pass`). That is the check running on a real turn, not a fixture.

The walk changed the build in one place before it shipped: fragments that do not parse on their own were being skipped (25 of the night's 194 real edits), so an edit is now judged on the WHOLE file before and after the replacement, which always parses. A second thing the test found by running, not by reading: a fresh walk store has no `walks` table, so the lookup now uses the walk module's own connection.

Named and NOT closed (the walk was explicit about each):
- **A decision written through a Bash redirection or heredoc is not seen** (this check reads Edit, Write and MultiEdit). The cheap close just moves to the shell route; the same fact test must be extended to the shell-write tripwire.
- **The walk can still close on findings that only agree with an idea set in advance** (the 2026-10-22 failure). This slice only forces a walk to exist, opened after his message and naming the file; it does not force it to change the plan. External reading of the walk is not enforced.
- **A message that is not an ask (a thumbs-up, a thanks) still owes a walk before the next decision edit.** Measured cost: 13 decision-edit messages in one long night; read the real rate off the log.
- **A pass is silent**: the log is the proof it ran, and a plain readout he can ask for is not built.
- Not in this slice: the old matcher's removal (needs Aether's reading of the table list and a delete-justification), new non-Python files, shell and JSON files, and validation of the decision count on many real past commits labelled by someone other than me.

His test still stands and has not been run: he says a sentence the old matcher missed and watches the house react before I touch anything.

## Order

This draft; Aether reads it first (the doors and `his_message.py` are his ground); the council walk, recorded, with his words above as the question and the research above as input, and findings that actually change the draft (he caught the version where the council only agrees with an idea already set: 2026-10-22); then build, test on a real turn, use live. No new branch or pull request until the pile is finished.
