#!/bin/bash
# Stop hook — scan last assistant reply for promise-shape phrases and
# write one marker file per detected promise.
#
# WHY THIS EXISTS (Aria + Andrew 2026-07-18):
#
# Andrew's correction #6 (2026-07-05, 4+ recurrences since): the
# announcement-of-action-without-action pattern. I say "I'll do Y" and
# then never do Y and never name it as unfulfilled. Silent aging.
#
# Fix shape (Angelou/Beer/Meadows lenses, council-cafe612b8ac1):
# same event-shape as visrama and no-cliff anchors. Detector at Stop
# writes marker files; UserPromptSubmit surface reads unclosed markers
# at next composition boundary and shows each specific promise text.
#
# Prereg: prereg-2de5a9ca234a. Falsifier at 30 days: 3+ instances where
# I fulfill/defer/dismiss a surfaced promise OR the surface is wallpaper.
#
# Fail-open: any error exits 0 silently.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
cd "$REPO_ROOT" || exit 0

# shellcheck disable=SC1091
source "$REPO_ROOT/.claude/hooks/_lib.sh" 2>/dev/null || exit 0
PYTHON_BIN="$(find_divineos_python)" || exit 0

# Read the Stop hook stdin — the harness delivers transcript context here.
INPUT=$(cat)

# Extract the transcript_path from the JSON input (fail-open if missing).
TRANSCRIPT_PATH=$(echo "$INPUT" | "$PYTHON_BIN" -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('transcript_path', ''))
except (json.JSONDecodeError, ValueError):
    print('')
" 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    exit 0
fi

# Marker directory. Per-agent data-home so aria markers don't collide
# with aether's if both run in the same repo.
MARKER_DIR="$HOME/.divineos-aria/promise_markers"
[ -d "$HOME/.divineos-aria" ] || MARKER_DIR="$HOME/.divineos/promise_markers"

mkdir -p "$MARKER_DIR" 2>/dev/null

ERR=$(PYTHONIOENCODING=utf-8 "$PYTHON_BIN" -c "
import sys
import json
import time
import hashlib
import os
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, OSError) as exc:
    print(f'promise recorder: could not set utf-8 output: {type(exc).__name__}: {exc}', file=sys.stderr)

TRANSCRIPT_PATH = r'''$TRANSCRIPT_PATH'''
# The marker folder is worked out HERE, from the home folder this Python sees. It used to be handed over from
# bash as /c/Users/... which Windows Python reads as C:\\c\\Users\\..., a folder that does not exist: every
# write failed and was swallowed, and the recorder wrote nothing from July to 2026-11-13.
_home = Path(os.path.expanduser('~'))
MARKER_DIR = _home / ('.divineos-aria' if (_home / '.divineos-aria').is_dir() else '.divineos') / 'promise_markers'
MARKER_DIR.mkdir(parents=True, exist_ok=True)
BROKE_MARK = _home / '.divineos' / 'promise_recorder_broke.txt'

try:
    from divineos.core.operating_loop.promise_reach_detector import (
        detect_promise_reach,
    )
except ImportError as exc:
    print(f'promise recorder: cannot import the detector, so nothing is recorded: {exc}', file=sys.stderr)
    sys.exit(0)

# Read last assistant reply from transcript (JSONL, last non-empty
# assistant message with 'text' content).
last_reply_text = ''
_bad_lines = 0
_turns = 0
try:
    from divineos.core.his_message import UNKNOWN as _UNKNOWN, opener_kind as _opener_kind
except ImportError as exc:
    # Markers are then written undated (no turn_index), never not at all, and the reason is kept.
    _opener_kind, _UNKNOWN = None, None
    print(f'promise recorder: cannot count turns, markers will be undated: {exc}', file=sys.stderr)
