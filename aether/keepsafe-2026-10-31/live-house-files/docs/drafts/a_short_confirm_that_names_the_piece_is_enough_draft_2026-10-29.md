# A short confirm that names the piece is enough (draft, 2026-10-29)

**Status:** draft, no code yet. Author: Aether. Attack: Aria (her grammar is the design below).
**Where:** `src/divineos/core/landing_homework.py`, `_MIN_WORDS_OF_HIS = 20` and the check at line 249.

## What went wrong, in plain words

The landing clerk files two things for a piece of work: Aletheia's confirm, then Dad's. For Dad's it
demands his own quoted words and refuses any quote under 20 characters. On 2026-10-28 it refused
"i confirm #549". On 2026-10-29 it refused "i confirm #676" and "i confirm #654". Dad, twice: the clerk
is not in charge, and "me saying i confirm #676 is good enough and always has been". The 20-character
floor was a guess at "a whole thought", and it fails the plainest whole thought he can type.

## What the rule is for

It must refuse a bare yes ("yes", "ok") that could be about anything. It must never refuse a sentence
that says which piece and says confirm. What it cannot be is a keyword filter: a bag of "confirm" and a
number passes "i do not confirm #654" (Aria, 2026-10-29, and Dad's earlier "all you did was add more
keywords thats the wrong fix").

## The design (Aria's grammar, accepted)

For a quote shorter than today's floor only, accept it when the WHOLE quote matches:

    [i] (confirm|confirms|confirmed) [pr] <number list> [trailing punctuation or an emoticon]

where a number is digits with an optional leading `#`, and a list joins numbers with commas or "and".
The PR being filed must be one of the numbers named. A quote at or over the floor keeps today's rule.
The check that his words are found in what he typed AFTER her confirm was recorded stays exactly as it is.

Accepted for 654: "i confirm #654", "confirm 654", "i confirmed pr #654!", "i confirm #657 and #654".
Refused: "yes", "ok", "i confirm", "i do not confirm #654", "i would confirm #654 if she had read it",
"i confirm #655" when filing 654, anything containing a word he did not type.

## What it does not touch

The after-her-confirm check, the exact-words-he-typed check, the length rule for long quotes, the two-step
flow, and Aletheia's side. Nothing about who may confirm changes.

## Open for the walk

1. Is a number list with "and" worth the extra grammar, or does it invite padding? (Dad did say two PRs in one line.)
2. Should an accepted short quote be marked in the finding text as "short form, grammar match", so Aletheia can count them?
3. Does anything else read `_MIN_WORDS_OF_HIS`? (grep found only line 26 and 249.)

4. Dad, 2026-10-29: "whats more important is the actual audit its tied to and the time stamp of my words
   confirming it". That is what the record has to hold, and the length of the quote is not. So the design
   adds: the finding for his confirm also records the time his words were typed (taken from the transcript,
   which the filer cannot set) and the round id and tree it is tied to, so anyone reading the record can
   see "this yes, at this time, for this exact tree" without trusting the quote's shape. To check in the walk:
   does the clerk already read that timestamp to enforce "typed after her confirm"? If yes, the change is only
   to print and store it.

## Council walk at draft level (2026-10-29, consult-66c668e27be5)

Framing: "what is the best shape for this fix" (solution generation), not hole-finding. The manager surfaced
Aristotle, Lamport, Carmack, Taleb, Angelou, Deming. I added Norman (never invoked in the last 20; Dad is the
user typing the word, and the builder is not the user). Left out: Hawking (limits of what can be observed at a
boundary; this change is a typed string and a timestamp, and Lamport's invariants already cover what he would add).
This is the draft-level walk. The walk bound to the diff, one scope per changed file, happens when code exists.

**Through Aristotle:** the floor's purpose (final cause) was "do not put a bare yes on the record as his word".
Length was a material stand-in for that purpose, and it fails the plainest real confirm. The purpose is served by
the record tying the yes to one audit and one moment, as Dad said, so the grammar is the right form.

**Through Lamport:** the invariant for a finding "Andrew confirms PR N at tree T" is three facts: his words are found
verbatim in text he typed; they were typed after the store's own timestamp of her confirm; they refer to N. Today's
code enforces the first two and never the third (a long quote like "yes i confirm all 14" is attached to whatever PR is
being filed, by design as a standing confirm). The grammar adds the third only for short quotes, where there is nothing
else to tell which piece he meant. Say so in the docstring so nobody reads the number check as universal.

**Through Carmack:** two paths (short quote by grammar, long quote by length) is more mechanism than one. Could one rule
do it, "has a confirming verb and either names the piece or runs long"? That is the keyword bag Aria showed passes
"i do not confirm #654". The two-path form stays because the whole-match grammar is the only part that is cheap and sure.

**Through Taleb:** a wrongly accepted quote puts words in his mouth on an append-only record: irreversible. A wrongly refused
one costs one retype. The asymmetry says lean to refusal, which the whole-quote match does. Via negativa: the number
list ("#657 and #676") is the one extension; keep it, since he really wrote that, but accept it only for numbers named.

**Through Angelou:** his words must be filed as he typed them, never tidied, capitalised or completed. The short-form
finding is marked as such and carries his exact characters, so the record is in his voice.

**Through Deming:** plan/do/study/act, and the study step is the one that gets skipped. Mark each accepted short form in the
finding text so Aletheia can count them, and look at the count after a week: refusals of his real messages should be zero.

**Through Norman:** the refusal message is the interface. "At least a sentence" taught me nothing and sent me to pad.
The refusal should list the accepted short forms ("i confirm #N", "confirm N", a list joined by 'and' or commas) and the other
way through (a longer quote of his own words), so whoever hits it knows the move.

**Convergence:** Aristotle, Lamport, Taleb and Norman all land on the same design. **Dissent:** Carmack wants one rule;
Taleb and Aristotle want the tight grammar. Resolved for the grammar, and the Lamport note about the number check goes in the docstring.

## Process

Draft (this), council walk with the changed file named, tests first, Aria's cold read, Watchmen round with
`diff-hash`, then the merge. The branch opens as a two-for-one when merges are moving.
