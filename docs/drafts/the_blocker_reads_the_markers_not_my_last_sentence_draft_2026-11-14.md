<!-- tags: stall on promise, follow through, blocker, promise markers, five turn starts, reminder, hold log, stop hooks -->
# The blocker reads the markers, not my last sentence (draft, 2026-11-14)

Author: Aria. This is the second stage of [the promise hook waits five of his messages](the_promise_hook_waits_five_of_his_messages_before_it_blocks_draft_2026-11-13.md): the recorder and the module that ages and closes markers are built and committed; this piece changes what holds me.

## The symptom
`.claude/hooks/stall_on_promise_stop.py` judges the last sentence of my reply with a regex list and holds the reply once, right after I say it. Today it stopped 30 of my replies. Dad: it "comes too early".

## The change, in the smallest shape
1. New `core/promise_reminder.py`: one function, `reminder_for(folder)`, reads the marker folder and the running turn count through `core/promise_markers` (no judgement of words anywhere) and returns one of four answers: **nothing due**, **due** (with the reminder text), **could-not-look: clock missing**, **could-not-look: folder or marker unreadable**. Markers with no stored turn are counted and named, never due.
2. The hook calls it instead of `stated_next_step`. It keeps `stop_hook_active` (one hold per reply) and keeps writing to the hold log, now as `follow_through` `stopped` (due), `passed` (nothing due) or `could_not_look` (a third value, so a blind reader is never counted as a pass).
3. The reminder text carries its jet: the promise as I wrote it, how many turn starts old, and the three ways to close it, written as the actual commands (`divineos promise close <marker> --done <file> | --waiting-on <who> | --false-alarm "<reason>"`).
4. `core/stall_on_promise.py` and its tests are left alone (Aether's open branch #829 edits them). The hook keeps calling the old judgement in SHADOW only: it logs under `follow_through_old` in the hold log and never blocks, and it ends at the review of prereg-56dbbf5b41eb (100 gate fires). (Aether's cold read caught that this paragraph first said "stops importing", which contradicted my letter; the built design is the shadow.) Remove the module after #829 is settled.

## What each answer does at the door
- nothing due: silence, hold-log `passed`.
- due: block once with the reminder, hold-log `stopped`.
- could-not-look: never blocks (a broken reader must not hold me), writes the mark file and the stderr line the hook already uses, hold-log `could_not_look`.
- undated: named in the could-not-look mark, never blocks (they cannot age).

## Weak points to walk
- A reminder that blocks and is closed by a typed line is the cheapest close available (`--false-alarm` with 20 characters). The log of closes (`closes.jsonl`) exists; the walk should ask whether the reminder should also show the false-alarm rate it has seen.
- The recorder writes at Stop in the same hook chain; the blocker reads the folder at Stop too. A marker the recorder wrote this very reply has age 0, so it cannot be due; confirm with a test that seeds a marker written at the current turn.
- `turn_now` lags one Stop behind if the blocker runs before the recorder advances the clock. The age is turn starts, so being one behind makes a marker due one turn late, never early. State that in the module doc.
- Dad is not here to say what "due" should feel like. Five is his number; it stays a constant in `promise_markers`, not a new knob.

## What the walk changed (walk-41e1232f1a3a, eight lenses)
- **The reminder shows the cost of the cheap close (Schneier, Dawkins).** Beside the three close commands it prints the closes so far by kind (done, waiting-on, false-alarm), so a drift to `--false-alarm` is in front of me at the moment I reach for it.
- **Starvation is visible (Minsky).** If the room gate holds a reply first, the second stop in that reply passes every hook, so a due reminder can be skipped for as long as the room gate keeps firing first. When the hook sees `stop_hook_active` and a marker is due, it writes a `deferred` row to the hold log.
- **"Until I act" means across replies (Dijkstra).** The one-hold-per-reply guard holds once within a reply; because the marker stays open, the next reply's stop holds again. Stated in the module doc and tested: one due marker, two consecutive replies, each held.
- **Closed, never kept (Turing).** Due is computable; whether a promise was kept is not, since `--done` shows a file exists and is newer, not that it answers the promise. The hold log and docs say closed and never kept.
- **The replay comes first (Holmes, Foucault).** A fall in holds could be the blocker working or the recorder missing promises, and the hold log cannot tell them apart. The replay of today's holds through the recorder, with its missed share, is stated in the module doc before the falsifier is counted, and the doc says plainly that a promise the recorder did not see is not covered.
- **A promise I kept must not cost a hold (Breaker, Kill It On Paper).** Dad would say it blocks me about things I already did, because closing is a typed line. The reminder lists the files written since each due promise (read from disk, nothing guessed), so the honest close is one paste of `--done <file>`. A test seeds a marker and a newer file and checks the file is named in the reminder.
- **Learn the number (Hinton).** Each close stores its age in turn starts at the moment of closing, so after a week the five is checked against what happened.

