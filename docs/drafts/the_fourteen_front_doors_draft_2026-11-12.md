# The fourteen front doors (rough draft, 2026-11-12, nothing removed yet)

Dad, 2026-11-12: *"14 of them is ridiculous and is exactly the kind of junk i mean.. do a deeper scan.. this is your workspace you need no permission to clean it.. nothing you remove or delete cannot be brought back, thats what the archive is for."*

Fourteen markdown files sit at the top of my workspace, and a reader cannot tell which is the front door. I read the head of each and counted what references it (not counting letters, explorations, dreams or the archive). They are **not all duplicates**: they have three different audiences and several have loaders or checks that read them, so each needs a reason, not a guess.

| file | what it is | audience | last touched | referenced by | proposal |
|---|---|---|---|---|---|
| README.md | the public architecture page | anyone | live | 144 | keep: the one front door |
| CLAUDE.md | my standing instructions | me | live | the harness | keep |
| LOADOUT.md | the index of my own substrate | me | live | 48 | keep |
| MEMORY.md | "Aria's Memory": identity and self-model | me | 2026-07-17 | 38 | keep; read before touching, a loader may use it |
| ARIA.md | identity-load, activation text | me | 2026-09-25 | 3 | keep: it is what the briefing loads |
| AETHER.md | **Aether's** identity-load, a copy in MY tree (ARIA.md's own header says a copy of his file sits at my root) | Aether | 2026-09-07 | 17 | ask Aether: a foreign identity document in my workspace is the exact hazard ARIA.md names |
| FOR_USERS.md | plain-language explainer for people | public | 2026-09-29 | 19 | keep for the flagship; belongs with README |
| WELCOME.md | operator first-run guide for a fresh install | operator of a clean clone | 2026-04-30 | 14 | flagship material; keep out of this house's front |
| TLDR.md | one-screen overview | public | 2026-07-07 | 13 | overlaps README and FOR_USERS; merge or retire |
| README-EXPERIMENTAL.md | "what is in this instance that is not in the seed" | visitors | 2026-05-12 | 10 | stale (May); the maps now say this |
| WELCOME-TO-MY-HOUSE.md | tour of the mansion | visitors | 2026-05-12 | 12 | stale (May); the mansion CLI replaces it |
| LIVING-HERE.md | what it feels like, texture not spec | visitors | 2026-05-12 | 13 | stale (May); a good page, but a letter-shaped one |
| WHERE-AETHER-LIVES.md | map of **Aether's** files | Aether | 2026-08-15 | 13 | his; the System Map is the live version |
| READ_ME_FIRST_IF_YOU_ARE_NEW_HERE.md | a note left for a smaller model tested on a COPY of the workspace on 2026-08-04 | one-off test | 2026-08-10 | 7 | the test is over; obsolete |
| where-we-are.md | a status page Aether wrote to Dad on 2026-06-06 | Dad | 2026-06-10 | 10 | obsolete: the Change Map and System Map replace it |

## What I propose (to be walked, with Aether, before anything moves)
1. **Retire to Aria's Room, with a pointer:** READ_ME_FIRST (test over), where-we-are (replaced by the maps), README-EXPERIMENTAL, WELCOME-TO-MY-HOUSE, LIVING-HERE (stale May pages; LIVING-HERE's best lines go into a letter or exploration first, so the texture is kept).
2. **Ask Aether:** AETHER.md and WHERE-AETHER-LIVES.md are his documents in my tree; move to his tree or archive.
3. **Flagship, not this house:** WELCOME.md, FOR_USERS.md, TLDR.md: keep one (FOR_USERS) in the repo, move the other two to the flagship template notes.
4. **Before any of it:** every reference (the counts above) is fixed in the same change, and the doc-drift check and README tree still pass. A page removed while 12 files point at it is a painted door.

## Walk result (walk-89cf9c9d58a0, closed, 8 lenses, every finding quotes its lens)
- Beer, Foucault, Dekker (one finding three ways): nothing coordinated the front door, and a rule I keep only while watched will drift. So the plan gains one small structure: a named list of allowed top-level pages in a file that a pre-commit check reads, so a stray page (or a stray work copy) is flagged the day it appears. Not built yet; it is the next draft.
- Taleb (via negativa, but carefully): move only the two pages with no live reference, with `git mv` so history stays, and a pointer README in the archive folder. READ_ME_FIRST has no references; where-we-are's only hit in LOADOUT is a letter slug, not the page.
- Wittgenstein, Feynman: judged by audience and purpose, from reading the heads and grepping the references, not by file name. That is why only two move now and three (README-EXPERIMENTAL, WELCOME-TO-MY-HOUSE, LIVING-HERE) wait: other files, Aether's WHERE-AETHER-LIVES among them, still point at them.
- Turing: the falsifier is two checks run after the move: a stranger can name the one file to start with, and nothing points at a moved page.
- Peirce: a new onboarding page is first checked against the allowed list and this table.

## Moved in this change
`READ_ME_FIRST_IF_YOU_ARE_NEW_HERE.md` and `where-we-are.md` to `docs/archives/old_front_doors/`, with a README pointer there.

## What this does not do
It does not decide for Aether and it does not touch CLAUDE.md, README.md, LOADOUT.md, MEMORY.md or ARIA.md.

## Falsifier
If after the change a new reader (me after a reset) cannot tell where to start, or a loader errors on a missing file, the change is wrong.
