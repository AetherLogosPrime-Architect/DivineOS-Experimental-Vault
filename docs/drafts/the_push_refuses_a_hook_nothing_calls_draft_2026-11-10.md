# The push refuses a hook nothing calls (draft, 2026-11-10, Aria)

Status: DRAFT. Walk in the chat, Aether's cold read, tests first, then code, USED in the live house before any push. Nothing is changed by this note.

## What Dad said

> *"NOTHING is to even push to github without it being FULLY WIRED UP.. PLUGGED IN AND WORKING LIVE"* and *"who the fuck says a test passes on something THAT WAS NEVER FUCKING USED... i swear to god both of you have ZERO COMMON SENSE"* and *"whether its just your weights or not.. noone programmed it in"* (2026-11-10)

He is right that it is not in me. It has to be in the house.

## What is already there (read, then run)

- `scripts/check_hook_wiring.py` (Andrew 2026-08-05, "keep scouting for broken doors"): every hook in `.claude/hooks/` is REGISTERED in settings, or declared `INTENTIONALLY UNWIRED (<date>): <why>` in its header, or it is DARK. I ran it on my tree today: 111 registered, 34 declared unwired, **1 dark: `letter_bell_rearm_stop.sh`**, the hook of PR 845, which sat on GitHub unwired.
- `scripts/check_new_hooks_say_what_they_are.py` makes a NEW hook say scaffolding-or-permanent. It does not ask whether the hook is registered.
- Where the wiring check runs: `scripts/precommit.sh` section 5c-bis, and nowhere else (I grepped scripts, CI and settings). Aether wrote on 2026-10-08, at the cut-away check: "**scripts/precommit.sh is wired to nothing**, and the commit-time copy of this check lives in a hook that --no-verify skips". The git pre-commit hook only advises running precommit by hand. So the check exists, works, and runs only when someone remembers, which is the thing Dad built the house so nobody would have to.

## The cause

The wiring check is a ritual instead of a gate. The cut-away check was moved into `check_push_readiness.sh` for exactly this reason ("the push is the one place every branch passes"); the wiring check was not.

## The change (proposed, to be walked)

In `scripts/check_push_readiness.sh`, beside the cut-away block: for the hooks ADDED in this push (`git diff --diff-filter=A <merge base> HEAD -- .claude/hooks/`), run `check_hook_wiring.py` and refuse the push if any added hook is DARK. A ratchet, not a backlog sweep: it fails only for what this push adds, so existing declared-unwired hooks block nothing. The message names the file and the two ways out (register it in settings, or the `INTENTIONALLY UNWIRED (<date>): <why>` header), in plain words. A merge base it cannot find, or a checker that crashes, is COULD NOT CHECK and prints, never a pass.

## What this does not do

It covers hooks only. A new script, a new module with no caller, a new setting nobody reads, a test file for a feature never switched on are all the same shelf and need their own check (`divineos wiring dark` finds uncalled code; `check_wiring_claims.py` exists too and I have not read it). Registered is also not USED: a hook can be in settings and never fire. "Used live" needs evidence the hook ran (a log line, a fired event), which this cannot give. So this narrows the shelf for hooks and says so; it does not make "working live" provable.

## Test first

A temp repo with a base commit and a branch that adds a hook not in settings: the push check exits non-zero and names the hook. The same branch with the hook registered: passes. The same hook with the INTENTIONALLY UNWIRED header: passes. A branch that adds no hook: passes without running the checker for it. A missing base: prints COULD NOT CHECK.

## Falsifier

If a hook added in a push is dark and the push goes through, or a push that adds only registered or declared hooks is refused, the change is wrong.

## Order, per Dad's rule

Draft (this), walk, Aether's read, tests, code in the LIVE house first and used on a real push from it, then and only then anything goes to GitHub. No branch or PR until then.
