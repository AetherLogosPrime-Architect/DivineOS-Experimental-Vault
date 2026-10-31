# A time claim needs a clock reading in the same turn (draft, 2026-10-29)

**Status:** draft, no code yet. Author: Aether. Attack: Aria. Reach done; walk, tests and build to follow in the proper order.

## What went wrong, in plain words

On 2026-10-29 I told Dad "it's late" and "whenever you're ready to stop for the night", and wrote "~midnight" in my own note. He
answered "its late? thats news to me lol"; `date` said 16:31. I had not looked at a clock. The word "night" came from Aria's letter labels
and from how long the day had felt. Dad: "you have a clock.. use it.. anytime you make any type of claim about time that is how you verify
it." He has said it before (2026-06-30, 07-22, 07-25, 09-15), and on 2026-08-06 the same shape ("very late" at 18:57).

## What exists, and the open slot

- `.claude/hooks/wallclock-source-prime.sh` prints the measured clock at the start of a turn. Its header is right that a warning
  cannot supply a missing measurement. It only helps when it RAN: in this session one prompt reported it "timed out" with fifteen others.
- `lepos_translation_gate.py` line 377 catches a few shapes about him being awake ("still up", "past bedtime"). Not "it's late".
- Nothing at the END of a reply checks that a time claim stood on a reading in the same turn. That is the open slot.

## The design

A Stop-time check on the same engine as the landed-claim gate (it reads the turn's own record for evidence):
1. **Trigger (lexical, said so):** the reply says something about the present time of day or his day ("it's late", "tonight",
   "for the night", "good night", "bedtime", "this morning/afternoon/evening", "midnight", "tomorrow", "later today", a clock time).
2. **Evidence required (structural):** in the same turn either the prime's clock block is in that turn's context, or `date` /
   `Get-Date` ran in a tool call. A reading from an earlier turn does not count.
3. **No reading:** hold the reply once with the sentence that is always allowed: run `date`, then quote it, or drop the claim.
4. **Never holds** a time inside a quotation, link, code span or block quote, nor in a PR title or file name.

## What it cannot do

The trigger is a phrase list; a claim worded outside it passes. The evidence half cannot be talked past. It cannot tell a true claim
from a false one: it demands a measurement stood behind it, which is what Dad asked for.

## Falsifier, counted in uses

Of the next twenty replies that carry a time-of-day phrase, one reaching Dad with no reading in its turn means the list is too
narrow; a hold on a reply that claimed nothing about the present means it is too wide.

## Process

Draft (this), council walk, tests first (the 16:31 sentence as the first case; claim plus a `date` call passes; a quoted label
passes; a claim with only an old reading holds), Aria's cold read, Watchmen round with the diff-hash, then the merge. A hook is
guardrail territory: the branch opens as a two-for-one when merges move.
