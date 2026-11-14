<!-- tags: promise recorder, promise-reach-detector, transcript re-read, stop hook timeout, byte offset, turn clock -->
# The promise recorder reads only what is new (draft, 2026-11-14)

Author: Aria. Not built. Nearby drafts read first: `the_promise_hook_waits_five_of_his_messages_before_it_blocks_draft_2026-11-13.md` (the turn clock this touches) and `three_findings_from_the_cold_read_of_the_clean_branch_draft_2026-11-14.md`; neither covers the transcript re-read.

## The defect, measured
`.claude/hooks/promise-reach-detector.sh` is a Stop hook with a 10-second timeout (settings.json; 17 of 25 Stop hooks have 10 s). Lines 96-125 open the whole transcript and parse every line as JSON to find the last assistant reply and to count turn starts. Mine is 403 MB, 114,939 records; parsing it once takes 2.0 s (timed alone, no writes). The hook's own log median is 5.2 s over 40 runs, 2 of 40 at or over 10 s (max 12.6 s). The cost grows with every turn, so it only gets worse.

## The change
Keep a bookmark per transcript in the seat's promise folder (where `advance_turn_now` already keeps the turn clock): the byte offset after the last COMPLETE line read, the turn-start count so far, and the transcript's file name. Each Stop: seek to the offset, read only what was appended, update the count, and take the last assistant reply from what was read (if nothing new was appended and no reply was seen, there is nothing to detect).

## The two edge cases that decide whether it is safe
1. A new transcript, or one that shrank (offset beyond the end): start from zero and say so. Same file name with a smaller size is treated as new.
2. A partial last line (the file is being written while we read): do not advance past the last newline; the bookmark stays at the end of the last complete line, so the partial line is read next time, whole.
Also: the turn clock must give the same count as the old full read on the same file; that is the test.

## What can go wrong, and the count that would show it
- The turn count drifts from the old method, and promises look older or younger than they are. Test: run both methods on a copy of a real transcript and on a synthetic one with a partial last line; the counts must be equal.
- The last reply is missed because it was written before the bookmark (a reply appended and bookmarked by an earlier Stop that saw no promise). Test: a transcript where the reply arrives in two appends.

## How this can say no
- Pre-reg: after 30 Stops with the new version, the median of this hook in `hook_timing.jsonl` must be under 2 s and no run over 10 s; if the median is still over 3 s, the transcript read was not the main cost and the draft is wrong.
- If any test shows the new count differing from the old on the same bytes, the change does not ship.

## Decisions made after the walk (2026-11-14, walk-bc1607e1eb7c, prereg-ba388bdc24d8)
- Prior art found by the search I owed: `the_stop_checks_read_the_end_not_the_whole_draft_2026-09-24.md` (Aether) solves the LAST-RECORD question for four helpers with widening tail windows. It does not give a RUNNING COUNT of turn starts, which this recorder needs; that is the part that stays new here. The last reply could use the same tail readers; this draft takes it from the new bytes instead because those bytes are already in hand, and says so.
- The logic moves OUT of the shell hook into a new core module, `core/promise_transcript.py` (`read_new(transcript, bookmark_file, is_turn_start)` returning the last reply found in the new bytes, the total turn count, whether it started over, and the count of unreadable lines; and `commit(result, bookmark_file)`). The hook becomes a thin caller (Dad's second criterion: a hook holds no logic).
- The bookmark is a BYTE offset read in binary, never a text-mode position (Windows CRLF and multibyte text make those unreliable), kept at the end of the last complete line, so a line cut mid-character is read whole next time.
- It is committed right after reading, before detection: a crash later loses that one reply's findings, which the old full read also lost (the next Stop sees a newer reply).
- Condition, one sentence: the turn count from bookmark plus new bytes equals the count a full read gives on the same bytes. The test compares them, and the same comparison is run once offline on the real 403 MB file.
- Not in this slice: the other hooks that read whole transcripts (continuity-frame-detector, lepos-channel-reflect, `promise_markers.turn_index`).

## Order
Reach, walk with Aether (he owns the Stop-door order), root-cause record, the equal-count test written to fail first, build, pre-reg, then Aletheia and Dad before any merge. Dad said "ok go ahead" on 2026-11-14 after this draft's description reached him, so the walk and build proceed; Aether is told by letter.
