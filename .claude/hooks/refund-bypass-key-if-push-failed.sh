#!/bin/bash
# refund-bypass-key-if-push-failed.sh -- PostToolUse(Bash): a key is not spent by a push that never lands.
#
# MINE, and here is why. check-branch-on-push spends the one bypass key at CHECK time, before the push has
# run. A push stopped by anything else (a remote that was never added, a second check inside git's own
# pre-push hook, the network) cost the key twice in one afternoon, 2026-11-15, and Dad said: "a failed
# bypass should never waste your key". This hook runs after every Bash command, asks the REMOTE whether
# what was pushed landed (core/bypass_key.refund_if_not_landed), and gives the key back only on a clear
# "no" for every named ref. It never reads the exit code (correction #227). It never blocks anything:
# every failure here is silent and leaves the key spent, because could-not-tell must never mint a key.
# walk-5195f6e0680e; draft docs/drafts/a_key_is_not_spent_by_a_push_that_never_lands_draft_2026-11-15.md.

set +e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -z "$REPO_ROOT" ] && exit 0
cd "$REPO_ROOT" || exit 0

INPUT=$(cat)

# shellcheck disable=SC1091
source "$REPO_ROOT/.claude/hooks/_lib.sh" 2>/dev/null || exit 0
PYTHON_BIN="$(find_divineos_python)" || exit 0

printf '%s' "$INPUT" | "$PYTHON_BIN" -c "
import json, sys
try:
    data = json.loads(sys.stdin.read() or '{}')
    cmd = (data.get('tool_input') or {}).get('command', '') or ''
    from divineos.core.push_detection import is_git_push_command, push_cwd
    if not cmd or not is_git_push_command(cmd):
        sys.exit(0)
    from divineos.core import bypass_key as bk
    result = bk.refund_if_not_landed(bk.REFUND_GATE, cmd, cwd=push_cwd(cmd))
    if result == 'refunded':
        print(
            '[bypass-key] that push did not land, so your bypass key is back: it was never used. '
            '(The remote was asked, not the exit code.)',
            file=sys.stderr,
        )
except Exception:
    sys.exit(0)
" 2>/dev/null

exit 0