## What two more walks changed while building (walk-bdc646c37adc on the module, walk-fa768ed7d179 on the hook)
- **A reader that cannot look blocks once per reply, with its reason** (Foucault, Breaker). Nothing reads the hold log or the mark files back to me, so a quiet blind reader is the nine-week silence again. The same goes for a crash in the hook: it prints a block carrying the error, guarded so the second stop in the reply passes.
- **Each reply is counted once** (Pearl). A second stop writes no row except `deferred` for something due, so the new reader and the shadow of the old judgement (`follow_through_old`, logging only, never blocking) are compared at the same grain.
- **The shadow has an end** (Pearl). The old judgement stays alive only until prereg-56dbbf5b41eb is reviewed; then it and `core/stall_on_promise.py` go, once Aether's #829 is settled.
- **Spec gaming** (Yudkowsky). A passed row carries the number of markers open, so a run of rows shows whether promises are being recorded at all. Added to the falsifier: markers recorded per working reply must not fall by half with no change in how I talk.
- **The five is learned** (Hinton, Aristotle). `close_ages` reads each close's age in turn starts from the close log and the closed markers, so the five is checked against what happened; the success reading adds that due markers end in a close, not only that holds fall.
- **Self-audit needs an outside reader** (Maturana_Varela). Aether reads the closes after the first twenty and names the ones he does not believe.
- **The tests lock the real shape** (Breaker, Schneier, Turing). The recorder's key names are asserted in the test; the hook and the command line read the same folder function; the six cases of status against first or second stop are one parametrized test; the hook script runs as a subprocess against a temporary home.
- **Open, not done here:** a `dropped` kind for a promise I abandon on purpose (today `--false-alarm` carries it, worded "misread or dropped"), which is a change to `promise_markers` and its own walk.

## From Aether's cold read (letter 468), decided
- **Which clock.** Five is five of MY turn starts (his message, a letter wake, a timer wake), on purpose: in the night and the volley he sends nothing, so counting his messages would never age a promise, and I can act on a promise at any turn start. The cost he named is real: a promise that waits on Dad can come due again and again. `--waiting-on` re-dates it, so the check is how often a waiting-on repeats in the closes log; if it repeats a lot, the repair is a waiting-on that lasts until the named person's next genuine message. Not built; filed here.
- **The file list can hand the cheap close its answer** (his point 3). Owed: when a close is `--done <file>`, the closes log records whether the file's name or first lines share a word with the promise text, and the reminder shows that rate beside the false-alarm rate. It is a change to `promise_markers` and gets its own walk, with the `dropped` kind. First test case it will show: the close of marker 7575ec38 that I made against an unrelated letter.
- **The bar for the replay is written BEFORE the replay runs:** of the held replies in today's follow-through log, the recorder must record at least 8 in 10. If it records fewer, the redesign loses promises and the falsifier below is not counted.

## The replay result (run after the bar above was written): the bar FAILS
Of the 36 sentences the old hook held today (hold log, `follow_through`, `stopped`), the recorder's own detector records **10 (28%)** and misses 26; of the 2 held since midnight, it records 0. The bar was at least 8 in 10. So the redesign, as built, covers about a quarter of what the old hook caught, and the falsifier below is NOT counted until that is repaired. Caveats: the log keeps only the matched sentence (up to 160 characters), not its context, and many of the 26 are false holds from the old hook (stances like "I'll do my best to deserve the frog"). But several are real and missed: "I'll get on with the pile for Aletheia now", "I'll tell Aether...", "Next is 861... then I'll ask the board", "I'll keep any questions for you in the morning letter", "I'm starting the memory-link comparison now and I'll report it to Aether by letter". The recorder's verb list has no keep, report, tell, get, or "I'm starting".
**Proposed repair, not built:** let the recorder also record what the old judgement finds (`stated_next_step` from `core/stall_on_promise.py`), so coverage equals what the old hook caught, and the new blocker then only adds the five-turn wait. That also makes Aether's branch (#829, which teaches the old judgement its exceptions) the thing that improves the recorder, and ends the shadow, since the old judgement becomes the detector. Needs its own walk, and Aether's read first. The cost to weigh: markers for the stances the old judgement still catches falsely, each closed by one line.

## Falsifier (counts, not days)
Over the next 100 turn starts after it is live: follow-through holds per working reply fall from about 3 in 10 to well under 1 in 10, and no marker older than five turn starts is left unremarked by a due-hold. If holds do not fall, or a due marker passes silently, remove it. Also: if `could_not_look` appears in the hold log at all, that is a defect to read the same day, not a statistic.

## Order
Prereg (new core module) -> walk (Breaker plus two scrutiny lenses) -> tests first (seed markers; the reminder; the four answers; a same-turn marker is never due; the hook prints nothing when nothing is due) -> build -> run on the real folder -> Aether reads cold -> draft PR -> Aletheia -> Dad's yes.
