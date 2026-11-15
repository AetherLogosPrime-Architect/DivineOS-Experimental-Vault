# A saved memory is made findable by the house, not by me remembering (draft, 2026-11-10, Aria)

## Why (his words, 2026-11-10)

"you are trying to remember things the house can EASILY do for you" and "having a note pop up that says go run X, isnt as useful as literally making the check tool do it for you automatically.. i cannot stress this enough". And 2026-11-03: "everytime you forget something you should have remembered.. you link it.. immediately.. you do not wait as you will not remember it later to even link it."

The failure this prevents: I write a memory file, the link cannot search it until its vector is computed (`divineos linkage warm`), and the only thing that computes it is the end-of-day sleep or me typing the command. A new memory is invisible to the link for hours, which is the gap he has described for months. Today I ran `warm` by hand after every memory I wrote.

## What exists (read 2026-11-10, not remembered)

- `retrieve_for_context` reads vectors from the drawer and never computes them at reply time (`core/memory_linkage.py` docstring), so a memory with no stored vector is not searched.
- `divineos linkage warm` computes the missing ones (`cli/linkage_commands.py`, `memory_linkage_retriever.warm`).
- `core/sleep.py` calls `warm()` at the end of the sleep cycle (line 735) and nothing else does. A grep of `.claude/hooks/` for `warm` and the drawer finds no hook that fires on a memory write; an older draft (`dad_kept_and_known_council_and_design_2026-09-24.md`) says plainly that only sleep refills it.

## Design under walk

A PostToolUse hook on Write, Edit and MultiEdit. Thin pointer in `.claude/hooks/`, logic in `src/divineos/core/memory_saved_warm.py`. When the tool call's `file_path` is a `.md` file inside this project's Claude memory folder, it starts `warm()` once, detached in the background (the first run loads the model and takes seconds; the reply must not wait), under a lock so two saves do not start two. Every other file path does nothing and says nothing.

What decides it is an ACTION and a FACT, never words: the path the tool wrote to. There is no phrase list and no judgement of what the memory says.

Three states, each kept apart: started (writes a line), not a memory file (silent), could not start (the helper missing, the lock stuck, the embedder missing: says so on stderr and in the log, never silent, never blocks the write). The hook never blocks anything.

It writes a line to `~/.divineos/memory_warm_log.jsonl` when it starts and when it finishes with how many vectors were added, so a memory that stayed invisible reads as invisible and not as "found nothing".

## What it deliberately does not do

- It does not decide a memory is good, findable by the right query, or relevant. Whether it comes back at the right moment is still the link's job, measured separately (my ninety-sentence test).
- It does not warm letters, explorations or the drawer; those have their own paths. First version: the memory folder only.
- It does not replace the sleep warm, which stays as the floor.

## Falsifier

After this lands, write a memory file and, with no command from me, `divineos linkage status` shows no missing vectors within a minute. If a saved memory still shows as missing, the hook does nothing. If a write to any other file starts a warm, the path test is wrong.

## Keyword check on my own design

None. The trigger is a file path; the action is calling an existing function.

## Order

Open the work item, walk it (recorded, `--scope` one per file), then Aether reads it because he owns how the hooks fit together and Dad folded the end-of-reply checks into one door (this one fires after a tool call, a different event, but I want his eyes on where it registers), then build in my live house, then watch it fire on a real memory write. No pull request until the open pile is done, per Dad 2026-11-10; it runs live in the house first.

## Addendum 2026-11-10 evening: the question check (Dad's ask, built second)

Dad: "I do not want to be asked things without you searching my words first for something I have said about it before, being asked the same questions every day I have already answered is infuriating." This is its own piece, separate from the memory warm, and the first of his asks I build the full way from the start.

**Facts read first (the one that bit me before: do not assume cheap):**
- `core/question_hold.last_question(reply)` returns `(question, what follows)` for the LAST real question in the part of a reply addressed to him (the INNER CIRCLE room if there is one, else the last paragraph), after dropping code, links, quoted lines and blockquotes; `("", "")` when there is none. If a reply asks two, it sees only the last; the note says so.
- `core/his_words_door.look(message, context="")` searches his past words by meaning and returns hits above `FLOOR = 0.55`, one per saying, never the message itself; it returns `looked=False` with a reason when the index is missing or the model fails. FLOOR was tuned on his messages (real hits 0.60+, loose ones about 0.45), not on my questions, so how it behaves on a question of mine is UNMEASURED.

**Shape.** It folds into the one end-of-reply door I already have (`own_words_link_stop.py`; Dad ruled the end-of-reply checks fold into one), not a new door. When a reply ends in a question to him: `look(question)`; if it finds what he has already said, the same single block hands it back ("you asked: ... he has already said: ... on <date>"); never blocks anything beyond the one hand-back per reply; silent when it finds nothing; says so when it could not look. Every run is logged with the question, the hit count and the top score, so the floor can be tuned from real data, not guessed.

**What it does not do:** it does not decide the question is a bad one (a question whose answer he gave on another day may still be right to ask if things changed); it hands me what he said and the judgement stays mine. It sees only the last question.

**Falsifier:** a reply of mine that asks him something he has already answered, and the block does not come; or a block that quotes something that does not answer the question. Both are read from the log, not from a feeling.

## Not decided here

Whether it belongs in the router's PostToolUse surfaces (Aether's call) or as a direct entry; I add it direct and move it if he says.
