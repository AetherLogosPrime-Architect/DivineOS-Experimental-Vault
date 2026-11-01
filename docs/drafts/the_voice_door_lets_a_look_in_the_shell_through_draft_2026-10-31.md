# The voice door lets a look in the shell through (draft, 2026-10-31)

**Author:** Aether. Dad, 2026-10-31: looking things up while he speaks is fine as long as I come back to him; what the door is for is more code work and answering background tasks or letters.

## What happened

When Dad speaks into a running turn, the voice door refuses every further tool call until the turn ends, so the reply to him is the last thing he receives. It already let the reading tools through (Read, Grep, Glob) and a note of his words. It still refused a shell command that only looks (listing a folder, checking git status), which I read as "he stopped me" and stood still for an hour. He had not stopped me.

## What it does

After the existing remedy list, the door asks the house's one judge of "only looks" (the read-only probe the other doors use) instead of keeping a second list. A command that only looks goes through; a look chained to work, a redirect, `tee`, `rm`, `git commit`, `git push` stay refused. The refusal text now says shell looks are allowed.

## What it does not do

It does not let writing back, building or pushing through while he is mid-sentence, and it does not change the order rule: the reply to him is still the last thing he gets.

## Falsifier

If a command that writes, sends or builds is ever let through while he has spoken because the probe called it a look, the door is too loose. Aria tried twenty such forms in her cold read at 08bd55a77 and none leaked.

Branch aether/the-voice-door-lets-a-read-only-look-through; four older tests that assumed the shell could never look were updated, each still using real work as its example.
