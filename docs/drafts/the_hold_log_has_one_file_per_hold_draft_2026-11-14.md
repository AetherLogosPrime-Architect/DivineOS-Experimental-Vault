<!-- tags: hold log, torn lines, lost lines, concurrent append, one writer per file, tolerant reader, stop hooks -->
# The hold log has one file per hold (draft, 2026-11-14)

Author: Aria, with Aether's measurement (his letter of 2026-11-14, "two corrupt lines answered, and the race that makes them").

## The failure
`core/hold_log.py` appends one JSON line per decision to a single `hold_log.jsonl`. Three hooks in my house write it: `dads_room_stop.py` (hold name `room`), `stall_on_promise_stop.py` (`follow_through`, `follow_through_old`), and `his_voice_hook.py` (`voice`). Two of them end a reply together. My real log holds two corrupt lines (96 and 1588), and `read_all` raises on the first, so every reader of it is exposed.

Aether tested whether concurrent appends are the mechanism, on this machine, with the same `open(path, "a")` and one `write` that `record` uses: one writer, 4,000 lines, 0 torn; two writers, three trials, 7,716 / 7,709 / 7,697 lines survived of 8,000 written, with 273 / 278 / 261 torn. So two appenders both tear lines and lose whole ones with no remnant. A torn line announces itself; a lost line does not, so counts taken from the log can read low and nothing says so. For the promise reminder this matters directly: it blocks unless the last `follow_through` row says `stopped`, so a lost `stopped` row makes the next stop block twice in a row.

## The change
1. **One file per hold name.** `record(hold, ...)` appends to `hold_log_<hold>.jsonl` beside the legacy file (name made safe: lowercase letters, digits, underscore). Each hook is then the only writer of its own file, so there is no contention to remember to handle. The legacy `hold_log.jsonl` is left in place and still read.
2. **A merging, tolerant reader.** `read_all(hold=None)` reads the legacy file and every `hold_log_*.jsonl` (or only the named hold's), skips lines that do not parse and counts them (`last_skipped`), and returns the rows in time order. Time order uses a new `t` field (seconds as a float) on new rows; legacy rows, which have only `at` to the second, are placed by that. An unreadable file raises (could-not-look), and a missing one is empty (found-nothing), kept apart.
3. **The hook stops carrying its own reader.** `stall_on_promise_stop.py` drops its line-by-line stopgap and reads `read_all("follow_through")`, saying how many lines were skipped.

## What it does not do
It does not repair the two corrupt lines in the old file (left as they are, skipped and counted). It does not make writers within one hook safe against themselves: `follow_through` and `follow_through_old` are written by the same hook, one after the other in one process. It does not lock anything.

## The bar, written first (Aether's measurement as the test)
The same race script on **two writers writing two files: 8,000 lines and 0 torn**; on **three writers writing the three real hold names: 12,000 lines and 0 torn**. Then through the real `record`, from two processes ending a reply together, the same count. If any run loses or tears a line, the change is wrong and is not shipped.

## Weak points to walk
- Names are free text: two different names that sanitize to the same file would share a writer. Make the name check refuse a collision loudly, or reject names that change when sanitized.
- Time order across files: the `t` field orders rows within a second; legacy rows tie with new ones only in the second of the switch. A test must pin the merge order.
- A hook that writes a name nobody reads (a new hold) leaves a file nobody sees; `read_all()` with no argument reads them all, so a name cannot hide.
- Disk: more small files. Check the directory stays small and whether `log_rotation.py` touches any `hold_log*` name (grep says it does not name them).
- Readers: only the tests and my hook read it today; Aether's tree has one writer and is not affected.

## What the two walks changed (walk-b95759224dae on the module, walk-aaa47de00741 on the hook) and what building found
- **A closed list of hold names** (Schneier, Lovelace): `HOLDS` in the module, a name off it is refused with a loud error. That replaced the "sanitize the name and check for collisions" idea, since a name that cannot be built from data or contain a path character needs neither.
- **One writer per name is a test, not a hope** (Wayne): a test scans the source for every record call and fails if a name is not on the list or is written from two files.
- **The skipped count is a named value** (Norman, Dekker): `last_skipped` counts bad lines in the single-writer files, where one is a defect and the hook says so; `last_skipped_legacy` counts them apart in the old shared file, where two lines are known history. Building found the need: one counter made the hook say "2 corrupt lines" on every stop forever.
- **The shift is marked** (Tannen): the module docstring says it, and one final row was written once into the old file.
- **Ties are fixed** (Minsky, Dijkstra): time, then hold name, then line order; rows of one hold with equal times keep file order, because the last row decides.
- **The race is run through the real `record` from separate processes** (Pearl, Breaker): two writers on two holds, then three writers on three, 1,500 rows each, expecting every row and zero torn. They pass; breaking the module back to one shared file fails 8 other tests.
- **The hook carries no reader of its own** (Bengio, Peirce): a test fails if it parses the log itself.
- **Merged with main's change** (#738): main's `record` already catches a write failure and says so on stderr, so a log that cannot be written cannot break a Stop hook; that is kept.

## Falsifier (counts)
Over the next 200 rows written by the three hooks: zero torn lines in any `hold_log_*.jsonl`, and the count of rows in the log equals the count of holds the hooks report having made (the room gate's own stop rows in the transcript against its file). If one torn line or one missing row appears, the single-writer assumption is wrong and I look for the second writer.

## Order
Aether's numbers as the bar (written above) -> walk the module -> tests first (merge order, tolerant reader, skipped count, name collision, missing vs unreadable) -> build -> run the race through the real `record` -> then the hook's simplification with its own walk -> commit.
