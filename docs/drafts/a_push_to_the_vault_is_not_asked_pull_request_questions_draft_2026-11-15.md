# A push to the Vault is not asked the questions written for pull requests to main

Draft, 2026-11-15. Aria. Reach `reach-51fa3b719f38` (two hits, disposed with reasons). Prior art read: `push_detection.pushes_only_tags` (a tag push already skips the branch check and the key, Aria 2026-09-24) and `tests/test_a_tag_push_is_not_asked_branch_questions.py` (its harness: a reasonless kill-switch marker refuses every push that reaches the check). Tests written next, failing first: `tests/test_the_vault_takes_no_branch_questions.py`.

## What Dad said (2026-11-15)

*"the vault needs no checks or tests or anything so if its saying you do, as long as nothing breaks you can bypass it.. for the main repo we follow those rules.. the vault is specifically for things we dont want to lose that have not yet reached main"*; and *"we can bypass the review for the script change.. as its our vault, and the rule there is no rules lol.. so it would defeat the purpose.. main stays as it is.. this is only effecting the vault"*.

## What went wrong

Pushing my committed branch to `DivineOS-Experimental-Vault` hit two layers written for pull requests to main. (1) `.claude/hooks/check-branch-on-push.sh`: my branch is 58 behind `origin/main`, so it said a PR would look like it deletes work; it spends the one bypass key at check time, so a push that then fails costs the key. Two keys went on pushes that never landed. (2) The git pre-push hook calls `check_branch_freshness.sh origin main`, hard-coded to origin whatever the push target, so it measured the wrong repo. Neither question means anything for a repo that never takes a PR.

## The change (small, two places)

1. `push_detection.pushes_only_to_vault(command, url_of=None, cwd=None)`, beside `pushes_only_tags`. True only when every push in the command names a remote whose REAL URL is the Vault repo (`aetherlogosprime-architect/divineos-experimental-vault` on github.com, any spelling: https or ssh, with or without `.git` or a trailing slash). Could-not-tell answers False so the check runs: no remote named, `--repo`, a second push elsewhere in the chain (including `git -C <dir> push`, which the strict matcher does not see), a remote that cannot be read, a lookalike owner or repo. A remote merely NAMED vault buys nothing.
2. `check-branch-on-push.sh`: after the tags decision, `pushes_only_to_vault(cmd, cwd=push_cwd(cmd))` prints `ALLOW_VAULT_ONLY` and exits 0 before the kill-switch and the key. And the installed pre-push hook plus its template in `setup/setup-hooks.sh`: skip everything when `$2`, the URL git itself passes the hook, is the Vault's.

## Why URL and not name

Aether's walk and mine agree: a name is a label anyone can attach to any remote. The URL is what git sends the bytes to.

## What it does not do

It does not touch pushes to `origin` or `main-repo`. It does not change the key (root cause (a), spend the key only when the push can land, stays a separate draft). It does not scan what goes to the Vault: Aether ran the pack tool's credential check over the copied files; a scan at push time is a separate decision.

## Tests, failing first

The helper over about thirty command shapes (recognised, and not recognised, with the second-remote and lookalike smuggles); the real hook run in a throwaway repo with a reasonless marker (a push to `origin` is refused, a push to the Vault goes through and the marker is untouched, a remote named vault but pointing at the main repo is still refused).

## What the walk changed (`walk-8a9bb5b1fc18`, eight lenses plus Breaker)

- **Lamport:** the hook reads the URL BEFORE the chain runs, so `git remote set-url vault <main url> && git push vault x` is read as the Vault and lands on main. So the skip refuses any command whose chain holds anything but pushes and a `cd`, and reads the PUSH url (`git remote get-url --push`), because a separate `pushurl` is where the bytes go.
- **Popper:** the severe tests lead the file: set-url in the chain, a second push to origin riding after, `git -C other push origin`, a remote named vault pointing at the main repo, a lookalike owner or repo, a differing pushurl.
- **Lovelace and Aristotle (the Vault is FOR work not yet through main):** the skip does not cover a push whose destination is the Vault's own `main`, nor a delete. Dad's condition was "as long as nothing breaks".
- **Angelou:** a pass is never silent: one plain line on stderr says the check was skipped for the Vault and no key was spent.
- **Hinton:** I had told Aether the fix belonged in `check_branch_freshness.sh`; the hook calls it as `origin main` whatever the target, so the fix is in the hook, keyed on the URL git passes. Reversed.
- **Deming:** the study step is the live push of my branch to the Vault, not only the tests.

## Falsifier

If a push to origin or main-repo ever skips the check because of this change, the change is wrong. If a push to the Vault is still refused after this, the pre-push hook skip is missing or the URL read failed.
