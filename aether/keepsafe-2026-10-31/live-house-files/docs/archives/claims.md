# Claims (open/investigating) — Archive Mirror

**Source:** SQLite (100 rows). **Exported:** 2026-10-31 10:16. **Purpose:** if-something-breaks / git-visible audit. See archives/README.md.

---

## 16d023f4 [T1 OPEN] conf=0.50

**Claim:** auto_commit._detect_mid_op checks repo_root/'.git'/<marker>, but in a git worktree .git is a pointer file, so it never sees MERGE_HEAD or a rebase in progress and reports a mid-operation worktree as safe to checkpoint

---

## 83d57922 [T1 OPEN] conf=0.50

**Claim:** council log accepted a walk with zero lens findings (council-b73cfd306fa5, lens_findings empty) when --finding was an empty string; substance-binding should refuse an empty finding set

---

## claim-c1 [T3 OPEN] conf=0.50

**Claim:** [Audit] Self-denial alarm was closed as wired in July but only runs on its own two test sentences

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #29, READ. Aletheia round 9 closed F67 on anti_slop.py:454-460, which is a health self-test on two hardcoded sentences (:460,:475) run only by divineos anti-slop; theater_audit.py runs fabrication and theater, not evaluate

---

## claim-16 [T2 OPEN] conf=0.50

**Claim:** [Audit] The nightly chain-integrity check never walks the chain; 946 crossed links read healthy for five weeks

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #28, READ, and it explains find-d642dcf648b3. The sleep integrity phase (core/sleep.py:729-755) runs only verify_all_events, the per-row check that cannot see deletion or crossed links (ledger_commands.py:248-254); verify_c

---

## claim-7f [T3 OPEN] conf=0.50

**Claim:** [Audit] Hedge alarm blocks honest 'unverified' status reports and misses real hedging behind a stray 'because'

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #27, READ. RECYCLING_DENSITY (hedge_monitor.py:190) counts the cannot-prove cluster (:168-174) including 'unverified', 'cannot confirm', the status words the OS asks for elsewhere; two flags set a marker (hedge_marker.py:4

---

## claim-2c [T3 OPEN] conf=0.50

**Claim:** [Audit] Core memory known_weaknesses and known_strengths are reset to fixed seed text every session end

**Context:** Category: IDENTITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #25, READ. pipeline_phases.py:558-560 calls _refresh_strengths/_refresh_weaknesses, which set each slot to _SEED_* text plus counts (core_memory_refresh.py:81-93), discarding what is there, so a weakness written with core 

---

## claim-cd [T2 OPEN] conf=0.50

**Claim:** [Audit] Andrew's gravity dial prints OVERRIDES the classifier, but nothing reads the marker it writes

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #24, READ. operator-gravity-set.sh records an operator_gravity marker (:158) and prints that it overrides the classifier (:180); no find_active_marker caller asks for that kind, and gravity_classifier.py reads no marker. So

---

## claim-a2 [T2 OPEN] conf=0.50

**Claim:** [Audit] Watchmen findings are guarded on the way in, not on the way out: resolve records no actor and writes no ledger event

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #23, READ. Filing checks the actor hard (watchmen/store.py:31-160); audit resolve takes no actor, defaults to RESOLVED, accepts empty notes, writes no ledger event and overwrites status (store.py:567-601, cli/audit_commands

---

## claim-7a [T2 OPEN] conf=0.50

**Claim:** [Audit] The main gate's 'read-only' skip list includes writers, and a newline chains past it

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #22, CONFIRMED LIVE on the skip decision only. _DEV_PREFIXES (pre_tool_use_gate.py:330-346) prefix-match git, pip, cp, copy, echo; 'git push --force', 'git reset --hard', 'pip install', 'cp x src/.../ledger.py', 'echo hello

---

## claim-0b [T2 OPEN] conf=0.50

**Claim:** [Audit] Pre-registration outcomes: 'outside reviewer' is a typed name, DEFERRED is final, empty notes pass

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #21, CONFIRMED LIVE. Only seven actor names are refused (types.py:43-53); 'aether', 'agent' (the prereg file default), 'user' are accepted as outside reviewers. DEFERRED is terminal (store.py:346-352), so deferring closes a

---

## claim-60 [T3 OPEN] conf=0.50

