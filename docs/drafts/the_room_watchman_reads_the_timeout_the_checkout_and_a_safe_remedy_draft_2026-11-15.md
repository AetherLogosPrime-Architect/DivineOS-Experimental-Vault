# The room watchman reads the timeout, the checkout, and prints a safe remedy (draft, 2026-11-15, Aria)

Status: draft. Nothing built. Walk and failing tests come next. This is PR 768's third slice, after `a05441759` (disableAllHooks and "his decision only with his words"). The second reader's note is 783; Aether read the same note against his 769 and confirmed my three open items (his letter 562).

## What the room watchman is

`src/divineos/core/room_state.py` checks at session start whether the circle room (`dads_room_stop.py`, wired in `.claude/settings.json`) is really plugged in, by running its wired commands and reading settings. It reports when something is false and exits 0, so a session still starts.

## The three open holes (read in my local head `a05441759`)

1. **A settings `timeout` of 1 on the room entry is not read.** `_blocks` runs the commands with a 30 second limit (`timeout=30`, line 124), but never reads the `timeout` value in the settings entry. The harness would cut the room off after one second while the watchman calls it wired.
2. **No checkout identity.** Nothing records which repository root a "his decision" marker belongs to, so one decision silences another checkout on the same user.
3. **The remedy is `git checkout origin/main -- .claude/hooks/dads_room_stop.py .claude/settings.json`** (line 47). If `origin/main` carries the unplugged file, the remedy restores the unplugged file.

## The change (three small parts, each with a failing test first)

1. Read the room entry's `timeout` from settings and report the room as unwired when it is below a floor that gives the hook time to run (the hook's own measured p95, rounded up), saying what it read and what it needs.
2. Record the repository root (resolved, normalised) in the decision marker when it is written and compare it when it is read; a marker from a different root does not count.
3. Make the remedy name a verified source: the file as it is at the last commit that had the room wired, found by asking git for the last commit whose `settings.json` has the room entry, not by trusting a branch name.

## What the tool decides, and what stays mine

The watchman decides whether the room is plugged in, by reading wiring and running the hook, and it never blocks a session. Whether a removal was Dad's decision stays with Dad: the marker counts only with his words and a time, and now only in the checkout it was written in. Whose will it carries: Dad's order that the circle is never unplugged quietly. What it cannot see: a removal that leaves every file and setting intact but changes what the hook does (Aether's note on `his_room.py`).

## What ends it

If the room becomes automated into the harness so it cannot be switched off from a settings file, the watchman has nothing to read and is retired.

## What would show it failed

- A room entry with `timeout: 1` still reads as wired.
- A decision marker written in one checkout silences the report in another.
- The remedy it prints restores a file that does not have the room wired.

## Limits

This does not close the routes Aether named as open on 769 (`git reset --hard`, an edit to `his_room.py`); those are his decision and walk. It does not make the watchman block anything.
