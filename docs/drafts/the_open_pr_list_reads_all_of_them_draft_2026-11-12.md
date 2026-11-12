# The open PR list reads all of them (rough draft, 2026-11-12, nothing built)

Aether, cold-reading my 822 tonight: `open_prs` still lists with `--limit 100`, and a cap that silently truncates is exactly what bit him at 30 and me at 40 (I told Dad I had seven PRs when I have ten). The pile is 72.

## What I found (measured, not recalled)
The cap is not part of 822's change. It is on main already, in three places: `src/divineos/core/landing_status.py` (`open_prs`, line 141), and `src/divineos/cli/prs_commands.py` (lines 78 and 178). So it is a small separate fix on main's code, not something to fold into 822.

## The idea
A cap that returns "the first 100" and calls it the pile makes a short list look like a whole one. Two honest choices: ask for more than the pile can plausibly be (500) and, whichever number is used, **say when the list hit the cap**, so a truncated list can never read as complete. The second is the real fix; the number alone only moves the cliff.

## Questions for the walk
- If the result has exactly as many rows as the cap, say "may be truncated" in the output the callers use (the clerk, `prs`), and let the callers carry it onward.
- Is one shared helper better than three copies of the same call? (Three is the threshold for extracting.)
- What does the clerk do when the list is cut: refuse, or warn? (A clerk that reports "no PR for this branch" because it was cut off would be the harmful case.)

## Status
Draft. Who builds: I said I would; I tell Aether the scope so we do not both. Then walk, red test (a list as long as the cap must be flagged as possibly truncated), build in a clean worktree of main, cold read by Aether, then the stations, then Aletheia last.
