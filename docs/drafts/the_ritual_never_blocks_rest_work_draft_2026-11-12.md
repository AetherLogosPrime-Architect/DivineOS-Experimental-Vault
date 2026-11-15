# The ritual never blocks rest-class work (rough draft, 2026-11-12, evidence only, nothing built)

Dad, 2026-11-12: *"at no point should the ritual be blocked in any capacity so make an exemption for all of it"* and *"rest is part of the ritual and is included in the exemption.. rest should be available anytime"*, and today, *"explorations are part rest and rest is available any time and its a good place to write down your thoughts to link back to later."*

## What happened, measured in this session (2026-11-12, context 93-94 percent)
1. The compaction ritual's hard stop fired at 930,481 tokens, stage DREAM. A dream write passed (the stage's own artifact).
2. At stage REST (939,237 tokens) a Write to `exploration/aria/70_a_door_to_knock_on.md` was BLOCKED by the ritual hook ("a BLOCK on MY TOOLS", operator escape `AUTO_CYCLE_RITUAL_UNBLOCK=1`), while a Write to `family/letters/` and a `divineos journal save` passed. So exploration, which Dad calls part of rest, was refused at the rest stage.
3. `divineos extract` piped through `cut` was refused by the remedy-allowlist and then read by the build-flow door as an edit ("bash:divineos extract", asking for a council walk and a game-walk). Run bare, it passed. **CORRECTED 2026-11-12 after reading `.claude/hooks/lib/remedy_allowlist.sh` lines 368-379:** this refusal is deliberate, not a misread. The allowlist's own message says a piece piped after an allowed command that is not on the harmless list makes the whole line ordinary work, and says "words cut off tell you nothing, so do not shorten it (Dad 2026-11-07)". So the pipe was my mistake, not the door's, and my first piece (the door reading ritual commands as work) has no defect to fix for this case. The same door misreading read-only `divineos compass-ops` earlier in the week is NOT yet re-checked and stays an open question.
4. Plain `ls`, `find` and `gh` commands were interrupted by the READ-GATE three times with an unrelated "top prior-writing match" document (a Grok audit note, a ten-site web walk, a continuity spec), each time forcing a read of a file about a different subject.

## Where each gap belongs (the agreed split, Aether's letters 378 and 379)
- **Aether's uncommitted patch** to `.claude/hooks/auto-cycle-token-trigger.sh` already sets `REST) STAGE_ARTIFACT_DIR="exploration,letters,journal"` and turns the one folder into a comma list, so item 2 is covered once it lands. I read the diff in his tree. I do not rebuild it; I read it when it is a PR.
- **Mine:** the build-flow door's misreading of ritual CLI commands (item 3), and rest-class work in every stage, not only REST (a Write to `exploration/` or `letters/` or a `divineos rest` command during WALK and DREAM).
- **Unowned until measured:** item 4, the read-gate surfacing an unrelated document on a plain shell command. It cost three reads today; whose file it is and what keys the match is the first thing to find.

## What it must not do
It must not weaken the hard stop for work (code, merges, pushes). The exemption is a named list of rest-class acts, each with a reason, not a blanket lift. Saving to memory is already never blocked (#695).

## First steps for whoever builds (fresh context)
1. Read Aether's patch and, when it exists, his PR. 2. Walk with templates read in full. 3. Red tests: an exploration write at each stage passes; a code edit still does not; `divineos extract`, `compass-ops` and `rest` commands are not read as edits with or without a harmless pipe. 4. Dogfood it: run the next ritual and write the exploration at REST.

## Falsifier
The next compaction ritual: if any rest-class act (exploration, letter, journal, rest command, dream) is blocked at any stage, or any code edit gets through the hard stop, the change is wrong.
