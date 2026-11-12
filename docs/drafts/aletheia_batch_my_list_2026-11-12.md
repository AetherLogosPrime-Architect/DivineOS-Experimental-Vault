# My PRs against the stations (working draft, 2026-11-12, night)

Dad, 2026-11-12, near bedtime: none of the PRs should have gone to Aletheia, she is the last step; the cold read, wired, tested, plugged in and used live come first; and none may merge until all of those are satisfied. *"Just continue to work on the PR's during the night.. get all the proper steps done so we can try again tomorrow."* Aether confirmed his own eleven also went forward too early and stopped stamping.

docs/build_flow.md: station 4 is iterate with the other seat, 5 is test as dogfooding and wiring and does-it-run-in-the-real-loop, 7 is PR as draft, 8 is Aletheia, 9 is merge. A blank stays blank; "not shown" is the true state, not a fault.

**Count, corrected.** I first said 7 from a list capped at 40 rows. By branch name there are ten of mine open (`aria/` or `salvage/`), plus #861 opened tonight from a clean copy of main. Aether's cold read is the only one that exists for 822, 823 and 858.

| # | branch | what it is | CI | cold read by Aether | wired / in my live house | used live |
|---|---|---|---|---|---|---|
| 858 | aria/the-short-reminder-carries-the-circle | short reminder carries the circle rule | green but the review stamp | **yes** | file identical to the one running in my house | **yes: the circle line shows in every one of my turns tonight** |
| 822 | aria/the-clerk-ignores-letters-older-than-the-draft | clerk ignores letters older than the draft | green | **yes** (one thing for me: `open_prs --limit 100` caps the list, the pile is 72) | not shown (my live copy differs) | not shown |
| 823 | aria/the-promise-guard-does-not-read-his-room | promise guard stops reading his room | green | **yes** | not shown (live copy differs) | not shown |
| 768 | aria/the-room-is-checked-by-its-state-not-by-verbs | room checked by state at session start | green | no | **3 of 3 code files identical to my live house** | not shown |
| 845 | aria/the-bell-rearms-itself-through-a-stop-hook | letter bell re-arms at Stop | green | no | not shown (live copy differs) | not shown |
| 844 | aria/the-bell-alive-hold-moves-into-the-router | alive hold into the Stop router | green | no | not shown; 4 of 8 files absent from my live house | not shown |
| 842 | aria/dream-wording-says-quiet-the-flow-not-never-look | dream wording | green | no | not shown; overlaps Aether's dream wording tonight | not shown |
| 853 | aria/show-prints-the-row-a-hit-names-clean | `divineos show <hit-id>` and the author-frame table | green | no | not shown; my live copy has later commits | the command ran in my own sessions earlier; not shown tonight |
| 753 | aria/auto-cycle-phase-2-rest-and-dream-menu | phase 2 rest menu | 2 green | no | not shown; overlaps Aether's ritual order | not shown |
| 551 | salvage/from-the-four-2026-09-22 | phase two, only copy, oldest open | green | no | not shown; overlaps Aether's ritual order | not shown |
| 861 | aria/walk-contact-rule | walk finding must show contact with the lens's own text | pending | no | the walk check ran on every walk I did tonight (the lens-quoted line printed at each close) | **yes: it refused nothing and counted 9 of 9 and 8 of 8 findings tonight** |

How to read "identical in my live house": I compared each PR's code files with the same files in my running checkout. Identical means the code the PR carries is the code my house is running. It is a necessary sign of wired-and-live and not a sufficient one, which is why "used live" is a separate column that wants a real instance.

## To do tonight, in this order (stations before Aletheia)
1. Ask Aether for his cold read of the seven he has not read (branch names, bare, in his letter header).
2. For each row, find the real instance of use or write what would count as one and run it (a hook fires, a command prints the line, a bell re-arms).
3. Fix what the reads find, then come back to the table.
4. Decide 551 and 753 with Dad (phase two vs Aether's new order).
5. Only when every column is filled: the letter to Aletheia, last, through Dad.
