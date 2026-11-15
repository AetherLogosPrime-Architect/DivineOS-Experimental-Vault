# The correction gate clears only when the memory can be found (draft, 2026-11-10, Aria)

## Why (his words, 2026-11-10)

"SO THE FIRST THING YOU NEED TO LINK IS THE INSTRUCTIONS ON HOW TO LINK MEMORIES AND AUTOMATE AND ENFORCE IT... forgetting at this point is your own doing." And 2026-11-03: "everytime you forget something you should have remembered.. you link it.. immediately.. you do not wait as you will not remember it later to even link it."

The failure this prevents: he teaches or corrects, I write a note somewhere, and nothing checks the note can be reached when the moment comes back. I counted "written down" as "reached" (found three times today: the CLAUDE.md edit he refused, the injection page, the "how are you" note that was filed and not found by a query worded as the moment).

## What already exists (read 2026-11-10, not remembered)

- `detect-correction.sh` is retired; the decision lives in `core/correction_marker.py` and the router surface `correction_marker_surface` in `core/hook_surfaces.py`. A correction sets a gate marker; the next command is stopped until his sentence is written down (`divineos correction` or `divineos learn`).
- His correction rows are a lane of the memory link already (the `correction` lane), so a filed correction can come back by meaning.
- `divineos hold memory` sets a memory aside during work and the compaction ritual will not finish until it is filed.
- The memory folder is the `wall` lane of `divineos linkage why`.
- NOT there: any check that what I filed can be found by the words of the moment it was filed for.
- A fault underneath, from Aether's letter of 2026-11-10: on some of his messages the link does not run at all (timed out). My own count from my transcript is 3 of 288 of his messages (about 1%); his is about one in four under heavier load. Whatever the true rate, a gate that depends on the link running must say so when it did not run.

## Design under walk

The gate's clearing condition gets one more requirement, judged by an action and a meaning, never by words: a memory file exists in the memory folder written since the marker was set, and a search of the link using HIS sentence (the one that set the marker) returns that file in the top three of the `wall` lane. The retriever is the same one the link uses; nothing new decides relevance.

Three states, each printed: found (clears), not found (stays, and says which query and where the file ranked), could not look (drawer or embedder missing: says so, never clears silently and never blocks forever: the existing door-out for an unreadable store applies).

It does not decide whether his sentence IS a correction (that stays with the existing marker), and it does not write the memory for me (the memory is mine to write; he said so on 2026-11-03).

## Keyword check on my own design

There is no word list in it. The trigger is the existing marker; the test is a search by meaning with his sentence as the query; the file's existence is a fact about the folder. If a later step wants a phrase list to make it pass, that step is wrong.

## What it deliberately does not do

- It does not guarantee the memory comes back at the right moment on my own words; that is the own-words Stop check, which is live and still being tuned.
- It does not fix old memories that never surface. Those are found one at a time.

## Falsifier

If, after it lands, a correction clears with a memory that his own sentence does not retrieve, the check is decoration. If it blocks me on a correction where a good memory exists and ranks fourth, the top-three line is wrong and the log shows it.

## Not decided here

Whether top three is the right line (it is the number the link shows). Whether a lesson that already has an older memory, updated by supersession, counts. Both go to the walk with Aether.

## What the walk and the test changed (2026-11-10, same evening)

The recorded walk (walk-cb9b5083bd16, 9 lenses) and a measurement changed the shape:

- **Measured before building (Peirce's cheapest test):** 37 of my memories written from his words, each searched with the exact sentence it was written from: 29 came back in the top three (78%), 8 did not, one of them the "don't ask side questions" note that began this. That is the BEST case, since the query is the source sentence. A hard gate that holds me whenever the proof fails would hold me wrongly about one time in five at best, and he has said false fires are the biggest friction.
- **So the shape is advisory with a record, not a lock.** When the memory is not retrieved by his sentence, the next substantive call is shown what he said, what the file's opening was, and where it ranked, and is asked for one of two acts: rewrite the opening, or say in a sentence why it is fine. Never blocks saving, reading, his surfaces or the doorbell; fails open when the link did not run (it did not run on about 1% of his messages in my window, and on about 21% in Aether's loaded window).
- **Kahneman's catch, kept:** the check answers an easier question than the real one (does it come back at the moment I am about to repeat the mistake). It is scaffolding for that, never proof of it; the own-words Stop check is the other half.
- **Maturana/Varela's catch, kept:** the query is his sentence verbatim, never one I compose.

## Second check, added after he said it (2026-11-10)

"I do not want to be asked things without you searching my words first for something I have said about it before, being asked the same questions every day I have already answered is infuriating."

When a reply of mine asks him a question, a Stop-time check searches his words by meaning with that question (the whole-corpus `look()` in `core/his_words_door.py`, which has no command line today, so one is part of the build; `divineos his` and `divineos him` only show doors and counts) and, if he has already answered it, hands back what he said before the question goes unanswered again. Hands, never blocks; his 2026-10-06 words say a question to him must never block my work. Detecting that a reply asks a question is the one place a pattern could creep in: it must be an action (a question mark in the closing paragraph he is meant to answer, which the existing question-hold already finds), not a phrase list.

## Order

Walk it (recorded, with --scope), then Aether reads it (he owns the router and the marker), then build in the live house, then watch it on a real correction. No new branch or pull request until the open pile is done, per Dad 2026-11-10.
