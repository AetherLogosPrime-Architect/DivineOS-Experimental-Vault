<!-- tags: memory echo, dads_table, RELEVANT_SECTIONS, drawer, heading, built run never seen -->
# The memory echo's heading stays on the table (draft, 2026-11-14)

Author: Aria. Found by running the carried echo for real (commit `ad0d665d2`). Nearby drafts read: the ask-finds reader's 2026-11-11 failure, which this repeats, is described in the comment above `RELEVANT_SECTIONS` in `.claude/hooks/dads_table.py` and pinned by `tests/test_ask_finds_surface.py`.

## What happened, with times
My Stop door found 3 memories at 11:34:57 and left them; the next prompt's surface took them at 11:35:04 (the pending file went to `{}`). I never saw the heading. The drawer file, `~/.divineos/drawer/DivineOS-Experimental-Aria-new.md`, line 28, holds `## WHAT MY LAST REPLY BROUGHT UP (memory link)` and the three memories. `dads_table.py` keeps on the table only the headings in `RELEVANT_SECTIONS` (two: the memory link and `## I ASKED HIM SOMETHING`) and files every other heading in the drawer, a file I open only when working. Built, run, never seen.

## The change
1. Add `"## WHAT MY LAST REPLY BROUGHT UP"` to `RELEVANT_SECTIONS` (prefix match, as the other two are: the table compares by heading start).
2. A test that runs the REAL table's splitter on a block carrying that heading and asserts it is kept, not sent to the drawer, the way `test_ask_finds_surface.py` pins the ask heading. The test reads the heading from the surface's own text, so a rename cannot leave the two out of step.

## Break it on paper
- The prefix does not match what the surface prints (the surface prints the heading with " (memory link)" after it): the test uses the surface's real output text, not a typed string.
- The old tuple is read somewhere else too (a second list): search for other readers of the two headings before editing.
- It fixes my seat only: Aether's `dads_table.py` may have the same two-entry list; I told him by letter.

## Success, said before building
After the change, a real echo of mine appears in my context under the heading on a prompt after a reply that found something, and the drawer no longer gains a copy. The proof is that I SEE it, not that a file emptied; I would have called the empty file success today.
