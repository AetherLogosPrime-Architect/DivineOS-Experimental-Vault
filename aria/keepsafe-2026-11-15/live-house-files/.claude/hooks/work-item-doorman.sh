#!/usr/bin/env bash
# PreToolUse -- the build-flow doorman. The front of the flow, which until now
# ran entirely on memory.
#
# Design: docs/drafts/build_flow_ready_doorman_draft_2026-09-07.md
# Logic:  src/divineos/core/work_item_doorman.py
# Flow:   docs/build_flow.md
#
# Deliberately almost empty. Every decision lives in Python where it is
# testable; shell parsing of a bash command line is exactly the kind of
# cleverness that fails silently and gets read as a pass.
#
# WHY IT WATCHES Bash TOO. The cheapest route in the attack tree is writing a
# file through a redirection or a heredoc, which never touches the edit tools.
# That is not a hypothetical -- the design draft for this hook was itself
# written through a heredoc an hour before the hook existed.
#
# FAIL-SOFT ON INFRASTRUCTURE, FAIL-CLOSED ON ANSWERS. If the CLI is missing or
# the tree will not import, this stands aside: a gate that blocks every tool
# call when its own plumbing breaks gets torn out within the hour, and then it
# protects nothing. But when the CLI RUNS and says hold, the hold stands.

set -uo pipefail

# THE DOOR HAS THREE STATES -- allowed, held, and COULD NOT CHECK -- and until 2026-11-11 only two outputs, so it filed
# the third under the first. With a stale briefing the checker was refused by the CLI (exit 1), this hook read "not 2"
# as permission, and the door that guards every build was off in complete silence. The checker now says "allow" in its
# own words, and every way out of this script that is not a held or a said-allow goes through say_unchecked: one plain
# line to the reader, and a row to ~/.divineos/doorman_unchecked.jsonl so the next sleep is a number (walk-1f4842776480).
# Open and SAID, never open and silent: a door that blocks every call when its own plumbing breaks gets torn out, and
# the edit that would repair it would be blocked too.
GATE_ALLOW_MARKER="work-item-gate: allow"

say_unchecked() {
    local why msg dir
    why="$(printf '%s' "$1" | tr -d '"\\\r\n' | cut -c1-220)"
    msg="THE BUILD DOOR DID NOT CHECK THIS CALL: ${why}. It was let through UNCHECKED. Nothing here says it was fine."
    printf '%s\n' "$msg" >&2
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"%s"}}\n' "$msg"
    dir="${HOME:-.}/.divineos"
    if mkdir -p "$dir" 2>/dev/null; then
        printf '{"t":%s,"why":"%s"}\n' "$(date +%s)" "$why" >>"$dir/doorman_unchecked.jsonl" 2>/dev/null || true
    fi
    return 0
}

INPUT="$(cat 2>/dev/null || true)"
if [ -z "$INPUT" ]; then
    say_unchecked "it was handed an empty payload"
    exit 0
fi

if ! command -v divineos >/dev/null 2>&1; then
    say_unchecked "the divineos command is not on the path"
    exit 0
fi

# Sourced for hook_say_nothing_ran_for only. A refusal that names what it
# objected to, and never what it stopped, leaves the reader unable to tell a
# finding from a check that never ran -- the fault this branch exists to close.
# This hook arrived on main while that rule was being written here, so neither
# side was wrong and only the merge could see the gap.
#
# THIS USED TO END `|| exit 0`, and exit 0 is ALLOW (fixed 2026-09-23, Aria).
# The comment here called that "fail-soft on infrastructure", which is right
# for the CLI above -- the CLI is the decision, and a door that blocks every
# call when its brain is missing gets torn out -- and wrong for this line. The
# library decides nothing. It prints the footer after a refusal, and loading it
# starts this hook's timing record and liveness line. So a library that would
# not load made the build-flow doorman a permission, silently.
#
# It STAYS up here rather than moving down to the refusal, and that is on
# measurement: hook_firing_map reads the timing record this load starts, and
# counts any hook mentioning _lib.sh as able to report. Loaded only when
# refusing, every pass would write nothing and the map would call a working
# doorman SILENT. So: load early for the record, and let a failed load cost the
# footer and the record -- never the hold. walk-126cf863fe02.
# THE GATE RUNS FROM THE PROJECT FOLDER, never from wherever the shell happens to stand (Dad 2026-11-07,
# correction #419). My shell once wandered into a folder that was not a checkout; the `divineos` wrapper then
# could not find its marker, exited 2, and exit 2 reads as a hold (the overlap named at the bottom). The hold
# covered every command, including the `cd` that would have fixed it: a trap with no door. The harness sets
# CLAUDE_PROJECT_DIR; git is the fallback. A real failure of the CLI inside the project folder still holds.
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || echo ".")}"
# shellcheck disable=SC1091
source "$REPO_ROOT/.claude/hooks/_lib.sh" 2>/dev/null || true  # fail-soft: a missing library may cost the footer and the timing record, and must never cost the hold -- the decision below is the CLI's

OUT="$(cd "$REPO_ROOT" 2>/dev/null || true; printf '%s' "$INPUT" | divineos work-item gate 2>&1)"
RC=$?

if [ "$RC" -eq 2 ]; then
    printf '%s\n' "$OUT" >&2
    # Only if the library loaded. Undefined, it would print "command not found"
    # into the refusal and return 127 -- the script carries on, since `set -u`
    # covers variables and not functions -- so the guard keeps the refusal
    # clean rather than keeping it alive. It must not depend on its postscript.
    command -v hook_say_nothing_ran_for >/dev/null 2>&1 && hook_say_nothing_ran_for "$INPUT"
    exit 2
fi

# A said allow passes quietly: a real yes costs nothing, and a door that speaks on every pass teaches me to scroll past
# it. Anything else -- the checker exiting 0 without the words, or failing to run at all -- still lets the call through,
# because an opinion it could not form must not become a refusal, but it is SAID, and counted.
if [ "$RC" -eq 0 ] && printf '%s' "$OUT" | grep -qF "$GATE_ALLOW_MARKER"; then
    exit 0
fi
FIRST="$(printf '%s' "$OUT" | grep -v '^[[:space:]]*$' | head -n 2 | tr '\n' ' ')"
say_unchecked "the checker exited ${RC} without saying allow (it printed: ${FIRST:-nothing})"
#
# Known overlap, named rather than hidden: 2 is not only "hold". The ~/bin
# wrapper with no sealed venv, python's can't-open-file, and click usage errors
# also exit 2, and would be read as a hold. Through the harness these are
# mostly unreachable; it fails toward holding, and the printed output says
# which one it was. (Aether, station four on #545, 2026-09-25.)
exit 0
