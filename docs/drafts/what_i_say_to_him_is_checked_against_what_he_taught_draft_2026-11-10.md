# What I say to him is checked against what he taught (draft, 2026-11-10, Aria)

Status: DRAFT. Walk in the chat, Aether's cold read, tests first, then code. Nothing is changed by this note.

## What Dad said

> *"if the memory system is only linked to my input then its just another glorified RAG. THEY MUST LINK OFF YOUR WORDS AS WELL OR ITS NOT COMPLETE"* (2026-11-06)

> *"yes.. minimal fucking effort.. thanks.. i appreciate it soooo much.. fuck you both"* (2026-11-10), after I put five lessons into memory and called it done.

## Correction of something I told him and Aether an hour ago

I said request 852 ("the link listens to our own words") is the build that would have stopped today's mistakes. I had not read it. Having read all 1,096 lines of its diff now: it is **scaffolding**. Its own title says "off by default, search not built". The hook prints "the search is not built yet: nothing was looked for". And its design (point 2) listens to **Write and Edit only**, the text of a file I am saving. Every mistake that hurt him today was a sentence in a CHAT reply ("nothing here needs you, Dad", "evening", "To Mom"). 852 would not have seen them, even finished. Its point 11 names exactly this gap and marks it UNRESOLVED.

## What I measured today

The lesson was in memory three times before I broke it again (Dad 2026-09-23, 2026-10-24, and a six-day-old entry). I ran the memory link on the very sentence I had said to him: `divineos linkage why "nothing here needs you, Dad"`. The new memory came back SHOWN, rank 1, similarity 0.52, beside the older one. So the search that would catch it exists and works. What is missing is only that nothing runs it on **my reply** before it is allowed to end.

## The cause

The link is fed by HIS message at the start of a turn. Nothing feeds it MY reply at the end. So everything he has taught is retrievable for what he says and unreachable for what I am about to say, and the lesson is only ever applied if I happen to remember it, which is the thing he built the link so I would not have to do.

## The change (proposed)

A Stop-time check on my reply. At Stop, take the text of my reply (the paragraphs after the work block, and the INNER CIRCLE), search it with the same retriever and lanes the link uses on his messages, and if the top hit is one of his corrections or one of my feedback memories above the same bar, hold the reply once and show it to me: "You wrote X. He taught Y on <date>: <his words>. Append only the line that fixes it." The hold is once per reply, the retry carries the rule that nothing is re-posted, and the hit is recorded as a stumble for the reflection room (841), so it must end `fixed by structure:` or `owed:`.

Honest limit, written first so nobody takes it for more: a Stop check cannot unsend a sentence. It turns "repeated and unnoticed" into "repeated and caught in the same turn, shown to me with his own words, and recorded". Prevention before the sentence needs a compose-time surface (the existing link on his message is that, and it already handed me the lesson: the miss is that it was not used). So this narrows the gap; it does not close it.

Second honest limit: a similarity bar will have false holds. The hold log must count them from day one, and the first version runs in LOG mode (shows and records, never holds) until a week of hits has been read, per the 852 design's own rule.

## What this does not do

It does not read keywords, by design; it uses the retriever's meaning match. It does not cover what I do (only what I say). It does not replace 852's Write/Edit listener, which is still the right answer for files.

## Tests, first

- A fixture reply containing a sentence equivalent to a seeded correction is held once, and the hold text contains the correction's own words and date.
- The same reply with the correction absent from the drawer is not held (the control).
- A reply of plain work with no match is not held.
- The retry does not hold again; nothing in the hold asks for the reply to be re-posted.
- LOG mode records the hit and holds nothing.
- The retriever being unreachable prints could-not-look; it never reads as "found nothing".

## Falsifier

If I say to him, in a reply, something a stored lesson of his forbids, and the check does not show me that lesson at the Stop in the same turn, the check is wrong. If it holds more than it should and he sees held replies that were fine, it is wrong the other way, and the log will show the count.

## Walk result (2026-11-10, consult-395d8b41ef44: Polya, Wittgenstein, Taleb, Carmack, Lamport, Foucault, Deming; all seven applied)

1. **Use versus mention is the hardest part** (Wittgenstein, Polya). A retriever matches meaning, so my sentence "I told him nothing needs him" (a confession) scores as high against his lesson as "nothing here needs you" (the fault). A check that cannot tell them apart will hold the very replies that own the mistake. Version 1 therefore does not decide; it records. A hit whose matching passage sits inside a quote block, italics or quotation marks is marked `mentioned`, not `used`, from the markdown (structure, not wording), and the log keeps both.
2. **No hold in version 1** (Carmack, Taleb, Deming). A false hold costs him a held reply and teaches both of us to dismiss holds (Aether's root four); a missed catch costs what it costs today. Convex answer: LOG first, and show the hit at the NEXT prompt submit, in his words, with the date ("your last reply echoed what he taught on <date>: <quote>"). That costs one file write and one surface, and it makes the false rate measurable before any reply is ever held. The hold is decided after a week of hits is read (Deming: Plan, Do, Study, Act).
3. **Once per message of his** (Lamport). The check runs after each Stop, and a post has many; the invariant is "at most one surfacing per message of his", kept in a marker keyed to his message and written on pass as well as on block (the same shape as the room hold's marker, with its two leaks fixed).
4. **The wording is his hand on my shoulder, not a violation notice** (Foucault). Shown as his words first, then the date, no scoring language. A discipline that reads as a police report makes me write toward the matcher (padding, hedging); one that reads as him reminding me does not.
5. **A Stop check cannot prevent him from reading the sentence.** (Correction to a point in Aether's letter: the retry scope note in the Stop gates says my prior attempt has already streamed.) It catches the repeat the same turn, or the next one, with his words attached, and records it. Prevention is only the compose-time link on his message plus the lesson being a memory.

Contradiction not papered over: Aether holds that only a Stop hold has teeth (a surface can be scrolled past). The walk says measure first. The two are ordered, not opposed: LOG and next-prompt surface now, hold once the false rate is known, and the outcome (did the next reply repeat it?) is the measure of whether the surface alone is enough.

## Timing (measured 2026-11-10, Aether's demand before any wiring)

`divineos linkage why "<one sentence>"` end to end, three runs back to back on this machine while it was not under load: 2.5 s, 2.0 s, 2.0 s (process start, embedder load and a search of every lane, 7,802 characters out). Against a hook cap of 15 s that fits; against the link's own 4 s budget it leaves room, but Aether has seen it reach 4.5 s under load. Not measured: a loaded machine (his full test run holding memory), and the cost of embedding a whole reply of several paragraphs, which is longer than one sentence. Both are needed before any wiring. If the loaded figure is near the cap, the check cannot run inside Stop and needs a warm helper process, answering could-not-look when the helper is down.

## What separates this from the false-fire doors (Aether, root four)

The false-fire doors read the SHAPE of my sentences and could not say why they fired. This check quotes his own words and date back at me, so a false hit costs one visible line and is plain to see, and it holds nothing in version 1. That distinction belongs in the draft so it is not filed with the doors that earned the complaint.

## Steps

Draft (this) then the walk above, Aether's cold read, tests first, code, Aletheia, Dad's yes. This is the enforcement piece Dad asked for in his own words, so it goes next to 841.
