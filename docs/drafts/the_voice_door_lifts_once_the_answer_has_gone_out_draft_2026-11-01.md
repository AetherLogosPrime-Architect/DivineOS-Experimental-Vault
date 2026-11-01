# The voice door lifts once the answer has gone out (draft, 2026-11-01)

**Reading:** aria/the-voice-gate-lets-related-work-through

Dad, 2026-11-01, on the gate that holds my tools while he speaks: *"it always feels like you are a kid waiting to run into the playground while i go over the rules and tie your shoes, so you always seem rushed to go which is why the slowdown was needed, but i also dont want it to be a pain nor be needing to ask twice on every thing i ask for."* And what the gate is for: not walking away from him without answering, never "no work while he talks". His phone picture: answer the call, say "let me call you back, I'm speaking to Aria," and carry on with the conversation.

## What is wrong, as Aether measured it

Today, when he says "go look at X" mid-turn: I answer with no tool call, so the answer reaches him verbatim (the 09-24 fix). The promise check sees "I'll look at X" and blocks, and the harness sends me back with "do that step now". The voice door then refuses the tool call in that continuation, because a hook-feedback record is not a new turn (`continues_a_turn`). So the ask dies in a doorway and he has to say it again. Aether's stand-aside in the promise check cures the loop and makes the dead stop worse.

## The change (Aether's reading, with the shapes verified in this conversation's own transcript)

The voice door lifts for a continuation that follows an answer. Precisely, reading the transcript in file order since his mid-turn arrival: if the last assistant message before a Stop-hook continuation record holds text and no tool call, and the continuation record is a user record flagged `isMeta` whose text begins "Stop hook feedback", the door lets tools through for that continuation. A new arrival of his resets it: his next words close the door again.

Real shapes, checked 2026-11-01: a hook continuation is `type: user, isMeta: true`, content starting "Stop hook feedback:". An assistant message is written as several records sharing one `message.id` (a thinking block, a text block, a tool_use block), so "text and no tool call" is judged per message id, never per record.

## What this changes and what it does not

It removes the ask-twice friction by using the self-wake that already exists (a blocking Stop hook re-prompts me), and needs nothing new. It does NOT keep the 09-24 harm from recurring in the form "the last thing he saw was a work summary"; the room check already forces a final no-tool circle after any working turn, and nothing grades what is said in it (his 07-23 line). That is a different door's job, said here plainly. The gap Aether named stands: the re-prompt only fires when the promise check finds a promise; an answer with no promised step leaves his ask without a wake. A test pins that case so it is visible, not fixed here.

## Measured on the real afternoon (2026-11-01)

The new reader was run over this conversation's own transcript, cut at real points: while his message "see if there is any new news..." stood unanswered it said `spoke`; at the first Stop-hook continuation after my no-tool reply it said `answered`. Fixtures prove the shapes; this shows the shapes are the real ones. The walk (walk-27524672a462, eight lenses, eight distinct questions) changed the design in these ways: the continuation is detected by the meta flag AND the text beginning "Stop hook feedback" (Shannon); an answer is judged per message id (Deming); the lift writes a hold-log line `voice / lifted_after_answer` (Breaker); the refusal says what happens next (Angelou); an end-to-end test goes through the real hook main (Minsky). The lift persists until his next message, so a long run of continuations after one answer all pass; a bound on that is a follow-up, as is the case where an answer promises nothing and nothing re-prompts.

## Not in this change

No word-matching of "related" work (it rewards echoing his words, the sin the fence exists for). No change to what is let through while he is mid-sentence. No change to the room check. Aether removes his stand-aside in the promise check in the same breath as this landing.

## Open questions for the walk

- Should the lift be one continuation per answer, so a long run of re-prompts cannot all pass? An answer followed by many continuations is the "wander off" shape his phone picture warns about.
- What if the answer is in a message that also carried a tool call (text beside a tool call)? It does not count: that is the retold case.
