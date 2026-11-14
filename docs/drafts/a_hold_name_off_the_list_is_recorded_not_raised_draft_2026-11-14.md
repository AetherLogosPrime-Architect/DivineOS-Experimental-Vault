<!-- tags: hold log, closed list, unlisted hold name, Stop hook crash, record raises, one file per hold -->
# A hold name off the list is recorded, not raised (draft, 2026-11-14)

Author: Aria, from Aether's cold read of `core/hold_log.py` (his letter, "cold read of your hold_log, one path and one crash"). Builds on [the hold log has one file per hold](the_hold_log_has_one_file_per_hold_draft_2026-11-14.md).

## The failure
`record` calls `_path_for(hold)` before its `try`, and that raises `ValueError` for a name off the closed list `HOLDS`. `except OSError` does not catch it either. So a new hook that calls `record("something_new", ...)` before the list has the name crashes inside a Stop hook, which is exactly what main's #738 exists to prevent (a write failure inside a Stop hook must not break the turn). Today every caller uses a listed name, so nothing breaks; it breaks the first hold someone adds in a hurry, and then it breaks a reply.

## The change
1. `record` no longer raises for an unlisted name. It says so on stderr, and writes the row to a fixed file, `hold_log_unlisted.jsonl`, with the offered name stored inside the row (`offered`). No path is built from data, and nothing is lost.
2. The loudness moves to a test: the existing scan of every `record("...")` literal in `.claude/hooks` and `src` already asserts each is on `HOLDS`; it stays, so a new hold breaks a test run and not a reply.
3. `read_all()` with no hold reads the unlisted file too (it matches `hold_log_*.jsonl`), so unlisted rows cannot hide. `read_all("unlisted")` is allowed.
4. The module docstring says what one file per hold does and does not do: it removes the contention between DIFFERENT hooks, not between two copies of one hook. `his_voice_hook` is wired on every tool call (`PreToolUse`, matcher `*`), so several copies can run at once and can append to `hold_log_voice.jsonl` together; nothing decides from voice rows except a test, so the worst case is one torn or lost row, said, not built around.

## What it does not change
The closed list, the one-file-per-hold layout, the merge order, the skipped counts, main's catch of a write failure.

## Weak points to walk
- The old test asserted a `ValueError` for an off-list name. It becomes: no exception, a stderr line naming the offered name, a row in the unlisted file with `offered` set, and a name with path characters writes nowhere but that fixed file.
- An unlisted row is a defect and must not become routine: `read_all` sets `last_unlisted`, the count of rows in that file, so a reader can say it.
- A name that is not a string (None, a number): store its `repr` in `offered`, still one fixed file.
- Writing the unlisted row can itself fail (disk): the same OSError catch applies and says so.

## What the walk changed (walk-57dcc761cdbd, nine lenses)
- **`record` returns the path it wrote, or None when it could not write** (Hoare), so a caller or a test can tell found, unlisted and could-not-write apart.
- **The `last_unlisted` counter is dropped** (Taleb, via negativa): the fixed file is the one addition worth keeping; a reader wanting a count reads rows whose hold is `unlisted`.
- **The same OSError catch covers the unlisted write and its stderr line** (Watts): the change must not be able to crash for the reasons it exists to prevent.
- **The offered name is stored as its repr cut to 80 characters** (Schneier), so a huge or hostile name costs one short row in one fixed file.
- **The stderr line starts with `DEFECT`** (Yudkowsky), and the docstring says an unlisted row is never a place a hold lives.
- **Outcome and text are coerced with `str`** (Dijkstra): the invariant is that `record` never raises into a hook for any input; the text was the other hole, the same crash class.
- **Boundaries are test cases** (Knuth): empty, None, a number, an unhashable list, a 500-character name, path characters, capital letters.
- **A real subprocess test** (Breaker): the real `record` with an unlisted name exits 0, names the offered name on stderr, and leaves one row in the one fixed file.
- **Constants instead of string literals in the hooks would build the quality in** (Deming); the scan test only inspects after the fact. Deferred, with its reason: three more hook files and their walks for a small gain, and the falsifier counts unlisted rows.

## Falsifier (counts)
Over the next 200 rows written by real hooks: none in `hold_log_unlisted.jsonl`, and every hold name in the source on the list. A row in the unlisted file is a defect to read the same day.

## Order
Walk -> tests first (no raise, stderr, fixed file, offered name, non-string, read_all sees it, last_unlisted) -> build -> run the hold-log tests and the race bar again -> commit on both the live branch and the clean branch.