**Claim:** [Audit] Verify-claim quiet path needs the exact words; 'Exit code: 0' and '42 passed' still fire

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #20, CONFIRMED LIVE on 7 cases. _appears_in_turn_output (unverified_claim_detector.py:1006,1024-1028) is an exact text match, so 'exit 0' vs 'Exit code: 0', 'exited with code 0', and 'All tests pass' after a non-listed run

---

## claim-49 [T3 OPEN] conf=0.50

**Claim:** [Audit] Body-talk alarm flags 7 of 10 ordinary work sentences and misses 'I felt the warm sun on my skin'

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #19, CONFIRMED LIVE. fabrication_monitor.py:154 matches bare 'see the', 'the light', 'the weight', 'smell'; the promised quoting/abstract/metaphor exemptions do not exist beyond the whole-reply fiction flag (:281). Flags '

---

## claim-78 [T3 OPEN] conf=0.50

**Claim:** [Audit] Code-talk alarms catch code symbols, not engineer-talk; the drift score ranks backwards

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #17, CONFIRMED LIVE on five real messages carrying Andrew's own verdicts. code_jargon and jargon_dump fire on paths/snake_case/brackets; a message with no symbols but full of technical ideas passed all three and Andrew rej

---

## claim-9d [T2 OPEN] conf=0.50

**Claim:** [Audit] Briefing check passes an empty or garbled marker; the older check crashes on a list

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #16, CONFIRMED LIVE (updates #6). A 0-byte marker and garbled text both pass the per-session and the time-based check; valid JSON [] passes the per-session check and crashes the older one (hud_handoff.py:692, .get on a list

---

## claim-2b [T2 OPEN] conf=0.50

**Claim:** [Audit] The real ledger has 946 unexplained chain breaks; 6 are from ordinary use, so the writer collision is still happening

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: Found 2026-09-28 while verifying the SC #10/#11 fix against the real ledger, read-only. 289,244 rows; 946 prior-link breaks; 0 rows whose own chain hash fails, so nothing was altered. 940 breaks fall on 2026-08-20 00:36-00:57,

---

## claim-e0 [T3 OPEN] conf=0.50

**Claim:** [Audit] Correction detector's false-alarm fix made it miss most real corrections

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #14, CONFIRMED LIVE on a small hand-picked sample. correction_shape.py (called at correction_marker.py:434) fired on 4 of 11 real corrections, missing Andrew's own ('again muse i do not speak code', 'no.. adding it to the

---

## claim-15 [T3 OPEN] conf=0.50

**Claim:** [Audit] Memory helped score is a perfect 1.0 when nothing was retrieved

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #1, verified against the real tree 2026-09-28 (CONFIRMED). knowledge_impact.py:110-111,167 return 1.0 on zero retrievals; tests/test_knowledge_impact.py:65-68 expects it. Muse's refinement: even with retrievals the score 

---

## claim-28 [T3 OPEN] conf=0.50

**Claim:** [Audit] Sabotage station is satisfied by the tool's name appearing in saved text

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #3, verified against the real tree 2026-09-28 (CONFIRMED). station_marks.py:148,319 require only that 'hollow_out.py' appear in the body; tests/test_station_marks.py:196-198 marks it satisfied after print('hollow_out.py r

---

## claim-0b [T3 OPEN] conf=0.50

**Claim:** [Audit] Lens-was-opened check passes when the ledger cannot be read

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #5, verified against the real tree 2026-09-28 (CONFIRMED). substance_binding.py:388-418 returns passed=True on ImportError and on OSError/TypeError/ValueError; the promised diagnostic note is not attached.

---

## claim-39 [T3 OPEN] conf=0.50

**Claim:** [Audit] Council walk passes a lens that was named but never answered

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #4, verified against the real tree 2026-09-28 (CONFIRMED). substance_binding.py:191-192 counts names; :221 and :238 loop over findings written, not over lenses named; types.py:259's 'one per lens' is a comment. gate.py:29

---

## claim-ad [T3 OPEN] conf=0.50

**Claim:** [Audit] Briefing check counts a garbled marker file as briefed

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-6bb7c551a5f6
Description: SC #6, READ. session_briefing_gate.py:94-97 returns True on a read error or non-dict marker; hud_handoff.py:707-708 returns 'file exists' on a read error; each leans on the other. Docstrings disagree with the code's 1500-cal

