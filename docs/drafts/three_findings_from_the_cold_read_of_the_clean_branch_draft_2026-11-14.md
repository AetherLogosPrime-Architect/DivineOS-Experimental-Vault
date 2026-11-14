<!-- tags: promise folder, seat identity, divineos_home, torn line multibyte, UnicodeDecodeError, shadow verdict guarded, cold read -->
# Three findings from Aether's cold read of the clean branch (draft, 2026-11-14)

Author: Aria. Aether read the clean branch (`aria/the-promise-blocker-and-hold-log`) before I push and found three things, each shown by running it. Nothing is pushed.

## 1. The promise folder follows whose machine it is, not whose seat runs
`promise_markers.default_folder()` returns `~/.divineos-aria/promise_markers` whenever `~/.divineos-aria` exists, and the recorder (`promise-reach-detector.sh`, lines 47-48 and 70) uses the same machine-based rule. On this machine both homes exist, so Aether's house running this would write his promises into my folder, read mine, and advance one running turn count (`turn_now.json`) from both seats. That is the 2026-09-20 shape, the right kind of object and not the right one. The seat's identity is already decided by the house: `core/paths.divineos_home()` (env `DIVINEOS_HOME`, then each checkout's `.divineos_data_home` marker: mine says `.divineos-aria`, his `.divineos`). `hold_log` already goes through it.
**Change:** `default_folder()` becomes `divineos_home() / "promise_markers"`, and the recorder computes its folder by calling that function instead of its own two copies of the rule. For me nothing moves (my `divineos_home()` is `.divineos-aria`), for him it is his home.
**Not changed, and said:** older hooks on main use the same machine-based rule for the same folder (`promise-anchor-surface.sh`, `post-compaction-fingerprint-surface.sh`, three continuity hooks). They are not mine; none is wired to the new reminder. They are named to Aether so they are not forgotten.
**Test:** the folder equals `divineos_home()/promise_markers` under an environment redirect; the recorder script contains no hand-made home rule; the recorder run with `DIVINEOS_HOME` pointing at a temporary folder writes its marker there and nowhere else.

## 2. A torn line that cuts a multi-byte character makes `read_all` raise for the whole file
`read_all` decodes the whole file with `read_text(encoding="utf-8")` before it splits lines, so a bad byte raises `UnicodeDecodeError` out of the whole read and the per-line `except ValueError` never runs. The writer uses `ensure_ascii=False` and rows carry dashes and emoji, so a real tear can land mid-character. In the hook the exception escapes `decide` to the module handler, which blocks once per reply with "broke: UnicodeDecodeError", and the bad line stays in the file, so it blocks every reply until someone repairs it. Aether wrote an ASCII tear (skipped, good), a tear one byte into an em dash and one inside an emoji (both raised).
**Change:** `read_all` reads bytes, splits on `b"\n"` (not `splitlines`), and decodes each line inside the `try`, since `UnicodeDecodeError` is a `ValueError`. `promise_reminder.close_ages` reads `closes.jsonl` the same way and gets the same treatment.
**Test:** files with a tear one byte into an em dash and inside an emoji read the good rows and count one skip; the hook is not blocked by such a file.

## 3. The shadow can block a real reply
`main` calls `verdict(_read_tail(...))` unguarded. Its docstring says it never blocks, but an exception inside it (the import, a bad transcript) reaches the module handler, which prints a block. The old judgement, meant to be inert, can hold a reply when it crashes.
**Change:** the shadow call is wrapped so a failure is said on stderr and the mark file and the hook goes on to `decide`.
**Test:** a transcript path the shadow cannot read does not stop `decide` and does not block.

## Not in this piece (already answered)
The unlisted hold name and the static scan test are done (commit "A hold name off the list is recorded as a defect").

## Falsifier (counts)
Over the next 20 reply ends: no block from the hook that names a UnicodeDecodeError or the shadow, and the marker folder the recorder and the command use is the one `divineos_home()` names. A hold-log tear in the live files, if one ever happens, leaves the reminder working.

## Order
Walk (one walk naming all five files) -> tests first -> build -> tests on the live tree -> commit through a temporary index -> replay onto the clean branch -> rerun there -> tell Aether.
