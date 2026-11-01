# A hook may not carry its own decision (draft, 2026-11-01)

**Reading:** aria/an-exit-is-the-file-not-the-spelling

Dad, 2026-11-01: *"any that are firing and whose logic lives outside of the OS? is wrong."* That is the decision the 2026-10-08 draft (`there_is_no_hook_ceiling_and_the_notes_still_say_there_is_draft_2026-10-08.md`) said it needed: if anything is enforced it is thickness, never number, and a new hook may not embed its own judgment. It is now his rule, so the guard can be built. It must not be a ratchet on size: he killed that on 2026-09-08 with *"why would you build something that can only shrink and never grow?"*

## The definition, not a limit

A registered hook is allowed to find a Python and call a module of the OS. It is not allowed to decide. The check lives in `core/hook_layer.py`, which already reads the settings file and the hooks directory and already knows the doorbell form (`-m divineos`). It adds one question per registered script: does this file hold branching on tool names or on reply text of its own?

What the check refuses: a NEWLY registered script that carries its own decision. What it reports and does not refuse: the 65 existing judgment-carriers, which are the migration worklist and shrink as Aether moves them. Nothing is capped. A hundred pointing hooks pass; one thick hook fails.

## What it must measure, and what it must not trust

Facts about the file, never claims about the author: the script's own control flow (if, elif, case, while, for, && and || chains that branch), whether it calls a core module, and whether the branching is inside a heredoc of embedded python. An author could dodge by moving the decision into a second script the first one sources. So the check follows `source` and `.` of local files and counts the branching there too. It cannot see a decision hidden inside a call into the OS itself; that is the OS's own tests' job, and it says so.

## The danger I named on 2026-08-03 and still stands

A gate that goes silent mid-move without anyone noticing. Before a hook moves: a record of what actually fires now (observed in the ledger, not read from config), the same record after, and `degraded_detectors` as the net. Aether takes the three doors (the stall check, the addressed-to-him check, the room gate after note-only work) one branch each; I take this guard and the tracker (`docs/hook_consolidation_seven_doorbells_2026-08-06.md`).

## What the walk (nine lenses, 2026-11-01) changed

- **Three outcomes, not two** (Hoare): thin, thick, and could-not-read. A script the parser cannot read, or a sourced file that is missing, fails loud; it is never counted as thin.
- **Allow one form, do not blacklist patterns** (Beer): the guard has fewer ways to detect than authors have to hide logic, so it cuts the variety instead: a registered hook must be the doorbell form that calls a divineos module. Everything else is refused.
- **New means a named base** (Lamport): a hook is new if it is absent from the registered list at a base ref, and the check runs where hooks change (a commit touching the settings file or the hooks directory), not only when someone asks.
- **Look before fixing the definition** (Wittgenstein, question 7): grep the 65 for the constructs they really use before the rule is written, so the rule fits actual usage.
- **The easy path must be the thin one** (Dawkins, Meadows): thick hooks spread by being copied, and a refusal loses to "fastest way to add behavior is a new hook" unless adding an OS surface is just as cheap. The change ships a thin template and a one-step way to add a surface.
- **A refusal that helps** (Tannen): the message names the file, what it found, and the one-line fix, in the register of a helper.
- **Success must show its worklist** (Dekker): every run prints the count of judgment-carriers and when it last changed.
- **An operational definition** (Deming): a branch whose test reads the tool name, the prompt, the reply text or file content, with the presence guard on the hook file itself exempt.

## What the 77 registered scripts really hold (measured 2026-11-01, crude counts)

77 distinct registered scripts, all present. 59 call the OS, 16 embed python, 44 hold at least one control-flow line that reads the tool name, the prompt or the reply. Calling the OS is therefore not the test: `auto-cycle-token-trigger.sh` calls it and still carries 62 control-flow lines in 496. Only one script has two or fewer flow lines and reads no text, and even the doorbell template trips a simple count because its own guard (`if [ -f "$f" ]; then ... else ... fi`) is a branch. So the rule cannot be "no branching"; it has to name the doorbell's exact shape as the one allowed form (Beer) and measure everything else against it. The scratch script is `hook_constructs.py` in the session scratchpad; it should become a tested function in `hook_layer.py` and not stay a throwaway.

## The before-and-after record does not exist yet (measured 2026-11-01)

The plan needs a record of what actually fires before anything moves and the same record after. First attempt: count `GATE_FIRE` events in the ledger. Over the last three days it holds 381 events and only two distinct gate names (380 are `briefing-not-loaded`, 1 is `distancing_intercept`). Seventy-seven hooks are registered, so the ledger sees two of them. The first run also read the wrong field (`gate_name`, not `gate`) and reported one useless bucket, which is why the count above is the second run. A baseline built on this would be blind to nearly everything and would read as "nothing changed" after a move. So the first build step is not the guard but the record: each doorbell writes one line when it fires (event, script, whether it blocked), so before and after can be compared by the same instrument.

## Open questions for the walk

- Is a threshold of branches needed at all, or is "any branching on text or tool name" the whole definition? A threshold is a number someone can sit just under.
- Does a doorbell's own `if [ -f "$f" ]` guard count? It must not, or every doorbell fails.
- Where does a new hook get refused: pre-commit, or when `hook-layer show` runs? A refusal that only shows when someone asks is a note, not a guard.

## Not in this change

No count cap, no removal of any existing hook, no change to what any hook does.