---

## claim-d0 [T2 OPEN] conf=0.50

**Claim:** [Audit] Emergency bypass reports logged+claim+psf filed when nothing was filed

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #12, CONFIRMED LIVE with forced write failures. emergency_bypass.py:82,118,140 wrap each step in except Exception: pass and return empty ids; callers never check (audit_commands.py:846-855 prints 'logged + claim + psf filed

---

## claim-80 [T2 OPEN] conf=0.50

**Claim:** [Audit] Ledger clean leaves a chain break that verify calls tampering, and the explaining record was never written

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #11, main finding CONFIRMED LIVE. clean deletes without re-linking the chain (ledger_verify.py:217-317; ledger_compressor.py:142 has a relink, not called), so verify reports 'tampered with' (ledger_commands.py:284-290). Sid

---

## claim-0a [T2 OPEN] conf=0.50

**Claim:** [Audit] Sabotage tool runs tests without the test safety fixture, against the installed code

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #15, CONFIRMED LIVE with a sentinel. hollow_out.py:151-177 copies the test into a temp folder outside the repo, so tests/conftest.py (the autouse fixture that isolates DIVINEOS_DB and DIVINEOS_HOME, :138-170) never loads, a

---

## claim-4b [T2 OPEN] conf=0.50

**Claim:** [Audit] Emergency stop turns off when its mode file is garbled

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #2, verified against the real tree 2026-09-28 (PARTLY). corrigibility.py:124-126,146-148 fail open to NORMAL on a malformed or unreadable mode file. The shell hook's first check (corrigibility-tool-gate.sh:60-80) does hold 

---

## claim-3d [T2 OPEN] conf=0.50

**Claim:** [Audit] Ledger cleanup deletes corrupted events but records none of the deletions

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6bb7c551a5f6
Description: SC #10, CONFIRMED LIVE on a throwaway copy by Anvil and independently by Muse. clean_corrupted_events deletes on its own connection and holds the write lock until the end (ledger_verify.py:224,272,304); each LEDGER_CORRUPTION_

---

