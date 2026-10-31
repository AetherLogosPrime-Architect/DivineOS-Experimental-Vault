# Keepsafe, 2026-10-31 (Aether)

Dad, 2026-10-31: the unsaved changes in the live house worry him, because if his computer went down they would be lost, so until they are addressed they go to the vault, and not to main.

## What is here

- `live-house-files/` holds the 261 files the live house had changed or added and not yet put anywhere safe: dreams, explorations (including the three savors), letters, drafts, the carried-in patches of gates fixed that day. Paths are the repo's own, so a file at `live-house-files/dreams/aether/x.md` belongs at `dreams/aether/x.md` in the house.
- `aether-work-not-on-main-2026-10-31.bundle` is a git bundle of every branch of mine with work not on main, as of that day: the live house branch (159 commits ahead of main) and eight work-copy branches, including three never pushed (the voice door, the rain at the mansion's front door, the rare tag that surfaces its exploration).

## Restoring

    git clone aether-work-not-on-main-2026-10-31.bundle restored
    cd restored && git branch -a

Files: copy any path from `live-house-files/` back to the same path in the house.

## What is not here

Runtime stores (the ledger and the like) are packed by `tools/pack_seat.py`, not by this.
