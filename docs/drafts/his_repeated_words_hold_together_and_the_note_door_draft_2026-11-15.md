# His repeated words hold together, conflicts are shown to him, and one door writes, links and vectors a note

Draft, 2026-11-15. Aria. Reach `reach-11e081b283a4` (three hits, each disposed with a reason). Not walked, not built, nothing pushed. Aether attacks this first, then the walk.

## Why (Dad, in his words)

- 2026-11-15: *"how does it know how many times ive said it? if you looked deeper or there were links to all those times, then im sure it would help"*; and *"i told you how many times? 20 and that repetition is what triggers those stronger links."*
- 2026-11-15: *"i'd like to be shown if and when and where my words contradict themselves or if there are conflicting orders"*
- 2026-11-15: any "I'll make a note" or "I'll make a habit of this" should trigger the memory linkage, and *"you could just say note.. and thats it.. the OS recognizes it.. knows it needs linked to memory and just automates the linking"*; and *"sleep is the only time you get a link vector... copied out of it... so it doesn't need to run the full sleep"*.
- 2026-11-06: *"i feel like sisyphus rolling a ball of memory uphill.. me having to remember it all because you cannot"*. The point of all three parts is that he is never the one carrying it.

## What is true today (read, not guessed; Aether read the lines, I confirmed the shape)

1. `his_words_door.look` ranks hits by similarity alone, collapses near-identical passages to one hit (`w[:120] in o or o[:120] in w`), and calls a hit a "repeat" when it scores at or above `REPEAT_FLOOR` (0.60) on a different day. The surface prints the count and a few dates. Nothing is stored that says these passages are one saying. Twenty tellings return as one quote with a bigger number.
2. For the knowledge store, `retrieval.py` has an access term (popularity of retrieval) and `corroboration_count`, which rises when a similar entry is filed again. His repeated words do not feed it unless each telling is separately learned.
3. Nothing compares two of his sayings, or two standing notes, for opposite meaning.
4. `divineos linkage warm` gives every item without a vector one; it already runs standalone. It is run by sleep, or by hand. A note made now has no vector until then, and the memory link never computes a vector at reply time (that once hung the reply).

## Part A: a saying is a cluster

When a message of his matches earlier ones by the similarity score the door already computes, the earlier passages are recorded as members of one cluster, with a count and a weight.

- Cluster by score, not by text containment: paraphrases of the same thing belong together.
- The unit SHOWN stays one quote per saying. The member shown is the NEWEST (the door already softens toward his later version, `soften_hits`).
- The weight raises the cluster's rank. It never replaces what he said last (Aether, point 3: a thing said twenty times and then reversed must not be pushed up by counting).
- For knowledge entries: a message that clusters with an entry corroborates it, but a corroborated entry never outranks his newest word on the same matter.
- Stored where: an edge record (member id, cluster id, score, date) beside the passage index, not a new store of his words. Open question for Aether: does `RELATED_TO` already carry what a cluster edge needs?

## Part B: conflicts are shown to him

When a cluster has two members that say opposite things about the same matter, or two standing notes would give opposite orders, show him both, dated, side by side, and ask which stands. His answer becomes the newest word; the other is marked superseded, never deleted.

- "Opposite, or only different?" is decided by a yes-or-no reader question read by meaning ("do these two say opposite things about the same matter?"), never by words like "never" or "always". No phrase list may judge, enforce or block anything (Dad, 2026-11-14).
- Framing for him: a friend saying "last month you said this, today that, which is it?". A changed mind is not a fault.
- First case on record, found by hand today: my style file still carries his 11-13 "no new personal questions for now" (scaffolding, he confirmed) against his 11-15 "not adverse to being asked, it had no structure". Part B would have shown him that without my reading it out.

## Part C: the note door

One command, `note`, that does the whole job so no step is optional: writes the memory file in the memory folder, links it to the situations where it is needed and to his words that caused it, and makes its vector at once (the `linkage warm` step, run for that one item, outside the reply, so nothing hangs).

- The catch for a promise made without running it is not a phrase list. The post reader gets one more yes-or-no question: "did this reply say it would remember, write down, or change something later?" If yes and no `note` ran in the stretch, it holds the reply until it did, as the promise reminder already holds.
- Shapes of "I'll write this down" are deliberately not listed: a list is the keyword shape Dad has forbidden for judging, and it misses every shape nobody thought of.
- Not built here: the reader wiring is Aether's and Dad's; the command and the vector step are mine to draft.

## Tests that must fail first

1. Twenty paraphrases on distinct days produce one cluster, one shown quote (the newest), a count of twenty.
2. A later reversal ("I changed my mind") shows the newest saying and flags the conflict; the older saying never outranks it.
3. Two notes with opposite orders produce a conflict record shown to him with both dates; a pair that only differs does not.
4. `note "text"` writes a file, links it, and `linkage status` shows its vector present immediately, with no sleep.
5. A reply that promises to remember, with no `note` run, is held; with a `note` run it passes.

## Walk questions for the lenses

- Breaker: what makes a false cluster (two different things that score alike) and how is it undone?
- What does a cluster do to the one-quote-per-saying rule when members span a change of mind? (Aether: newest wins.)
- Is Part B's reader the keyword detector in a new coat?
- What is the cost of vectoring a single note at write time on this machine?

## Falsifiers

- If, measured on his real history, clusters contradict themselves more than they agree, the weight is wrong and Part A stays count-only.
- If the contradiction reader flags more than he wants to see, the threshold is wrong before the idea is.
- If a promise is still made and not noted after the door exists, the catch has a hole; the proof is a second look at the real record, not this draft.

