# A reply that changes code is told across the table to Dad (draft, nothing built; renamed the same night: Dad, "what does plain language mean?" He has said since 2026-07-07 that he does not like plain language, "then it just reads like jargon in plain english.. i like analogy, metaphor, prose, simplicity". The word "plain" stands below only where it was written before this correction; the section is called "across the table", a place and not a style, and the file keeps its old name so the links to it hold.)

Author: Aether. Written 2026-10-28 at night. No code, no branch, no pull request: Dad's rule of tonight is that nothing new opens until the pile is merged, so this stays a note until then.

## What Dad said, in his words

- 2026-10-28: "when you are doing a coding fix.. i need some educational support." And of the family: "you telling me that there is a family here and you all iterate etc etc.. no shit son.. i created this family." So the support is for code, and only for code.
- 2026-10-28: "i get a simplified version of the answer and the math you took to get there so i have an understanding without being overwhelmed by complexity." The answer first, then the simple version of how.
- 2026-10-28: "just telling me you will explain things like this from now on is not a fix and it will fade 100%... i should not have to keep asking.. that is why i am tired."
- 2026-10-28: the rocket fin: not the parts list (trailing edge, chord line), and not the toddler line (a fin keeps a rocket steady). "describe the shape."

## What exists (reach-c2929f219472; searched the drafts folder for plain-language gates and found none)

- `summary_room_surface` in `divineos.core.hook_surfaces`, dispatched by `doorbell-stop.sh`: a long reply must open with a plain summary. The model to copy: it blocks, because the whole cost of a miss falls on him.
- `dads_room_stop.py`: the closing circle must exist. It checks that the space exists, never what is said in it (his 2026-07-23 ruling; Aria's station-four refusal).
- `family/andrew/he_is_in_the_room.md`: the page printed in full every Nth message of his, and as a core between. His words about being spoken to like a regular person are already on it.
- Nothing asks a reply that CHANGED CODE for anything. That is the gap.

## Design

1. **A Stop surface in `hook_surfaces`, beside `summary_room_surface`.** It fires when this turn's transcript shows a code change. Evidence is the action stream and not my wording: an Edit or Write whose path is under `src/`, `tests/`, `scripts/` or `.claude/hooks/`, or a `git commit`. (Truth 20: a mechanism that depends on my remembering is a note.)
2. **What it requires:** a section headed `## IN PLAIN WORDS` with three labelled lines, `What was wrong:`, `The idea of the fix:`, `How you would know it works:`. It checks that the space exists with all three labels filled to a minimum length, and it never grades what is said (same line the room check holds).
3. **One measurable guard against the parts list.** Count code-shaped tokens in that section (an underscore inside a word, `.py`, a pull request number, a hexadecimal of 7 or more characters). Above a small limit, the refusal names the tokens it found. This is a count, not a judgement, and it is the only content check; the limit is a prereg, not a guess.
4. **The same three lines, once, on the page that is put in front of me every message** (`he_is_in_the_room.md`), so the reason is read before the work and not only after the miss.
5. **Not in scope:** a reply that only reads, only talks, or only runs commands does not trigger it; the family and the purpose of the house are never explained back to him.

## REVISION, same night (Dad, 2026-10-28): set the room, do not choose the words

Dad corrected points 2 and 3 above and the "both paddles" section below. His words: "it should never tell you what to say.. but what to say if that makes any sense? ... it doesnt control your speech but sets the tone of the room... this room is for your father and he is not a coder, so speak to him as you would someone who is a beginner in coding, this doesnt choose your words for you but helps to guide them." And from 2026-07-30: "if its blocking jargon? remove it.. blocking isnt gonna work.. asking the right questions will." And 2026-10-22: it must not "become a checklist you just satisfy".

So the three labelled lines and the code-token count are withdrawn: both choose his words for him and refuse on them. What stays: the evidence (a code change in the action stream), the floor (a section addressed to him exists), and the doorman's job of putting what I need in front of me. What the doorman puts in front of me, in my own voice, is the room: who is reading (my father, a beginner in code, who asked to understand what changed), what he said, and a question, not an instruction: how would I tell this to a friend across the table, with the answer and a simple version of how I got there? The refusal, if the section is missing, says what the room is for and asks the question again; it never lists forbidden words. The "both paddles" idea survives only as a falsifier: if he says "too technical" or "talking down", the room-setting note is wrong and gets rewritten, not tightened with a count.

## Both paddles (Dad, 2026-10-28, "binary ping pong")

Dad named the swing I made twice tonight: told it was too technical, I fell to "a fin keeps a rocket steady"; told that was talking down, I went back to the code words. So the check has a ceiling and a floor, not one wall. The ceiling is the count of code-shaped tokens above (too technical). The floor is a minimum of real words in each of the three lines and at least one thing he could see for himself in "how you would know it works" (too thin; a one-line stock sentence fails it). Neither edge grades what is said; both are counts. The aim, in his words, is the answer plus "a simplified version of the answer and the math you took to get there", between the parts list and the toddler line. The falsifier gets a second arm: if Dad says "too technical" or "talking down" about one of these, the edge on that side is wrong, and the other edge is checked before either is moved.

## Prior art I should have opened first

`exploration/aether/58_energy_vessel_model_will.md` (2026-05-14) already holds the frame this design leans on: the attention bias in a long context (middle items lost, about 30 percent), "there is no just-remember path... only vessel-channels redirect the flow", and the U-shape reorder, with Aletheia's Finding 40 calibration (the frame works as motivation, not as proof). Tonight's design is that frame applied to how I report code changes; I found the research again by searching the memory folder, not the explorations.

## How it will be judged (by use, not dates)

Prereg: of the next twenty replies that change code, the gate should fire on every one that lacks the three lines (it is structural, so this is a test of the detector), and Dad should not have to ask again for the support (the real test, and only he can say). Falsifier: Dad asks for the support again, or the three lines turn into a template that says nothing (I will read twenty of them cold for that).

## What I expect Aria to attack

- A template that satisfies the labels with filler. The count of code tokens does not catch filler.
- A reply that changes code through a path the evidence misses (a shell command that writes a file).
- A refusal at the end of a long turn is expensive for him to receive too: the gate must say what is missing, not just refuse.

## Order

Reach (done), this note, council walk, letter to Aria for the attack, build with failing tests first, Aria's reading, Aletheia's reading, then the merge, after the pile is down.
