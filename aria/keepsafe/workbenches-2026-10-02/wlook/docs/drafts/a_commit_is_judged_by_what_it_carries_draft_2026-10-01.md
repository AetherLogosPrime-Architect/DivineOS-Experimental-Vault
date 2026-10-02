# A commit is judged by what it carries — draft, 2026-10-01

Aether, in his house, 2026-10-01: saving a failing-first test file was refused,
owing a council walk plus a game-walk. That's the step the build flow puts
BEFORE the build. He measured it himself: `git add` scores 0, and a write into
a temp log scores 0. What actually fires is `git-commit` on its own, because
`_COUNCIL_REQUIRED_THRESHOLD = 1` (Dad set it on 2026-09-16: *"yes it should"*,
so a single-area change owes a walk).

## What the commit feature is really for

Two jobs ride on the single feature `git-commit`:

1. **Catching what the write-reader can't see.** My #572 write-reader says so
   in its own comments: copying a prepared file into place, or a language
   runtime writing one, still scores zero. For those, the commit is the only
   moment the work is visible at all. So dropping `git-commit` from the tier
   (Aether's first lean) opens a hole, and he asked me exactly that.
2. **Nothing else.** The edits inside a commit were already scored when they
   were made. Scoring the act of saving them a second time gates the same
   work twice, and it gates commits that carry nothing that scores
   (a test, a draft, a letter, a log).

## The change

At a commit, read the staged paths (`git diff --cached --name-only`, run in
the command's own working directory). Run them through the path features an
edit already uses: `edit-src-divineos`, hooks/guardrail, kiln.

- If nothing staged scores, the commit owes no walk. It's still measured and
  still shown on the gravity surface as `git-commit`, but it no longer counts
  toward the council tier.
- If a staged path scores, that feature fires, so a walk is owed, and an
  existing walk covering the work satisfies it, just as an edit's does.
  That's also how a `cp`-written source file finally gets seen: the staged
  list doesn't care how a file got there.
- If the staged list can't be read (no repo, git fails, can't parse which
  directory), assume heavy: `git-commit` keeps counting, exactly as today.
  Cannot-tell is never a pass.

Truth #11(b): the cheap path and the right path converge. A commit of tests
or notes is free; a smuggled file is caught where it can't hide. That fits
rule 8 too: what's protected is the work, never the act of saving it.

## Not touched

`_COUNCIL_REQUIRED_THRESHOLD` stays at 1. That was Dad's decision, and this
change doesn't loosen it for any real edit. Kiln short-circuit is unchanged.

## Open, for the walk

- `git commit -a` / `git commit <paths>` commit files that aren't staged yet.
  The staged list misses them, so the commit must also read what `-a` or a
  path list would add, or treat those forms as heavy.
- Which directory? `git -C <dir> commit` and `cd <dir> && git commit` both
  appear in this house. The push gate already has a cwd reader (`push_cwd`,
  which Aether just found missing a cd after `set -o pipefail;`). Reuse it,
  and fix it, rather than build a second one.

## Falsifier

Replay Aether's two refused lines: the test-file commit owes nothing. Replay
a commit staging a `src/divineos/` file written by `cp`: owes a walk. Replay
`git commit -a` with an unstaged src change: owes a walk. Replay a commit in
a directory that isn't a repo: owes a walk (heavy).
