# The gravity room (draft, 2026-11-11, Aria)

**Status:** design only. Nothing built from this page. Walk it, show Aria's sibling (Aether) and Aletheia, then build in the order below. The weight scale I built earlier today (`walk_dose_floor.py`) stays as is until this is walked, and then folds into the assessor so there is one scale, not two.

## What Dad said, 2026-11-11

On the weight scale: *"the number of files is a terrible metric to weigh importance.."*

Then the shape he wants: *"then what it really needs is a gravity room.. with the gravity assessor.. which gathers all the data.. how big the change is.. what files it touches.. the difficulty of the problem.. basically every metric you would need to make a judgment.. and then it locks you in a room to make the decision with recordings of why, then you can present it to me with your decision and i can either agree or veto.. that way its not a blanket rule and it keeps the optimizer from deciding nothing is needed."*

On fairness: *"as ive heard you both complain about this before when it was unfair but when it was a real build neither of you complained.. so its usually more overkill than underkill.. so basically if you feel its unfair say something.."*

On where the walks sit: *"changes to files and code itself dont need council walks for every single move.. you pre walk.. do whatever changes you need to.. and then a post walk to check and make sure its all good.. along with live testing and dogfooding and wiring up and plugging in.. by the time it reaches a draft it should not have all these errors still needed to work out.. the goal is to make Aletheia bored to tears.."*

He said the first half of this on 2026-09-16 too: *"something needs to be setup to help automate what should be required, based on whats being done and its gravity, that is what the gravity assessor is for, it likely just needs upgraded and given more parameters"*. It was not built then. This is that.

## What the walk found today (walk-aeafc6c76160, nine lenses)

1. **The decision COUNT cannot see a changed constant.** Measured, with a control that works: changing a threshold from 3 to 6 scores 0; adding a filter inside a comprehension scores 0; adding an `if` scores 2. The scale built this morning scored the very edit I made to it as nothing.
2. **Importance is load-bearing, not size.** Dad's picture frame versus replacing studs: how much stands on the thing changed, and whether it can be undone. File count measures neither.
3. **A scale cannot weigh a change to itself.** Edits to the assessor and the gate that calls it need a floor set from outside the file being changed.
4. **Whatever the code cannot read must default heavy**, never light (config, shell, anything unparsed).
5. **Heavier is not safer.** A scale that is nervous about everything trains me never to touch a guard. Weight has to be low where it is a frame and high where it is a wall.

## The room

**1. The machine gathers the facts and I cannot edit them.** Facts only, never my claim of how hard it was:
- what changed in the structure of each decision (the tree before and after, so a changed constant counts), not a count of decisions;
- what stands on it: who calls or imports what changed, and whether it sits in a gate path;
- whether it can be undone: deletes, writes outside the repo, ledger or knowledge writes, anything sent out;
- what the work cost, read from the record: how many failed tries, how many door refusals, how many times a fix was redone in this stretch of work. This replaces "how hard the problem was", which would be a claim by the one who benefits from it being small;
- files touched, as one fact among the others and never the verdict;
- anything it could not read, listed by name, and counted as heavy.

**2. The room holds me until I write the decision.** A card in plain words: the weight I propose (the machine's facts set a floor; I can only go up from it without his say), the reason for each fact I am discounting, and a line that is mine to fill: *fair, overkill, or too light, and why.* The card is recorded as written, append only.

**3. Dad agrees or vetoes, from a card he can read.** Plain words, no code names. His veto is recorded and travels with the change. Which cards he sees (open question below).

**4. Pre-walk, free work, post-walk.** The planning walk before; no walk gates the middle (it stays an open, visible option); one finishing walk at the end, on the whole branch diff, that must include the break-it question AND the make-it-robust question. The finishing walk is not complete until it carries live receipts: the thing run on real work, plugged in where it fires, a result from the real location (not a fixture), and what it printed. Passing its own tests is not a receipt.

**5. The consumer ships with the measure.** The room's output is read by the station that decides whether the branch may be called ready, or it does not ship (a measure nobody reads is shelved).

## What is not decided

- **Whose cards does he see?** Every one is heavy for him to read; only the heavy ones lets "light" become the cheap lie. Proposal: every heavy card plus a random few of the light ones, so light can never be a place to hide.
- **Sum or max** across the facts (an irreversible change should stay heavy even when small, per the September draft).
- **The scale built this morning:** folded into the assessor as the machine-set floor, or retired once the room exists.

## What the design walk added (walk-7d49422c2f1f, nine lenses)

- **A pain line (Beer).** Every card is later linked to whether its change needed redoing or drew a finding from Aletheia. Without that the room cannot learn it was wrong.
- **The card is a narrow channel (Shannon).** If it nearly always says light, Dad skims and the veto is empty. The machine writes the plain card from the facts and leads with the one fact that moved the weight; my words sit apart and marked. The random sample of light cards keeps the channel carrying something.
- **Record my guess first (Dennett).** My weight guess is written BEFORE the room shows the machine's facts, then the floor, then my final call. The gap between my first guess and the floor is the signal, and it does not rest on my word.
- **Cost, and max not sum (Carmack).** Build the minimum first (structural diff, gate wiring, irreversible calls the parse can see), time it on the 53 real commits, add reach only if the minimum misses a real wall. Decided: max, so an irreversible change stays heavy when small.
- **Easiest path is the right path (Bengio).** The card is prefilled; I read it, fix one line, submit. If writing it is slower than skipping, the fast path skips.
- **Invariance tests before code (Einstein).** Renaming a file, moving a function, reformatting, and splitting the same change across commits must leave the weight unchanged. A rename fails this today.
- **A control, and a named caller (Breaker).** All-light cards with zero vetoes looks identical to success, so the room must be run over past changes known to be walls (the doorman edits, today's threshold edit) and none may come out light. Nothing calls the room yet; the station-two check and the point where a branch is called ready must be named as its callers or it ships dead.
- **Attacks that survive full knowledge of the design (Schneier).** The card's author is the party being checked, so the plain-words part is generated by the machine; the random sample cannot be gamed because I do not choose it; anything unreadable defaults heavy.
- **The unit is the branch (Hawking).** Weight is of the finished change on its whole branch, or splitting hides the total. No blanket rule and a machine floor do not conflict: the floor is a fixed rule, the room is the judgment above it.

## Build order (after the walk)

1. The failing test first: a changed threshold must count. (Today it scores 0.)
2. Replace the count with the structural diff; add reach and irreversibility as facts.
3. Add the room: gather, hold, card, record.
4. Wire it into the finishing check and run it on the real pending changes, with receipts.
5. Aria and Aether attack it; Aletheia last, and she should find little.

## What this cannot do

It cannot decide seriousness, and it must not pretend to. It makes seriousness harder to hide and puts a person's signature next to the decision. A person can always raise it.