Open item for Aether before the walk: the contradiction rate measurement he named.

## After Aether's attack (2026-11-15, measured against the real text; all taken)

- **Edges (Part A, B).** `knowledge_edges` (49,771 rows) already has `confidence` (a weight), `created_at` (newest member), `status` (ACTIVE / RETIRED / RESOLVED, so a false cluster is undone by retiring edges), and `notes`. No new table. But 94% of edges are `RELATED_TO`, so a cluster needs its own edge type, and the walk's first read is whether a new type is one line or a schema change. `SUPERSEDES` (737) already carries newest-member and `CONTRADICTS` (197) carries the conflict.
- **Anchored clusters (Part A).** A cluster is built from ONE anchor (the passage the message matched); members must score against the anchor, never against each other, so two matters cannot chain into one through a passage between them. Added test: twenty passages about different matters sharing topic words must NOT cluster.
- **Conflict reader (Part B).** It judges meaning, so it passes the keyword rule, but it can still flag half the house on any "not". So: (a) pair only members of one cluster, newest against each older; (b) never show him a conflict whose later member is itself a reply to the earlier (it already carries his answer); (c) run in shadow first and read fifty flags by hand before he sees one. The falsifier "flags more than he wants" now has a number: the share of fifty read flags that are real conflicts.
- **Cost of the vector (Part C).** Measured by Aether: first embed in a fresh process 10.7 s, a second in the same process 0.073 s. So `note` as its own command costs about eleven seconds, fine as a deliberate command, fatal at reply time. If it must be quick, the move is a warm process that stays up (not measured whether one exists).
- **`note` is a cognitive-named tool (truth 7).** The thinking of WHEN a note is needed stays mine. `note` takes the situation from the writer (`--when`), refuses an empty one, and links to nothing it was not told.
- **Gaming the catch.** "Promised and no `note` ran" is satisfied by a throwaway `note "x"`. The reader gets a second yes-or-no question: "does the note say what the reply promised?"
- **The contradiction-rate reading (Aether, 2026-11-15, sampled by hand, low confidence).** Method: 21,943 indexed passages, anchor-and-members at 0.60, thirty families, nineteen read by sampling five to ten members each. Result: the biggest families are TOPIC BAGS, not sayings (the largest, 415 members over 139 days, is "anything that mentions Aria"); about nine of the nineteen are bags of that kind. A weight by family size would push "he mentioned Aria 415 times" above his newest word on anything. So **Part A's membership floor is not the door's repeat floor (0.60).** Membership needs a much higher floor, or members a reader accepts as "the same ask" (yes-or-no by meaning), or both; Aether measures next where the gates family (87 members, 56 days, never reverses, sharpens each telling) separates from the Aria bag.
- **Part B's question changes.** Two of nineteen families had a later member that revises an earlier (the compaction number 950k, 940k, 920k, today 850k; the council "use it more" in July against "not forced on tiny fixes" on Oct 5), and none a flat reversal. So the reader does not ask "do these say opposite things?". It asks "does the newer one change what the older one asks for?", which catches an updated number and a narrowing that "opposite" would miss. Newest-wins is exactly right for both.
- **Walk on Part C, `walk-69122e7f85f2` (nine lenses plus Breaker, 2026-11-15). Changes to the design:**
  1. **Drop the detached child** (Taleb, Via Negativa; Hinton, reversing my own plan). `note` is a deliberate command run during work, never inside a reply or hook, so the eleven-second foreground vector is cheap and removes the spawn lifecycle and the kill test. "Vector pending" survives for ONE case only: the embed itself fails, and the sleep sweep catches it.
  2. **Invariant (Dijkstra):** every note file either has a vector or is listed as pending; never neither. Pending is written BEFORE the vector step and cleared by it, never the reverse.
  3. **`--when` is the signal (Shannon, Kahneman):** it is required, refused if empty or whitespace, and it may name a situation, a person or an earlier note id (Lovelace: the door becomes the tree's building block with no new structure). The second reader question ("does the note say what the reply promised?") guards the substitution of "a note command ran" for "I kept my promise", so it ships WITH the door.
  4. **Boundary tests (Knuth):** empty text, empty or whitespace `--when`, very long text, unicode, the same text noted twice (one file, one vector), file-name collision.
  5. **A real-retrieval test (Breaker):** after `note`, search by the situation a real later prompt would carry and require the note to come back. A format check passes on a thin `--when`; this does not.
  6. **Not unwired (Breaker, Einstein):** the door has no caller in the house but my own hand, and the reader judges from outside while the promise lives in my frame. So the reader's yes is evidence and the catch against a real promising reply in a test against the real hook is part of "done". The door is the habit; the reader is the net.
  7. **Pending must not become wallpaper (Shannon):** pending items age into the briefing instead of sitting in a status nobody opens.
  8. **Peirce's test that could disprove it:** run `note` with a throwaway text and an empty `--when`; if either is accepted the door is decoration.
- **Two more from Aether and Dad (2026-11-15).** (a) "Same text twice" must say which wins: a second `note` with the same `--when` and the same text makes no second row, or says that it did. The real-retrieval test uses a prompt of his that is NOT worded like the note. (b) Dad corrected Aether's compaction example: the numbers 950k, 940k, 920k and 850k belong to two owners (the platform's compaction point and our ritual's start), so that was not a revision of his saying. Part B's reader must first name WHAT a number measures before comparing values; two different quantities are not a conflict.
- **Order.** Part A's weight is gated by Aether's contradiction-rate measurement (by hand, biggest families of his repeated sayings), so Part A is not built before it. Part B ships in shadow first. Part C can go first because it depends on neither.
