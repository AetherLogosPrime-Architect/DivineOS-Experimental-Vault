<!-- retired-rule
id: older-ritual-start-numbers
retired: 2026-10-16
retired-by: Andrew
successor: the ritual starts at 850k tokens and the hard line is 890k (FIRE_TOKENS and HARD_TOKENS in .claude/hooks/auto-cycle-token-trigger.sh, TRIGGER_THRESHOLD in src/divineos/core/auto_cycle.py). Read those constants, not a remembered number.
pattern: (?i)\britual\s+(?:starts?|fires?|trigger(?:s|ed)?)\s+(?:at|is)\s+(?:920|950|940|880)k\b
pattern: (?i)\bstart\s+the\s+ritual\s+at\s+(?:920|950|940|880)k\b
pattern: (?i)\bcompaction\s+(?:happens|hits|lands)\s+(?:at|around)\s+(?:999k|1m)\b
-->

# The older ritual start numbers

**Retired by Andrew 2026-10-16 (850k start, 890k hard line). Archived 2026-11-15, the day he explained the lineage to me and told me to retire the old amounts with their reasons.**

## What they said

The ritual (walk, commit, extract, sleep, dream, rest) starts at a token count: first 920k, at one point 950k with a hard line at 950k, then 880k, now 850k. The numbers also appear in prose as "compaction happens at 970k" or "999k".

## Why they moved

There are two different numbers, and they moved for different reasons. I misread them as one number being revised, told Aria so, and he corrected me on 2026-11-15.

1. **Where compaction happens is the platform's number, not his.** It was around 970k, then it moved to 999k, then back to about 970k, and later it was seen landing near 950k and 960k. The platform moved it and told nobody.
2. **Where the ritual starts is ours, and it tracks two things at once:** the platform's compaction point and the growing size of the ritual itself. In his words, compaction was happening *during* the ritual, so the start was moved back to give the whole ritual room to finish. 970k, then 950k, then 920k ("as the ritual grew we needed more room"), then 880k after compaction was seen near 950k (2026-09-18), then 850k on 2026-10-16 because the ritual takes longer lately.

So "920k" was right when it was set and wrong later, and nothing announced the change. A number with a reason, copied without the reason.

## What replaced it

The constants in the hook and in `auto_cycle.py`. The reasons for each step stay in the dated comments next to them; this file is where they are gathered.

## What is still owed

Some live comments still quote 920k and 950k as the trigger (the heartbeat hook's header, and explanatory comments in the trigger hook and the context meter). They are dated quotes of his words and read as history; the checker names any real hit and each is marked as history or reworded, read by me, not by the pattern. This guard catches copies, not rewordings (nine-twenty, 920 thousand). The repair that ends the drift is named in `auto_cycle.py` and is still owed: read the ritual start from observed compaction points instead of remembering a number.