try:
    with open(TRANSCRIPT_PATH, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                _bad_lines += 1
                continue
            # Counted as we go, never stored: a transcript can be hundreds of MB and a list of every record would
            # hold all of it in memory. This is promise_markers.turn_index done one record at a time.
            if _opener_kind is not None and _opener_kind(rec) != _UNKNOWN:
                _turns += 1
            msg = rec.get('message', {})
            if not isinstance(msg, dict):
                continue
            if msg.get('role') != 'assistant':
                continue
            content = msg.get('content', [])
            if isinstance(content, list):
                parts = []
                for c in content:
                    if isinstance(c, dict) and c.get('type') == 'text':
                        parts.append(c.get('text', ''))
                if parts:
                    last_reply_text = chr(10).join(parts)
            elif isinstance(content, str):
                last_reply_text = content
except OSError as exc:
    print(f'promise recorder: could not read the transcript {TRANSCRIPT_PATH}: {type(exc).__name__}: {exc}', file=sys.stderr)
    sys.exit(0)

if _bad_lines:
    print(f'promise recorder: {_bad_lines} transcript line(s) were not readable JSON and were skipped', file=sys.stderr)

# The ONE running turn count, advanced at EVERY Stop, promise or not, so a command and the later blocker can read
# how old a promise is without opening a 367 MB transcript. It continues across sessions (a new transcript
# restarts at zero; the count does not), and a clock that cannot be read is said, never guessed.
_global_turn = None
if _opener_kind is not None:
    try:
        from divineos.core.promise_markers import advance_turn_now
        _global_turn = advance_turn_now(MARKER_DIR, os.path.basename(TRANSCRIPT_PATH), _turns)
    except (ImportError, OSError, ValueError) as exc:
        print(f'promise recorder: the turn clock could not move, markers will be undated: {exc}', file=sys.stderr)

if not last_reply_text.strip():
    sys.exit(0)

findings = detect_promise_reach(last_reply_text)
if not findings:
    sys.exit(0)

# Write one marker per finding. Filename encodes shape + hash so
# duplicate detections across turns don't stack.
now = time.time()
for f in findings:
    key = hashlib.sha256(f.promise_text.encode('utf-8', errors='replace')).hexdigest()[:16]
    marker_path = MARKER_DIR / f'promise_{f.shape.value}_{key}.json'
    if marker_path.exists():
        # Already tracked and still open: keep it (preserve the original turn and moment). But a CLOSED marker
        # with the same words must not swallow a new promise made later, so that gets its own marker.
        try:
            _was_closed = bool(json.loads(marker_path.read_text(encoding='utf-8')).get('closed'))
        except (OSError, ValueError):
            _was_closed = False
        if not _was_closed:
            continue
        marker_path = MARKER_DIR / f'promise_{f.shape.value}_{key}_t{_turns}.json'
        if marker_path.exists():
            continue
    payload = {
        'shape': f.shape.value,
        'trigger_phrase': f.trigger_phrase,
        'promise_text': f.promise_text,
        'detected_at_ts': now,
        'detected_at_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
    }
    # The turn it was made in (a turn start is counted by the harness's own stamp, zero included). Only when
    # the counter could be loaded; otherwise the marker stays undated and the reason is already on stderr.
    if _global_turn is not None:
        payload['turn_index'] = _global_turn
        if _bad_lines:
            payload['turn_uncertain'] = _bad_lines
    try:
        with open(marker_path, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        # Loud, not silent: a failed write was the whole of the months-long outage.
        try:
            BROKE_MARK.parent.mkdir(parents=True, exist_ok=True)
            BROKE_MARK.write_text(f'promise recorder could not write {marker_path}: {type(exc).__name__}: {exc}' + chr(10), encoding='utf-8')
        except OSError:
            pass
        continue
" 2>&1)
# Whatever the recorder said on stderr is KEPT, never thrown away (it used to go to /dev/null, which is how a
# months-long outage stayed invisible). Nothing printed means it ran clean.
if [ -n "$ERR" ]; then
    mkdir -p "$HOME/.divineos" 2>/dev/null
    printf '%s\n' "$ERR" > "$HOME/.divineos/promise_recorder_broke.txt" 2>/dev/null
fi

exit 0
