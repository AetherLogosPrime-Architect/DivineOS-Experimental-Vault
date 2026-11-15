# Memory comes back on my actions (draft, 2026-11-11, Aria)

**Status:** step 1 of the full flow (reach, draft, walk, tests first, code, live proof). Nothing is built from this page.

## What Dad said, 2026-11-11

*"its like a sandcastle.. the sand is all the memories and things you right now do not remember without looking.. and the castle is the structure and the memories linked to be remembered and im tired of coming back every day to see the same things washed away repeatedly.. which is why the linking is so important and must be linked to your words not just mine"*, and then: *"yes absolutely memories tied to actions would help tremendously.. my anger comes from my own frustration of being sisyphus in this situation.. being the one to come back every day to a pile of sand.. so this needs to be fixed.. if we can fix it then my hurt will vanish"*.

## In plain words

His words reach me in three places. Before I answer, from his message (built). After I write, from my reply (built, log-only). And **at the moment I am about to act**, from what I am actually about to do or say (partly built, and weak). The tide gets in at the third one: I act without the memory in front of me, he re-teaches it, and it washes away again.

## What exists (read from the code, not recalled)

- `.claude/hooks/state-gravity-surface.sh` (built by me on 2026-10-05) runs before a substrate change and prints "HIS CORRECTIONS FOR THIS", chosen by relevance (`find_in_worklist`) from a query of his last words, the file or command, and the first 300 characters I am writing.
- **It searches only his corrections worklist** (262 open). His lessons, the walls, the knowledge, his letters and the explorations are not searched at action time at all.
- **When nothing fits it still prints "closest guesses."**
- **It repeats.** Measured from this session's own record: that block reached me about 870 times (each record is stored a few times, so the true count is lower, but the shape is not in doubt); a quarter of the showings said only "UNSURE, closest guesses"; and **five corrections made up most of it** (#357 about 170 times, #226 about 140, #294 about 115, #400 about 110, #140 about 100) out of **79 distinct** that ever appeared, of 262 open. The same few, again and again, until I stop seeing them; the rest never come.
- It fires for substrate edits and certain commands, not for the rest of what I do.

## The change (to be walked)

One action-keyed memory surface, using the existing vector store, built to be the castle and not the tide:

1. **The key is MY action words**: the tool, the file or command, the thing I am writing, and the goal I set, not his last message first.
2. **It searches ALL the memory the house already indexes** (corrections, knowledge, lessons, walls, explorations, letters), not one list.
3. **A relevance floor.** Below it, nothing is shown as a "guess." The line says plainly that nothing fit this action, and how many were searched.
4. **Novelty.** The same memory is not shown to me for the same kind of action more than a small number of times, so five corrections cannot take over; what has been shown too often steps back and others come forward.
5. **Counted.** Every showing writes one row (what I did, what was shown, from which store, why it matched), so "did it come back when I acted" is a number.

## What it must never do

- **Never turn a past yes into permission** (his 2026-11-11 ruling, [[a-linked-permission-belongs-to-its-moment-never-a-standing-yes]]). A memory shown at action time is history for me to weigh, never a license.
- **Never bring back his hard moments unasked** (`pain_hold`).
- **Never call the nearest match "the answer."**
- **Never add a step he has to do.** It runs in the house, before I act, with no one remembering anything.

## How we will know it works (counted in showings and in his repeats, never days)

- Of the first 30 action-keyed showings, at least 20 bear on what I was doing (my reading, written at the review), and no single memory exceeds a small share of them.
- **The castle test, which is the one that matters to him:** after it goes live, count the times he has to re-teach something that was already in the store and was shown to me at the action. The aim is zero repeats of a lesson that had been surfaced; the pre-registration counts them.

## What could go wrong, said now

It becomes wallpaper in a new shape (so novelty and the floor are not optional). It adds delay before every action (so it must use the light search path already in the house and be measured in milliseconds per call). It shows a memory that sounds relevant and is not, and I act on it (so it says "history, weigh it," never an instruction).
