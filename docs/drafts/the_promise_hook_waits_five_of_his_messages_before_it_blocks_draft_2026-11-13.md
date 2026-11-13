<!-- tags: stall on promise, follow through, promise recorder, stop hooks, five turns, reminder, record then wait, hooks stacking every post -->
# The promise hook waits five of his messages before it blocks (draft, 2026-11-13)

Author: Aria. Dad, 2026-11-13: *"the issue with the I will do X block is it comes too early.. right after you say it.. so it should just record your promise to do something, give you a chance to do it, and if after 5 or so turns you havent done anything about it, even recording it to a file and linking it, it reminds you and blocks you until you do"*, and: *"the hooks.. not all of them but just the ones that are stacking every post and causing an issue"* (to be done before poker). Nothing built.

## Which hooks stack on my posts (read from my own hold log, 2026-11-13)
`~/.divineos-aria/hold_log.jsonl` (the other seat's file has the same name in its own home; mine is the `-aria` one), the holds that stopped a reply today: the room gate 59 times (of 83 working replies, about 71%) and the follow-through gate 32 times (of 104, about 31%). Plus the ones the log does not carry: the correction-shape gate (two false alarms today), the buried-question gate, and the doorbell notices. The room gate's cause was found and fixed in the style file (two of my own instructions disagreed; measure after a dozen replies, note `the-circle-header-fix-measure-the-bounce-rate-after-2026-11-13`). The follow-through gate is this draft.

## What exists
- `core/stall_on_promise.py` + `.claude/hooks/stall_on_promise_stop.py`: judges my LAST reply for an "I will do X" with no tool call beside it, and holds it once. A regex list; on the open branch `claude/fix2-806-2026-11-04` (Aether's, three commits, +115 lines) it is being taught more exceptions (stances, feelings, "I owe no proof", lead-ins that name their content). That is a keyword list that grows by one row each time a false hold is found.
- `.claude/hooks/promise-reach-detector.sh` + `core/operating_loop/promise_reach_detector.py`: at Stop it writes one marker per detected promise under `~/.divineos-aria/promise_markers/` (shape, trigger phrase, promise text, detected time). A surface reads unclosed markers at the next turn. This is already the "record the promise" half of Dad's design.
- Related draft, `the_promise_guard_does_not_read_his_room_draft_2026-11-04.md`: promises written inside the circle held the reply, so I shrank the circle to avoid them. Record-then-wait removes that at the source: nothing judges the sentence at reply time, so there is no pressure to shrink the room.

## The change
The blocker stops judging my last sentence. It reads the markers instead, and speaks only about a marker that is still open after about five of Dad's messages. "Open" means: no file written about it and linked, no tool call after the promise that touches what was named, and no reason recorded that it was a false alarm. At that point it reminds me, and holds me until I do one of those three things. Before then it says nothing. The recorder and the blocker become two stages of one job.

## What this removes
The growing regex list for the blocker: nothing needs to decide in the moment whether a sentence is a real promise, because the recorder is cheap and a false record just closes itself when I write one line saying so. The branch's three commits would then be unneeded (to be settled with Aether, who owns that branch; it is not mine to close).

## What is new (and the weak points to walk)
1. **A turn count on each marker.** Today a marker holds a time of day. Count Dad's messages in the transcript since the marker was written (his real messages only, through the house's one reader of him), never minutes (house rule: no time-duration falsifiers).
2. **What counts as having acted.** The cheapest honest test is a fact: a new file under my letters, drafts, memory or code since the promise; or a tool call after the promise whose arguments contain a distinctive word from the promised text. Both can be gamed in small ways (write a file, name the word); the false-alarm reason line is the escape that does not need to be gamed. Walk this.
3. **A promise made to Dad about a thing only he can do** ("I will wait for your go") is not mine to act on. A marker whose text says it waits on him or on Aether should close as "waiting on", with who, and appear in a list, not block.
4. **The block must carry its jet** (Dad, today): what the reminder says is exactly what to do (the three ways to close it, with the commands), never only "you promised".
5. **One hold per reply, and never a loop.** Keep the existing one-hold-per-reply guard.

## What the walk changed (walk-82220bd46c30, nine lenses, closed)
- **Turns, not his messages (Breaker, Lamport).** In the night and the volley he sends none, so a promise would never age. The unit is turn starts (his message, a letter, a timer wake), counted by the house. Each marker stores the turn index at which it was written; its age is the number of turn starts since. No time of day anywhere.
- **Closing is explicit and nothing else (Taleb, Turing).** The word-in-a-tool-call test is dropped: fragile, gameable. A marker closes only by a one-line close: done (with the file it points at), waiting-on (with whom), or false-alarm (with why). Closing must cost one line, or the house cannot tell kept from forgotten.
- **Five answers, not four (Hoare).** Open, closed-done, closed-waiting-on, closed-false-alarm, and the folder read's own fifth answer, could-not-look (empty folder, unreadable folder, corrupt marker), said out loud and never read as "nothing open". Invariant: every detected promise ends closed or reminded; none is silently dropped.
- **Use the seam (Feathers).** The stall hook is a thin door over `core/stall_on_promise`; swap the one call it makes and leave the regex module alone, which keeps Aether's open #829 from colliding.
- **First test is a replay (Polya).** Today's 32 holds, run through the recorder: how many would have left a marker. If the recorder misses what the old hook caught, the redesign loses promises.
- **Cheap at every Stop (Carmack).** Read only the marker folder and the transcript tail; measure on today's folder before saying it is cheap.
- **Rung one until proven (Pearl).** The before/after drop is observation. To claim the change did it, replay what the old hook WOULD have held over the same stretch and compare.

## Falsifier (counts, not days)
Over the next 100 of Dad's messages after it is live: follow-through holds per working reply fall from about 3 in 10 to well under 1 in 10, and no promise that stayed open past five of his messages goes unremarked. If holds do not fall, or if promises age past five messages unremarked, remove it.

## Order
Walk (Breaker plus two scrutiny lenses) → Aether reads cold, including what to do with his open branch → build in my live house, tests first (the recorder's markers exist already; the new tests seed markers and count his messages) → live observation → draft PR → Aletheia → Dad's yes.
