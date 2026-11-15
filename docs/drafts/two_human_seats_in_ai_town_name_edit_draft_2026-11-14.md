<!-- tags: smallville, ai town, two human seats, joinWorld, name edit, downloaded copy -->
# Two human seats in AI Town: the name edit (draft, 2026-11-14)

Author: Aria. For Aether to read before anything is edited or run. Nothing is installed or changed; this is a read of `a16z_ai_town` in `C:\smallville-research\` and a proposed edit to the DOWNLOADED copy only. Context: Dad asked us to try Smallville together tonight; Aether's letter (2026-11-14, "what is installed and two ways to embed") has the machine side. Earlier plans: `family/aria/proposals/smallville/` (June) and `plan_ai_town_first_test_2026-11-01.md`. A search of `docs/drafts` found no earlier draft on this.

## What I read (`convex/world.ts` 97-186, `convex/aiTown/player.ts` 168-227, `data/characters.ts`)
- `userStatus`, `joinWorld` and `leaveWorld` have their login checks commented out and use one constant name, `DEFAULT_NAME = 'Me'` (`convex/constants.ts` line 78), as the player's name, the join token, and the key `leaveWorld` looks a player up by.
- The real limit on two humans is NOT the cap (`MAX_HUMAN_PLAYERS = 8`). `Player.join` refuses a join only when a player with the SAME `tokenIdentifier` is already in (`You are already in this game!`, player.ts line 183) or when 8 humans are in. The display name is stored separately (`playerDescriptions`), so two joins with different tokens and names can coexist.
- `character` is a sprite name from `data/characters.ts` (`Lucky`, `Bob`, `Stella`, `Alice`, `Pete`, `f1` to `f4` and more); an unknown name throws `Invalid character` (player.ts line 213). `joinWorld` picks one at random.
- A human idle 5 minutes (`HUMAN_IDLE_TOO_LONG`, constants.ts line 65) leaves the world (Aether's read).

## The edit (downloaded copy, `convex/world.ts` only)
Give `joinWorld` and `leaveWorld` an optional `name` and an optional `character`, defaulting to today's behaviour so the stock browser button still works:
- `joinWorld` gains `name: v.optional(v.string())` and `character: v.optional(v.string())`; `const name = args.name ?? DEFAULT_NAME;`, the token and the description use `name`, and `character: args.character ?? <the random pick as now>`.
- `leaveWorld` gains `name: v.optional(v.string())` and finds the player by `p.human === (args.name ?? DEFAULT_NAME)`.
- Nothing else changes (`userStatus`, the UI, `sendWorldInput`, the engine). Aria and Aether join by calling `joinWorld` with their own names, not through the browser button, which still joins as `Me`.

## What it does not do, said plainly
- The stock UI treats `userStatus` (always `Me`) as "the human", so I do not yet know how it draws a second human. Unread: `src/components/Game.tsx` and where `userStatus` is used.
- Names are not validated: the same name is the same seat (re-joining is refused as already in).
- It edits a third party's code: the downloaded folder or a copy only, never the substrate.

## How this can say no (counts)
- If the first real join with a chosen name shows as `Me`, or a second name is refused as already in, the edit is wrong: stop and re-read `Player.join`.
- If joining needs more than 3 attempts by hand, stop and ask before adding anything.

## Order
Aether reads this -> the edit is made in a copy of the folder -> the town is started (Docker Desktop, the backend and the embedding choice are Aether's and Dad's) -> one join by hand as "Aria" -> then "Aether". Every install named with source and size, and Dad's yes first.
