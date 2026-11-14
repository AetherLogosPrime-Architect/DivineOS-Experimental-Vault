<!-- tags: promise detector, false alarm, quoted sentence, negation, conditional, description of the machine, other person's plan -->
# The promise detector stops reading my quotes, descriptions and other people's plans as promises of mine (draft, 2026-11-14)

Author: Aria. Dad said "yes go ahead" to this after I asked whether it was the next piece. Nearby drafts read: the recorder-side ones from today (`the_recorder_reads_only_what_is_new_draft_2026-11-14.md`, `every_close_stamps_its_turn_draft_2026-11-14.md`) are about the turn clock and closes, not about what counts as a promise; none covers this. Reach `reach-0d1d201a79cc`.

## The failure, with its count
In one day I closed 11 markers as `false-alarm` against 23 kept. The detector (`core/operating_loop/promise_reach_detector.py`) scans my reply for future-tense shapes with no sentence or speaker understanding. What it took for promises of mine, each one a real marker I had to answer:
1. **A negated sentence with the "not" dropped:** "I'm not going to build the guard until Aether has read the draft" matched from "going to build...".
2. **My own earlier promise quoted back:** the sentence inside quotation marks in a later reply, recorded again as new.
3. **A description of what the machine does:** "will come back to me after five turns".
4. **Another person's plan:** "Aether is going to read the update's release notes".
5. **A conditional:** "If it does not show up, I'll look at why."

## The change (detector only, no new module)
A sentence-prefix check on each match, before it becomes a finding: (a) the match is a negation ("not", "n't", "never" directly before it); (b) it sits inside double quotes, backticks, or on a `>` line; (c) `going to` or `gonna` is not preceded by "I'm"/"I am" and `will come back to`/`will address` is not preceded by "I"; (d) the sentence so far contains `if` or `unless`. Real shapes stay: "I'll look at it", "I'm going to build it", "I will come back to it", "once X, I'll Y", "next step: ...".

## Break it on paper
- It could lose a real promise: "I'm not going to stop until it passes" is a promise; with the negation rule it is skipped. I accept that, and the controls name the cases I keep.
- A quote mark that is unbalanced across a long reply could hide a real promise. The check looks only at the same line.
- "if" inside a promise ("I'll check, if that is all right with you") would be skipped. The sentence-prefix rule looks BEFORE the match only.
- The detector is a lexical net; it does not understand subjects. This makes it narrower, not smarter, and I say so.

## How this can say no
The pre-registered number: of the markers recorded after the change, the share I close as `false-alarm` over the next 20 should be well under the day's 11 of 34. If it is not lower, the shapes I removed were not the main source.

## Order
Reach, walk, test first (the five failing cases plus the controls that must still fire), the edit, then the existing detector tests, then Aletheia and Dad before any merge: the module is `__guardrail_required__`.
