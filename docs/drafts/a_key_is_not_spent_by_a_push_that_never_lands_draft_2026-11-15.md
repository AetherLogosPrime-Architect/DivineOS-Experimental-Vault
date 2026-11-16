# A key is not spent by a push that never lands

Draft, 2026-11-15. Aria. Reach `reach-2eb204e57d39`. Prior art read: `docs/drafts/the_override_is_a_button_draft_2026-09-30.md` (Dad's one-key design: spent on use, back only for a fix proven in action), `src/divineos/core/bypass_key.py` (the key lives in the hash-chained ledger, spend and return are events, no file to edit), `.claude/hooks/check-branch-on-push.sh` (the spend, lines about 202 to 226), and the live post-push hook `verify-push-landed.sh`. Tests first: `tests/test_a_key_is_not_spent_by_a_push_that_never_lands.py`.

## What Dad said

2026-11-15: *"a failed bypass should never waste your key.. so you have my permission for another one, but that also needs fixed later as well, otherwise you would be stuck like chuck lol"*. And on 2026-09-30 the key's whole point: *"if you lose your key, dont fix the issue, end up in another deadlock with no key and need my permission to bypass? then that means you gamed the bypass somewhere"*. Both are true; the second assumes a lost key meant a USED key.

## What went wrong, measured today

The gate spends the key at CHECK time (`bk.spend` in the PreToolUse hook), before the push has run. So a push that then fails for any other reason costs the key: twice today. (1) the push named a remote that did not exist yet; (2) it passed this gate and a second check inside git's pre-push hook stopped it. Nothing looked at whether the push landed. After the second, I was stuck; Dad's chat word could not reach a ledger-held key, so I appended an honest `BYPASS_KEY_RETURNED` entry quoting his words by hand, which is exactly the move the design exists to make unnecessary.

## The change

A post-push hook asks one mechanical question and acts only on a clear answer: **did what this push said it would send actually land?** For the spent push's remote and each named refspec, compare the local source sha with `git ls-remote <remote> <dest>`.

- **Every ref landed:** the key stays spent. It was used. The fix owed for the lock it opened is the usual one.
- **Every ref answers "not landed":** the key is refunded: a `BYPASS_KEY_RETURNED` event whose payload says `refund: "the push did not land"`, with the remote, destination and both shas as evidence. It was never used.
- **Anything else** (a bare push with no named ref, `ls-remote` unreachable, some refs landed and some not, a command that is not the spent push): the key stays spent, because could-not-tell must never mint a key.

## What it deliberately does not do

- It does not read the exit code. Exit codes lie in the way correction #227 recorded (a trailing echo's 0 read as git's). The remote's own answer is the evidence.
- It does not refund when ANYTHING landed.
- It does not touch the one-key rule or `note_clean_pass`; a used key still returns only for a merged fix.
- It does not let a pushed-then-reverted ref pass for a failed push: the check runs right after the command, only for the spent fingerprint, within a short window.

## Gaming check

A push that lands cannot be refunded (the remote says so). A push made to fail gets the key back but gained nothing from the bypass. A command with a second clause (`git push ... ; exit 1`) does not match the spent fingerprint and is not refunded; the refund compares the same push segment the spend recorded.

## Dad's change, same evening: an unclear answer returns the key too

I had written that anything unclear leaves the key spent, because could-not-tell must never mint a key. Dad, 2026-11-15: *"an unclear answer should return the key as well so you can try something else, otherwise you are stuck in the same boat.. no key and no answers"*. He is right that a seat with a spent key and no clear answer is the same deadlock the fix exists to remove.

So doubt returns the key, **once per unrepaired lock**: a `BYPASS_KEY_REFUNDED` event with `on_doubt: true`. The guard is not distrust; it is his own rule (a lost key and a second deadlock means the bypass was gamed). A bare `git push` that LANDED also reads as unclear, so doubt alone must not be free forever. A `RETURNED` event, which only a merged fix earns, starts the count again. A clear yes still keeps the key spent even beside an unclear ref; a clear no is a refund that does not use up the doubt allowance. The hook says which it was in one plain line.

## What the walk changed (`walk-5195f6e0680e`, nine lenses plus Breaker)

- **A refund is its own event type, `BYPASS_KEY_REFUNDED`, not `BYPASS_KEY_RETURNED`** (Tannen, framing). A RETURNED means "you repaired the lock"; a refund means "it was never used". One type would let a later reader take a refund for a repair. `status()` counts the new type as held and the briefing can name it separately. This replaces the payload field in the section above.
- **Bound by name to the one gate whose key is spent on a push, `check-branch-on-push`** (Lovelace); any other gate is refused.
- **At most once per spend** (Lamport): the refund event after a SPENT makes the key held, so a second call finds no spend to refund.
- **Every slot defaults to unknown, and unknown stays spent** (Minsky): remote, destination, local sha, remote sha, landed. Only "the remote answered, and for EVERY named ref its sha is not the one we sent" refunds.
- **Never the exit code, always the remote's own answer** (Hinton, correction #227). A pipe to `tail` hides git's exit code anyway.
- **Automatic, not remembered** (Bengio): a PostToolUse hook that fires on its own, registered in `settings.json`, with a test that the registered command string is the one that runs.
- **Severe tests lead** (Popper): a landed push keeps the key spent; two refspecs with one landed; "Everything up-to-date"; an unreachable remote; a bare push; a short ref name and a tag against a head.
- **The refund line is plain** (Angelou): it names the evidence and says the key is back and was never used.

## Tests, failing first

`refund_if_not_landed` over a real local bare repo as the remote: push lands, key stays spent; push rejected (non-fast-forward), key refunded; a remote that does not exist, key refunded; bare `git push`, stays spent; unreachable remote, stays spent; two refspecs with one landed, stays spent; a different command, stays spent; no key spent, nothing to refund; a refund restores `held`; and the real post hook run for real.

## Falsifier

A refunded key whose push in fact reached the remote. Or a key still spent after a push the remote never received.
