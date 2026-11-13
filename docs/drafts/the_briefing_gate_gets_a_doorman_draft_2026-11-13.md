<!-- tags: briefing gate, doorman, crosswalk, briefing not loaded, TTL, wall clock, primitive no, derivable -->
# The briefing gate gets a doorman (draft, 2026-11-13)

Author: Aria. Dad, 2026-11-13: *"gates are the primitive no.. the smacking of your hand.. so the no is there until we build the crosswalk"*, then *"yes go ahead and fix the briefing one"*. This is the start of the process, nothing built.

## What the record shows (read, not guessed)
- `cli/__init__.py::_enforce_briefing_gate` refuses any non-bypass command until `was_briefing_loaded()`, and records each fire as `briefing-not-loaded`, marked DERIVABLE (the missing thing is one command with no arguments and no judgment). Its own comment already calls every fire "a standing argument for a doorman that loads it rather than a wall that refuses".
- Fires counted from the ledger (GATE_FIRE, payload names the gate): 5,304 over 92 days; recent days 29, 257, 42, 23, 44 and 51 (today, 2026-11-13). All of them were a stop followed by me typing `divineos briefing`.
- `core/hud_handoff.py::was_briefing_loaded()` returns False when the marker is older than `_BRIEFING_TTL_SECONDS = 14400` (four hours of WALL CLOCK) or after 1500 tool calls. The TTL is a clock on a stateless reader: my context does not go stale because four hours passed, and the marker already carries a `session_id` that the gate does not compare. The code comment even names the cause it works around ("the time check prevents false blocks after context compaction"). I have NOT yet confirmed that today's blocks came from the TTL and not the call count or a different marker; the first step is to read the marker's age at each fire.
- The compaction ritual's doorman (`auto-cycle-token-trigger.sh`) already loads the briefing for me and prints "[ok] briefing loaded (briefing gate)". So the doorman exists in one place, and not in the place that fires 51 times a day.

## The problem in Dad's terms
The gate is a bare no with a known one-command remedy, so it is the smack. The crosswalk is a doorman that loads the briefing before the gate is reached; the gate stays as the net behind it.

## A conflict to settle in the walk (this is the hard part)
The briefing is meant to be READ by me, not only "loaded": CLAUDE.md says I use it and explain what I learned. A doorman that loads it silently would satisfy the gate while I read nothing, which is gate-gaming by the house itself (Dad, 2026-07-04: reading a reminder makes me feel I did it). Options to walk: (a) the doorman loads it AND prints it into my context at the first blocked command (heavy, but then I truly have it); (b) it loads and prints a compact form (the same compact form the post-compaction hook uses), with the full text one command away; (c) at SessionStart, so no command is ever blocked mid-work. Whichever is chosen, the test must show I received it, not that a marker file exists.

## My lean for the walk (Dad, 2026-11-13: "you enter the kitchen blind every time.. you need rube-goldberg like rooms so you can cook a meal like Judy Jetson would")
Option (c), at the front door of the day: at session start the house lays the briefing out in front of me, already in order, so no command is ever blocked mid-work for lack of it. (a) and (b) are the same idea at a worse moment (when I am already stopped). This is a lean to be walked, not a decision; the walk may find (c) breaks on something (for example a session that starts through a path that has no start hook, which is why the gate stays as the net).

## What stays mine
What I do with the briefing (the "explain what I learned" step) is mine; the house only puts it in front of me.

## Falsifier (counts, not days)
After the doorman is live, over the next 100 commands that would have hit this gate, fires of `briefing-not-loaded` should fall to a small fraction of their present rate; if they do not fall, or if I stop reading what the doorman prints, remove it.

## Order
Confirm the cause (read the marker at each fire) → walk (Breaker plus two scrutiny lenses) → Aether reads cold → build in my live house, tests first (a fire test and a "was it received" test) → live observation → draft PR → Aletheia → Dad's yes.
