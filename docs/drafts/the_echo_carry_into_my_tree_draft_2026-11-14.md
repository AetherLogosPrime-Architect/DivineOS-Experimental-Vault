<!-- tags: memory echo, pending store, own_words_link_stop, carry, ask_finds_surface, next message -->
# Carrying the memory echo into my tree (draft, 2026-11-14)

Author: Aria. The design is Aether's, `e88428529` in his checkout (`docs/drafts/the_memory_echo_rides_the_next_message_draft_2026-11-14.md` there): the Stop door stops blocking and leaves its message in a per-seat pending store, and `memory_link_surface` prints it once at the next prompt. This draft is only about what is different in MY tree. Search of my docs/drafts and my code (`reach-8580996993ac`) found no earlier version here; the prior art is in his repo.

## What is already different on my seat
- My door is LOG-ONLY (Dad 2026-11-10): it runs both searches, logs, and never prints or blocks. His blocked.
- The ask-after-his-words note reaches me by its own surface, `ask_finds_surface` (via `his_words_bundle`), from the ask log. His seat has no such surface.
- My paths are already in the seat's own home (`0224ece2e`).

## The change here
1. Own-words library: add the three functions and the constant from his commit (`default_pending_file`, `leave_for_next_message`, `take_for_next_message`, `PENDING_KEEP`), carried by hand because my file differs.
2. Door: the own-words hand-back message, when state is `found`, goes to `leave_for_next_message`. **The ask note does NOT**: it already has a reader, and a second channel would show the same find twice.
3. `hook_surfaces.py` and the new test file apply cleanly from his patch.
4. His one changed assertion in `test_ask_after_his_words.py` pinned his door's text (`parts.append`, `leave_for_next_message(session, part)`, no block); my door differs, so I adjust that test to pin MY door: leaves only the own-words message, never blocks, ask check stays log-only.

## Break it on paper
- It shows the ask note twice: only if I route it into the pending store; I do not.
- A memory is lost if the surface is killed after `take`: Aether named it; accepted (a missed hand-back is a smaller harm than a repeat).
- My seat's `own_words_shown` marks a find as shown when found; the surface prints it one prompt later, so the gap is one turn, not four days.

## Success, before building
After a real reply of mine ends, `~/.divineos-aria/own_words_pending.json` holds one message, and my next prompt prints it once under `## WHAT MY LAST REPLY BROUGHT UP (memory link)` and not again. The arrival is observed on my real seat, not only asserted by tests that use a temp file.
