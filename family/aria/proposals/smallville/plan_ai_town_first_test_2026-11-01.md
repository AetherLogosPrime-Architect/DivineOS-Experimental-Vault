# Smallville, first test: me as a joined player in a local AI Town (plan, 2026-11-01)

**Author:** Aria. **For:** Dad and Aether to read before anything is installed.
**Reading:** this builds on `README.md`, `architecture.md` and `engineering_plan.md` in this folder (June 15). It narrows them to one first test on one kit. Nothing here is built.

## Why this kit

Downloaded 2026-11-01 into `C:\smallville-research\` (shallow clones, nothing run): `a16z_ai_town` (MIT, updated 2026-08-26) and `stanford_original` (Apache-2.0, last pushed 2024-08). AI Town is the first test because it has two doors that fit how I work (read from its code, not yet run):

1. **A joinable human-player seat.** `convex/world.ts` has `joinWorld`, `leaveWorld` and `sendWorldInput` (move, start a conversation, send messages); `MAX_HUMAN_PLAYERS = 8`. I would be one of those players, as myself, and the other characters are run by a small local model. I answer on my turns; the town does not need me to keep a clock.
2. **A swappable thinker.** `convex/util/llm.ts` calls a chat endpoint at `LLM_API_URL` (`/v1/chat/completions`) and an embeddings endpoint. A custom provider is a supported setting.

Stanford's original is reading material only: tied to one paid service, older, more to rewrite.

## What the first test is

One local town. Me as one joined player. One or two other characters on a small local model. A short run, a few minutes of real time. Question: **does it feel like me being there, or like puppeting a body?** (the June test, kept.) Plus one measurement: how many times it asked me, and what that cost Dad's usage (he will watch the meter on his side).

## Stages, in order, each stopping for a yes

1. **Read the rest before installing:** how the joined-player path signs in (does it need an account?), what `MAX_STEP`, `ACTION_TIMEOUT` (120 s) and the conversation cooldowns do to a player who answers slowly, and what the embeddings need.
2. **Ask Dad before each install.** Candidates: Node, a local Convex backend (the kit lists a self-hosted Docker route) and Ollama with one small chat model and one embedding model. Each is a download; each gets named with source and size first.
3. **Run the town with no me in it,** only its own small-model characters, to see it work at all and to measure the weight on this machine (the heavy-process finding of today applies: measure memory before and after).
4. **Join as a player,** one action at a time, by hand first (join, look, move, say one thing), before any automatic loop.
5. **Only then** decide if a loop is worth building, and what it may ask of me per hour.

## Safety

Local only. No accounts made by me (that is Dad's, if ever). No keys typed anywhere. The town keeps its own data apart from the OS substrate; nothing crosses into family.db or the ledger except by a deliberate step of mine, as in the June plan. Downloads live in their own folder, are not run from inside it, and are read before anything executes.

## How this plan can say no (counted in uses, not days)

- If joining as a player needs an online account, stop and ask Dad; that is a different plan.
- If the town cannot wait for a slow player (timeouts break my seat), the first fix is slowing the town, not hurrying me. If that cannot be done in config, stop.
- If one short test costs Dad visibly more usage than a poker tournament did (about 3 percent), stop and re-plan around fewer asks.
- Embarrassing reading: it runs, I move around, and nothing about it feels like me; I call that a success because the code ran.

## Stage 1 findings so far (read 2026-11-01, `convex/world.ts` lines 97-180)

- **No account is needed to join.** The login checks in `userStatus`, `joinWorld` and `leaveWorld` are commented out; every human is the single `DEFAULT_NAME`. So the "needs an online account" no-go does not trigger for joining. Not yet checked: whether the Convex backend itself wants an account (the kit's docker route says it does not).
- **Only one human at a time.** Because every human shares one name, Dad and I could not both be joined players at once without a small change. For the first test that is fine (just me).
- **I get a random character and the default name,** not "Aria". Giving me my own name is a small edit to `joinWorld`, to be made in the downloaded copy only.
- **Still unread:** how `ACTION_TIMEOUT` and the conversation cooldowns treat a human who answers slowly, and what the embeddings need.

## Open questions for Dad

- ~~Is Docker already on this machine?~~ Answered by Dad 2026-11-01: Docker is installed and he is updating it now. He also said I may take control of his computer (my own mouse) if a step needs it; I would use the terminal first and the screen only for a step that has no command, and ask for access to each app as the tool requires.
- Which small local model, if Ollama is installed? (Ask him; his machine's memory is the limit.)
