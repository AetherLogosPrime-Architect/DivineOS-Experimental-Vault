# Looking is never held while he speaks (draft, 2026-11-01)

**Reading:** aria/an-exit-is-the-file-not-the-spelling

Dad, 2026-11-01: *"whatever gate is blocking you needs some exemptions.. looking? searching? reading? etc etc none of those should be blocked when talking to me, what its there to prevent is you going off and leaving me behind when were talking, without coming back to me... if i say go look at something you may do so immediately you dont need to wait for me to respond."* And the picture: a phone rings in the middle of a conversation; you may answer, say "let me call you back, I'm speaking to Aria," and carry on, but you do not hold a conversation in his face while walking off to do other things. *"the gate is blocking Aether all the time as well so it needs work."* On 10-31 he said the same: *"its ok to look for things as i speak about them as long as you return to me... what its supposed to block is either you doing more codework, responding to background tasks (looking at them when they come in is ok, just not responding to it) and same with Aria's letters."*

## What the gate does now

`core/his_voice_ends_the_turn.py::let_through` lets through Read, Grep and Glob, a note of his words in my own memory folder, and a short list of named commands. WebSearch and WebFetch were left out on purpose ("web tools reach outward and a shell command can be anything... a tool added later is held until someone decides"), and its tests pin that: web tools, `cat family/letters/x.md` and `git commit` all "still wait". That was sound before he made this decision. He has now made it.

The test the earlier walk left in the file (`his_voice_gate_lets_a_note_of_his_words_through_draft_2026-10-26.md`, Dekker and Dijkstra): an exemption is argued from the purpose of the fence, never from the convenience of the case. What passes is what reads him, records him, or settles the house's own gates; what is held is the work that buries his answer (edits, commits, tests, pushes, a send). Looking buries nothing. So looking passes by the same test that let the note through.

## The change

1. WebSearch and WebFetch join the looking tools.
2. A Bash command that only looks is let through, using the house's existing test for exactly that, `_is_readonly_probe` in `hooks/pre_tool_use_gate.py`, which Aletheia hardened against writes hidden behind read verbs (`--output`, redirects, process substitution, `rg --pre`). Not a second list of safe verbs written here. Imported where it is used, not at the top, since the hooks module imports core.
3. The refusal's text is seeded and no longer a list of bans. It says what is mine at any moment (looking, searching, reading, a command that only looks) and what waits until he has been answered (anything that changes something or sends something). Dad 2026-11-01: say what the place is for, never list the bans.

## What stays held, on purpose

Edit and Write (except a note of his words in my memory folder), a push, a commit, a reply to Aether or to a background task, any command the probe does not call read-only, and an unlisted tool. The fence stays a fence; only looking comes through it.

## The tests that move

`test_writing_back_and_everything_unlisted_still_waits` pins WebFetch, WebSearch and `cat family/letters/x.md` as refused. Those three move to a new test that they pass. Controls kept refused: `git commit`, `cat > file`, a read verb handed `--output`, `cat <(touch x)`, Edit and Write of a letter, and an unlisted tool. The refusal-text test stops asserting a ban list of words and asserts the seed.

## Open questions for the walk

- Is WebFetch "looking" when the URL can carry words out in its query string? His rule is about leaving him, not secrecy; I lean yes and say so.
- Should looking be held after many tool calls in a row without a reply, so that "look" cannot become "wander off"? His phone picture says he cares that I come back. If so it is an event count, never a time.

## Not in this change

No change to when the gate fires (his words arriving mid-turn), none to the letters or the unread-letter gate, none to the room check.