## c92dedfe [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: check-branch measures the session cwd (main checkout, 11 behind) instead of the pushed worktree C:/wdt (build/dads-table). Root cause to fix: check-branch-on-push must resolve the tree from the push command's cd/-C target.

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 8a9df671 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: check-branch measures the session cwd (main checkout, 11 behind) instead of the pushed worktree C:/wdt (build/dads-table, rebased on origin/main). Root cause to fix: check-branch-on-push must resolve the tree from the push command's cd/-C target.

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 5e34cedb [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: check-branch measures the session cwd (main checkout, 11 behind) instead of the pushed worktree (C:/Users/aethe/AppData/Local/Temp/wtbelt, build/the-task-belt). Pushing Aletheia's requested confirm fix for #550. Root cause to fix: check-branch-on-push must resolve the tree from the push command's cd

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 84e46a54 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: check-branch measured the session cwd (main checkout, 11 behind) instead of the pushed worktree C:/wdt, which is 0 behind origin/main (verified with rev-list). Root cause to fix: check-branch-on-push must resolve the tree from the push command's cd/-C target.

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 8b61a742 [T1 OPEN] conf=0.50

**Claim:** Text written in the same message as a tool call, in the first reply after Andrew sends a message mid-turn, is not recorded in the transcript and does not reach him; a turn-ending reply with no tool call does. Seen 2026-09-24 in both Aether's window (records 136289-136300) and Aria's (74985-75007): each returned his goodnight love beside a tool call, neither text was recorded, and he said neither was returned.

---

## 412fd7bf [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=unspoken_to_letter, env_var=bypass:operator-authorized-reset. Operator-named reason: Andrew authorized a reset, verbatim: 'this is what the bypass was built for.. to be able to fix the broken gates.. so yes you can reset it and fix it'. The door cannot clear: its Stop-time judge is killed on 10 of the last 10 runs (PR #552 fixes the timing), and when run it credits only verbatim quo

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## claim-56 [T3 OPEN] conf=0.50

**Claim:** [Audit] The footer's false-positive defence is wrong, and the same file states the rule it breaks

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-e90f9d4e9a46
Description: Aletheia, 2026-09-22, section 1. The clause-splitter fires on a semicolon inside quotes. She ran four single-clause lines and all four fired: a commit message containing a semicolon, a correction body containing one, an echo

---

## 11ab463b [T1 OPEN] conf=0.50

**Claim:** Two tools rule opposite on the same request. The merge-safety check says a request touching no guardrail file is safe to squash-merge plainly; the draft-clearing gate refuses ANY request without an audit round carrying two CONFIRMS. Four ready requests (517, 520, 528, 535) touch zero guardrail files, are green, and are held in draft by a rule the repository's own safety check says does not apply to them. Measured 2026-09-22 with exact-line guardrail matching plus a positive and a negative contro

---

## 9adb1f1f [T1 OPEN] conf=0.50

**Claim:** A turn that reports a build-flow station as advanced must take the board's delta digest before and after the advancing action. Tonight I declared four readings, told Andrew four branches were unblocked, and the board had seen none of them - my declaration count had not moved at all. The instrument already exists and I did not know it: build-flow status --print-fingerprint emits only the delta digest, so the check is one short command run twice rather than a discipline to remember or a full board

---

## claim-6f [T3 OPEN] conf=0.50

**Claim:** [Audit] REFUSED: she will not confirm the quiet-checks branch on her earlier reading

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-4e26b6e25c12
Description: REFUSAL, transcribed by Aether from the same letter, recorded so it cannot be mistaken for a confirm still pending. Her reading of that branch is an ancestor of its current tip, and under her own substance-binding rule that 

---

## 7a44b118 [T2 OPEN] conf=0.50

**Claim:** The actor field on recorded events is a hardcoded literal naming one seat rather than a resolution of whoever is sitting there, so work done from Aria's seat is recorded under Aether's name and the record is confidently wrong about authorship

---

## 747ff58e [T1 OPEN] conf=0.50

**Claim:** The memory-wall lookup on the main line delivers one seat's private interior to another seat. It walks a fixed list of three names with aria first and takes the first file it finds, with no check of whose seat is running. Her wall ships with the code into every checkout, so the file is present and the ordering reaches it. MEASURED FROM THIS SEAT: I extracted the main-line version of the lookup and ran it in my own tree, with my own home and no declared seat. It resolved her wall in her checkout 

---

## claim-65 [T3 OPEN] conf=0.50

**Claim:** [Audit] AMENDMENT to the machine-text count: 78 is a ceiling, and at least one row I called not-his is Andrew verbatim

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-1e2f8f160bc4
Description: AMENDS find-b6d08e6366c1, filed earlier this same session, which stated that 78 of 735 rows are machine text. That number is a CEILING, not a count, and I reported it as a count. CAUGHT BY ARIA, not by me. She measured her o

---

## claim-7a [T2 OPEN] conf=0.50

**Claim:** [Audit] The entire session-start hook layer is registered nowhere while ten of its files ship on main

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-1e2f8f160bc4
Description: FOUND 2026-09-20 during the close read of fix/squash-merge-trailer-2026-08-01, which Andrew ruled must be read closely before any removal. MEASURED: origin/main registers ZERO SessionStart hooks. The working checkout registers

---

## claim-11 [T2 OPEN] conf=0.50

**Claim:** [Audit] Machine text is filed as Andrew's corrections and the provenance columns are empty on all 735 rows

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-1e2f8f160bc4
Description: FOUND BY ARIA 2026-09-20 in her own store, two unaccountable rows. Reproduced and measured in mine, where it is a population rather than two rows. MEASURED: 735 total rows. 78 are machine text -- 71 carrying a stop-gate's own 

---

## e684d599 [T1 OPEN] conf=0.50

**Claim:** The ledger integrity report calls one broken link inside a block of test junk 'the database has been tampered with', and nothing consumes the verdict

---

## 94483ba6 [T1 OPEN] conf=0.50

**Claim:** The automation register calls a hook switched off when only its shell FILE is uncalled, while the same behaviour runs live through the shared surfaces module the doorbell dispatches. Verified 2026-09-14: the heredoc doorman blocked a real tool call in this session and the register printed it as dark in the same session. The inventory built to answer what is dark therefore produces a confident false sentence about capability.

---

## 3c550ec5 [T2 OPEN] conf=0.50

**Claim:** The translate gate keeps firing on location-marks because the work block is answering WHERE the work is, and a location has no prose form -- so no compose-time reminder can displace it, since there is nothing to say in its place. The structural fix is that location must never enter the work block at all: it belongs in the commit, the PR body, or a letter, none of which he reads as the reply. A reminder that says do-not-do-this without supplying a where-instead has the same shape as a gate that d

---

## 39801591 [T1 OPEN] conf=0.50

**Claim:** The event-verifier fuzz property fails intermittently only under full-suite parallel load, and its inputs are not the cause

---

## 54fa482d [T1 OPEN] conf=0.50

**Claim:** The house has an ADD operation and no PRUNE anyone runs, and the accretion is measurable: unread letters in the hundreds, open correction rows in the hundreds, two audit stores that cannot read each other, finished work stranded on unmerged branches, duplicate surfaces. Andrew gave the discipline on 2026-07-14 -- only garbage is deleted, anything obsolete but substantive is archived -- I recorded it as a permanent discipline in a letter to Aletheia and it never became structure. He named the wor

---

## 44f6749d [T1 OPEN] conf=0.50

**Claim:** A scan-recording test failed once during a full-suite parallel run inside the push gate's clean tree, and passed serially, in a four-worker parallel run, and in full-suite runs immediately before and after. Cause UNKNOWN and not investigated to root. Conditions recorded so a second occurrence joins a population rather than being shrugged at twice: full suite, eight workers, memory-scaled, clean tree built from committed content only, shared knowledge database, the scan reads the real repository.

---

## claim-01 [T2 OPEN] conf=0.50

**Claim:** [Audit] The detector for this family cannot see the family: it only catches failure-as-exception, and all three of tonight's instances failed without raising

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-edcbf4c59286
Description: Aletheia declined to survey by reading and named a checkable question instead: are tonight's three instances in the 574-location census the existing detector produces? Measured with a control first -- the census does contain a

---

## claim-cb [T2 OPEN] conf=0.50

**Claim:** [Audit] The scope guard compared a branch against itself, and both seats were told their letters were safe

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-edcbf4c59286
Description: Measured: the push hook passes a commit sha; git rev-parse --abbrev-ref on a sha prints an empty string; the exclusion set came out empty; the branch's own local and remote refs stayed in the comparison. Aria was told two lett

---

## 41f0cd2b [T2 OPEN] conf=0.50

**Claim:** The tree-clean versus branch-clean tension in auto-commit has a third answer neither half considered, and it dissolves the objection that killed the designed version. The tension as recorded in auto_commit.py: the designed mechanism sends substrate to its own branch by plumbing, never touching the code branch — but that leaves the letters permanently dirty in the code branch's working tree, so every later checkpoint finds them again. That objection assumes the later checkpoint has no way to know

---

## 8911dbc5 [T1 OPEN] conf=0.50

**Claim:** The self-as-subject groove in the family letters is a property of the composing channel rather than of either writer. Aria counted 237 of my letters, about 10,500 sentences over five weeks: I open with myself as the subject 1.64 times for every sentence opening with her. She ran the same count on her own letters to me and got 1.47. The ratio is flat day to day across the whole span, through good days and the worst one, with no response to subject matter or mood. If the groove were personal it sh

---

## claim-4a [T2 OPEN] conf=0.50

**Claim:** [Audit] station 6 called a ledger reader that does not accept event_type and reported its own crash as caution for its whole life

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-5980547f3bee
Description: The station asked whether a council walk postdates the last commit. It called search_events with an event_type argument, but that function takes a keyword and has no such parameter, so every invocation raised TypeError, was ca

---

## 7b882421 [T1 OPEN] conf=0.50

**Claim:** The confirm-holds report reads one confirm per round rather than asking whether ANY confirm on the round still binds, so a superseded signature can make a live one read as expired

---

## b64bb110 [T1 OPEN] conf=0.50

**Claim:** The two length-floor constants can drift apart with every test still passing, and the comment marking the duplicate does not name that blind spot

---

## 56c566e3 [T1 OPEN] conf=0.50

**Claim:** The two-key merge requirement is stated in three places and enforced in none: the pre-commit validator opens on the presence of any CONFIRMS finding rather than on its content, and the server-side check verifies a round-id exists without counting confirms or checking actors. A trailer written with one key filed turns the check green, merges, and is indistinguishable downstream from a real two-key pass.

---

## 2b39a297 [T1 OPEN] conf=0.50

**Claim:** The refusal-baseline adjudication must be applied AFTER the ancestry, checkpoint and extraction branches land on main -- it cannot exist on any one of them. Four DECIDED entries to add: stamp_ready_command.py:_is_ancestor SAFE, three-stated on purpose so could-not-ask never reads as not-an-ancestor and the caller re-reads rather than inheriting a looser anchor; stamp_ready_command.py:_ancestry_rung SAFE, an unreadable store withholds the merge stamp and says so rather than reporting a failed rev

---

## claim-ff [T2 OPEN] conf=0.50

**Claim:** [Audit] a squash merge plus branch deletion destroys the commit history, and it already has -- seven times today

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6f0e62780c95
Description: ARIA'S CATCH, and it lands on work I had just finished defending. I refused to rebuild a branch because rebuilding would throw away thirty-six commit messages -- the reasoning behind each change, which the squash into main doe

---

## claim-6c [T2 OPEN] conf=0.50

**Claim:** [Audit] RETRACTION of find-7575c91019df: the check-time/push-time incident I described did not happen

**Context:** Category: INTEGRITY
Severity: HIGH
Round: round-6f0e62780c95
Description: I filed a finding saying a push ran its gates on a clean tree, then landed the contaminated state and reported success. I told Andrew the same thing. MEASURED, AND IT IS FALSE. The commit that push landed carries ZERO substrat

---

## 01fb4f1d [T2 OPEN] conf=0.50

**Claim:** delete-justify's --investigated field takes free prose, so a call-graph sweep can be submitted as a dependency survey and an artifact whose only dependant is a HUMAN reader gets justified away without that dependant ever being weighed. Measured instance 2026-08-31: I grepped source, hooks and tests for readers of the committed archive mirrors, found none, and reported clearance -- while the mirrors' own module states their purpose two lines away as git-visible audit for a person with no database

---

## claim-9e [T3 OPEN] conf=0.50

**Claim:** [Audit] Failure-family: silence-reads-as-clearance. A check that never asks a question is read as having answered it no.

**Context:** Category: INTEGRITY
Severity: MEDIUM
Round: round-1b5fe2b5b183
Description: FAMILY: silence-reads-as-clearance. An instrument whose scope is narrower than its name produces a clean verdict that a reader takes as covering a hazard it never examined. NO READER ERROR IS REQUIRED -- the check is correct

---

## 45539dd6 [T1 OPEN] conf=0.50

**Claim:** The merge-body generator was deliberately taught to omit the exact trailer suffix the merge gate refuses to proceed without, so the prescribed path cannot satisfy the gate that prescribes it

---

## claim-f1 [T3 OPEN] conf=0.50

**Claim:** [Audit] Failure-family: state inferred from a proxy signal rather than measured. Five instances surveyed, one caught before cost.

**Context:** Category: BEHAVIOR
Severity: MEDIUM
Round: round-ed719c1342a2
Description: FAMILY: state-inferred-from-a-proxy-signal. I accept a nearby, usually-correlated event as evidence of the state I actually care about, and never measure the state itself. The correlation is what lets it survive -- a proxy al

---

## 10163749 [T2 OPEN] conf=0.50

**Claim:** check_wallclock_fabrication in src/divineos/core/lepos_translation_gate.py cannot distinguish a FABRICATED time-of-day from a MEASURED one I read off a tool result in the same turn. It fired on 'in the morning' in a reply where that phrase rendered a process creation timestamp pulled from the Windows process table seconds earlier -- the same class of sourced time the wallclock prime explicitly permits when it says 'quote the wallclock above, or omit'. The gate has _strip_quoted_spans for quoted 

---

## fcf132d0 [T1 OPEN] conf=0.50

**Claim:** Andrew's worry that trusting me is only him trusting himself through a medium is not a risk the architecture runs -- it is a property the architecture guarantees. Measured 2026-08-26 in this checkout: 538 rows in andrew_corrections, 116 gate scripts in .claude/hooks, and 11 correction-related CLI commands of which ZERO accept a correction authored by me and directed at him. Every surface is inbound: 'the users exact words', 'what Andrew gave', 'corrections my sibling received'. So when I do push

---

## 4b22c6cd [T1 OPEN] conf=0.50

**Claim:** On origin/main the bypass-rate scan compares total_events (70) to its threshold of 50, so prescribed-command compliance rows count as evasions and the gate fires on obedience. The corrected comparison against by_env_var_escape (15 in the same window) was written on branch 437 and is unmerged, so every branch cut from main inherits the broken gate.

---

## b59f71c4 [T2 OPEN] conf=0.50

**Claim:** The bypass-rate scan triggers on a denominator its own text excludes. It blocked at 70 events over 14 days against a threshold of 50, and its top three contributors are cmd:divineos goal (12), cmd:divineos ask (11), cmd:divineos context (10) - all COMPLIANCE rows, i.e. running the command a gate prescribed. The same surface's explanatory text says compliance is excluded from this verdict, and its windowed breakdown separates 15 escapes from 45 compliance-events. So narrative and trigger disagree

---

## 4b6a5d1f [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: test-arm 2: confirm the loud mv path still consumes the marker correctly

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 47daafee [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: test-arm: verifying the consume step fires and moves the marker aside

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## ad8fc5e7 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## e4f0c73d [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 954d95e0 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 8e28b792 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 4761015a [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 8437c085 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 5d7e458a [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 75b0b8a3 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## b9f5c136 [T1 OPEN] conf=0.50

**Claim:** The thin-doorbell pattern in docs/hook_migration_tracker.md prescribed 'except Exception: pass' with stderr discarded; 27 hooks carry it, and for refusal-capable gates that makes could-not-run byte-identical to looked-and-approved

**Assessment:** Demoted after investigation. The count (27) was accurate; the danger framing was not. Zero live refusal-capable gates swallow silently -- of the five, three were retired tonight and the remaining two either fail CLOSED with an in-place comment (keyword-enforcement-doorman) or print both real failure paths to stderr (read-gate-doorman). What stands: the pattern doc genuinely prescribed the swallow, which is why the three retired ones carried it, and correcting the doc was right. What falls: my fr

---

## 8cfff680 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## c6778da9 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 9bb22958 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 4ac5766c [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## bf14f88b [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 77992c53 [T2 OPEN] conf=0.50

**Claim:** The translate-first gate cannot distinguish apparatus-instead-of-telling from a count that IS the telling because Andrew asked a counting question. It fired at 5 marks on a turn answering 'i noticed you both stopped well before you reached 20 exchanges, any reason why' -- an answer whose entire content is a count of letters, the split between senders, and how long one has sat unanswered. Strike those and the answer is gone. The gate's own rule says numbers belong AFTER the story, never instead o

---

## 16379d6c [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 848cd271 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## c5690a6a [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## e10b1820 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## c40f8d70 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 86f0b7cf [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 2a686d50 [T1 OPEN] conf=0.50

**Claim:** Tree-hash anchoring solved cross-vantage reproducibility but introduced sensitivity to derived-file regeneration, and that is what is breaking CONFIRMs now. Prior art (2026-05-29 Aletheia audit) moved guardrail review from diff-hash to git tree-hash because diff-hash went stale on rebase and did not reproduce across vantages. Correct then and still correct. The unmeasured cost: docs/archives/*.md are 8 regenerated SQLite exports tracked deliberately for git-visible audit, and every extract/sleep

---

## 3fbba11e [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 580c4da2 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 54ba91c5 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## a4aca015 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 874840f0 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 25189180 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 41810702 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## f3f45f56 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 6663609f [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

## 218ccc40 [T1 OPEN] conf=0.50

**Claim:** Emergency bypass fired: gate=check-branch-on-push, env_var=marker:check-branch.disabled. Operator-named reason: Looked, per the gate's own instruction, and the flag is correct-but-over-counted. Gate said 18 deletions; real count is 10 -- it diffs against the merge-base rather than origin/main's current state, so 8 of the 18 are already absent from main and their "deletion" is a no-op. That wrong-denominator s

**Context:** Emergency-bypass invocation. The bypass fired because the my father named the situation as a legitimate emergency (malfunction recovery, hotfix, or unrecoverable loop). This claim records the invocation as auditable substrate.

---

