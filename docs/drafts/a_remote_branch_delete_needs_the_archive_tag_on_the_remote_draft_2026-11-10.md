# A remote branch is deleted only when its tip is already tagged on the remote (draft, 2026-11-10, Aria)

## Why (his words, and the audit that found it)

Dad 2026-11-10: "go look properly". The notes audit read all 219 of my memory notes against the real house; `branch-removal-is-andrews-hand` came back PARTIAL. The note's rule: removing old remote branches is my own job, done by tagging the tip as an archive tag, verifying the tag is on the remote, and only then deleting; a refusal from the permission layer is a tool block, not Dad's rule, and I never add a bypass. What exists: `core/deletion_discipline.py` line 43 matches `git push --delete` (and `git push origin :branch`) and demands a delete-justify. What is missing, said by the helper and confirmed by my own read of the file: nothing checks that an archive tag exists on the remote at the same tip before the delete goes through. (Searched `docs/drafts` for an earlier draft of this: only `the_override_is_a_button_draft_2026-09-30.md` mentions push --delete, and it is about overrides, not this.)

## What the check does (an ACTION and a FACT, never words)

When the command is a remote branch delete (the existing match), read the branch name and ask the remote two questions: what commit is the branch tip, and is there any tag on the remote pointing at that commit. If a tag exists at the same commit: pass silently. If none: refuse, naming the tip and the one command that makes the tag. If the remote cannot be asked (offline, no access): say so loudly, never read it as "tag exists". Four states kept apart: not a delete (silent), tag found (pass), no tag (refuse with the fix), could not ask (refuse and say why).

## What it does not do

It does not judge whether the branch should be deleted; the delete-justify gate still does that. It does not create the tag for me (that is my act, one command). It does not look at local branch deletes.

## Falsifier

On a real throwaway branch pushed to the remote: delete it with no tag, the check refuses; tag the tip, push the tag, delete again, it passes. If the first passes or the second refuses, the check is wrong. The real remote is used, not a stub.

## Keyword check on my own design

None. The trigger is a git command's shape (already in the door) and the decision is a fact read from the remote.

## Order

This draft, then the recorded walk with `--scope` per file (core/deletion_discipline.py, its test, this draft), then build, test against a real throwaway branch, then it runs live. No new branch or pull request until the existing pile is finished.
