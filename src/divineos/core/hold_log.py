"""A record of each time a hold stopped a reply or let one pass: one file per hold, so no two hooks share a file.

Walk walk-83a5483f0504 (Holmes, Maturana_Varela): a passing room and a real room leave the same trace, which is
none, so nothing could be read back later. This keeps one line per decision with the first words of what was
checked beside it, for Dad and the siblings to read and judge. Nothing here grades or refuses on content, and
nothing reads the log to decide anything except a hook reading its own rows: it is a record, not a gate.

ONE FILE PER HOLD (walk-b95759224dae, 2026-11-14). Two hooks that end a reply together appended to one file and
tore and lost lines: Aether measured two writers on one file losing about 4% of 8,000 rows and tearing about 3%,
while one writer lost none, and my real log held two corrupt lines. Each hold now writes only
`hold_log_<hold>.jsonl`, so each hook is the only writer of its own file and there is no contention to remember to
handle. Hold names are a CLOSED list (`HOLDS`): a name outside it is refused loudly, which also rules out a name
with path characters or a name built from data. A new hold is a one-line edit here.
THE SHIFT, said where anyone tailing the old file will see it: `hold_log.jsonl` no longer grows. It is still read,
so no history is lost, and the holds are in `hold_log_<hold>.jsonl` beside it.

READING. `read_all(hold=None)` merges the old file and the per-hold files in time order (ties: time, then hold name,
then line order), skips lines that do not parse, and sets `last_skipped` to how many it skipped, so a reader can
say so and a torn line is never routine. A missing file is empty (found-nothing); a file that cannot be read raises
(could-not-look). The two are kept apart.
"""

from __future__ import annotations

import calendar
import json
import sys
import time
from pathlib import Path

#: How much of the checked text is kept: enough to recognise the reply, not to store it.
_FIRST_WORDS = 160

#: The holds that write here. A name outside this list is refused (Schneier, Lovelace).
HOLDS = ("room", "voice", "follow_through", "follow_through_old")

#: How many lines the last `read_all` skipped because they did not parse, in the per-hold files. Each of those has
#: ONE writer, so a skipped line there is a defect and must be said.
last_skipped = 0

#: The same count for the OLD shared file, where two writers tore lines before this change. Kept apart so the known
#: corrupt lines in history are neither hidden nor a standing alarm.
last_skipped_legacy = 0


def _log_path() -> Path:
    """The OLD single file. It no longer grows; it is still read, and the per-hold files sit beside it."""
    from divineos.core.paths import divineos_home

    return divineos_home() / "hold_log.jsonl"


def _path_for(hold: str) -> Path:
    if hold not in HOLDS:
        raise ValueError(
            f"hold {hold!r} is not on the list ({', '.join(HOLDS)}); add it to HOLDS in hold_log.py"
        )
    return _log_path().with_name(f"hold_log_{hold}.jsonl")


def record(hold: str, outcome: str, checked_text: str) -> None:
    """Append one line to this hold's own file. `hold` is one of HOLDS; `outcome` says what the hold did."""
    path = _path_for(hold)  # a name off the list raises: a programmer error is loud, in tests first
    line = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "t": time.time(),
        "hold": hold,
        "outcome": outcome,
        "first_words": " ".join(checked_text.split())[:_FIRST_WORDS],
    }
    # A record, not a gate (docstring above): a log that cannot be written must not change or cancel the hold
    # decision the hook is in the middle of making (Aether on #738: a write failure inside the Stop hook could
    # break the turn). It says so on stderr, so the failure is loud and the hold still holds.
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(
            f"[hold_log] could not write the record ({type(exc).__name__}: {exc})", file=sys.stderr
        )


def _when(row: dict) -> float:
    """A row's time: the float `t` new rows carry, else the old rows' `at` (whole seconds), else 0."""
    t = row.get("t")
    if isinstance(t, (int, float)) and not isinstance(t, bool):
        return float(t)
    try:
        return float(calendar.timegm(time.strptime(str(row.get("at")), "%Y-%m-%dT%H:%M:%SZ")))
    except ValueError:
        return 0.0


def read_all(hold: str | None = None) -> list[dict]:
    """Every row (or one hold's rows) from the old file and the per-hold files, in time order.

    Lines that do not parse are skipped and counted in `last_skipped`. A missing file is empty; a file that exists
    but cannot be read raises.
    """
    global last_skipped, last_skipped_legacy
    legacy = _log_path()
    paths = [legacy]
    paths += [_path_for(hold)] if hold else sorted(legacy.parent.glob("hold_log_*.jsonl"))
    rows: list[tuple[float, str, int, dict]] = []
    skipped = skipped_old = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        for number, line in enumerate(text.splitlines()):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError("not an object")
            except ValueError:
                if path == legacy:
                    skipped_old += 1
                else:
                    skipped += 1
                continue
            if hold and row.get("hold") != hold:
                continue
            rows.append((_when(row), str(row.get("hold", "")), number, row))
    last_skipped, last_skipped_legacy = skipped, skipped_old
    rows.sort(key=lambda item: item[:3])
    return [row for *_, row in rows]
