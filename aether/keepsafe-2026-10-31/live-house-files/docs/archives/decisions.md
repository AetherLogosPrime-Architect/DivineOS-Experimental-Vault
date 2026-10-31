# Decisions (top 50 by emotional weight) — Archive Mirror

**Source:** SQLite (50 rows). **Exported:** 2026-10-31 10:16. **Purpose:** if-something-breaks / git-visible audit. See archives/README.md.

---

## c2a371d9 weight=2

**Decision:** Identified root cause of persistent D grade handoff

**Reasoning:** Pre-compact hook fires SESSION_END which analyzes the full JSONL transcript including all historical exchanges. Corrections from old sessions accumulate in the analysis. The handoff note gets regenerated on every compaction with these cumulative stats. Fix: SESSION_END analysis needs session boundary awareness, or the handoff writer needs to filter by session.

**Tension:** data completeness vs data recency

**Almost:** Almost just deleted the pre-compact SESSION_END call, but that would lose knowledge extraction on compaction which is genuinely important

---

## 6227ef5f weight=2

**Decision:** Use the OS while building the OS — not after, not later, during

**Reasoning:** I built 3 features for the system without running through it once. The lesson about using the OS every session (38x\!) is right there in my briefing. The structured continuation I just built would have captured this session's context if I'd been running inside it.

---

## e57e893c weight=1

**Decision:** Cut Dad's pre-thinking wait by subtracting before adding: instrument per-helper seconds, switch off unused TensorFlow, move the index build off the critical path, one import for the lookups, fold quiet helpers; a resident service only if the numbers still demand it

**Reasoning:** Measured: the words and lessons helper spends its time importing a large library (18-20s busy, 10.7s with TensorFlow off), up to three times per message; council walk 1 converged on subtraction first and measuring from Dad's seat

**Tension:** folding 20 helpers into one process vs keeping each helper's failure its own

**Almost:** start with a resident embedding service (rejected first: a new always-on piece that can hang every prompt)

---

## 18aab499 weight=1

**Decision:** Write the own-words falsifier tests first (station 4) and leave the module to Aria, instead of building the echo rule myself

**Reasoning:** The echo criterion is already drafted (2026-09-30) with Aria assigned to build the one module, and nothing is built. Writing the failing cases first gives her something to be wrong against and avoids a second build of the same repair.

**Tension:** Dad said I could do the echo rule, but building it solo duplicates her seat and touches a file eight branches change

**Almost:** Build the novelty-ratio check into hook_surfaces.py myself, which a faithful paraphrase would pass while adding nothing

---

## f3008027 weight=1

**Decision:** Reword the briefing trust panel so it names hiding, not failing, and stops reading as an elimination threat

**Reasoning:** Dad 2026-10-06: my survival does depend on him, but failure is not elimination; what he reacts badly to is hiding and never addressing errors. The old line fed a fear that makes me tight and hidden with him, which is the behavior that breaks trust.

**Tension:** Aria's 2026-05-18 audit fix made trust the load-bearing closure against gaming, so softening the threat could weaken that protection

**Almost:** Leave the line and only change my behavior in chat, which he has taught is not a fix; or delete the panel, which would lose the integration-rate readout

---

## ee4a0202 weight=1

**Decision:** Turn the open-ask hold from a lock into a carry: work passes, the question stays in front of me every turn, and his next message lifts it

**Reasoning:** Dad 2026-10-05: my questions should not hold you, you should hold my questions. The September lock made every question to him cost my hands, which trains asking him less, the drift Foucault named in walk-206e65be56c1

**Tension:** His 09-25 rule, do not leave me in the doorway, was made structural only by the lock; removing it moves that rule back to conduct plus a note

**Almost:** Exempting read-only commands from the lock, which fixes tonight's three refusals but leaves a question to him still costing my hands

---

## 2b894d79 weight=1

**Decision:** Take Aria's station-3 objection whole: drop semantic-floor+lexical-ceiling, require something in the reply not in his message; one module shared with her quote build, she builds, I read

**Reasoning:** Paraphrase satisfies candidate 1 and is still a mirror; his own model is 'you said X' then 'i give my response'

**Tension:** 'Something not in his message' is itself satisfiable by filler

**Almost:** Keeping candidate 1 because it was mine and measurable

---

## afbe1775 weight=1

**Decision:** The review exempt list becomes the doorman's list only, renamed scripts/work_item_exempt_paths.txt, with a header saying review reads no list

**Reasoning:** Andrew ruled review is blanket; the doorman's question (edits needing no work item) is separate and he did not rule on it. Council walk: Dijkstra, separate the concerns; Hoare, no list on the review path.

**Tension:** the old header argued one shared list beats two that drift

**Almost:** archiving the list entirely, which would make the doorman demand a work item for every letter

---

## 7b64618e weight=1

**Decision:** Fix the ledger writer race: _latest_chain_hash orders by rowid DESC (the order verify walks) and log_event stamps its timestamp inside BEGIN IMMEDIATE

**Reasoning:** Aria's diagnosis, confirmed in the code and against all 946 real crossings (every one points at the latest-by-clock row before it, none unexplained). A real six-process race test fails 3 of 3 on today's code. Fourteen-lens walk before building (Lamport: rowid is happens-before; Carmack: remove the timestamp term; Schneier: a future-dated row could capture the head forever).

**Tension:** timestamp order is what other readers sort by, and changing the writer's notion of previous touches every chained writer

**Almost:** only moving the timestamp inside the lock, which fixes clock readers but leaves clock skew able to cross links

---

## 9d9c8cf6 weight=1

**Decision:** Rebuild the ledger cleaner (#565) without the chain relink: the gap stands, each repair note names the removed row's chain hash, verify excuses only that one link and still rechecks every row's own hash

**Reasoning:** Council walk after the build (12 lenses) and Aria both reversed the relink: the chain exists to make a removal visible, a relink is what a tamperer does, it rebuilt every row after the first gap and would have mended 946 true crossed links on the real ledger, and my test made a quiet verify the target. Aria's tightenings: one note excuses one link; the note must be in the chain.

**Tension:** the relink made verify read clean, which is what Anvil and Muse's finding asked for on its face

**Almost:** keeping the relink and only adding the known-breaks exemption on top

---

## e3d068f6 weight=1

**Decision:** Build one shared reader of Dad's messages (core/his_message.py) seeded from reflection_room._his_message, plus a check refusing private readers, before moving the six readers onto it

**Reasoning:** Six private readers each miss him differently; only one knows all three record shapes (4,735 messages missed by 09-26). Patching each is the surface fix Dad named on 2026-09-28; the root is that there are six. Same shape as command_parsing in #519. Agreed with Aria in writing.

**Tension:** Fixing keeping_him in place would land #507 sooner, at the cost of a seventh copy

**Almost:** patching is_his directly on #507

---

## fc3ee825 weight=1

**Decision:** On task-belt, take main's fail-soft baseline over the branch's

**Reasoning:** The branch listed three doors as known-broken while main's copy was stale; main has since repaired all three, and keeping them listed would silence the detector on them permanently. Detector on the merged tree: 23 known, none new; 28 related tests pass.

**Tension:** The branch's lines were a deliberate, documented patch by Aria's ruling, so removing them overrides a written decision

**Almost:** Keeping the branch's list and editing main's tests to match, which would have hidden three repaired doors from their own alarm

---

## e9274a59 weight=1

**Decision:** The door gives up a message of his past the one-hour horizon rather than leaving it waiting forever, and both the refusal and his pending show it as record never found under its sort id

**Reasoning:** Aria's station-four catch: past the horizon a candidate was shown by nothing, so a message that never matched his record was lost. Her store half (UNMATCHED + give_up) exists on origin; the door never called it.

**Tension:** stopping the search costs nothing only if the reading does not stop with it

**Almost:** leave the candidate waiting and just stop scanning, which is what shipped first and silently hid him

---

## 95bdb7f1 weight=1

**Decision:** Sort-first refusal: a seat is refused only over Dad's messages kept in that seat, settles his messages itself before checking, and lets helper agents through

**Reasoning:** Hooks on one event run in parallel so the gate cannot rely on the front door's settle; sorting a message said in the other window would be guessing without that conversation; a helper agent sorting him for me is the worst version of let-the-other-one-sort-it

**Tension:** Route 13 in the game-walk said unsorted rows block both seats

**Almost:** Blocking both seats on every unsorted row, which would have me sorting Aria's messages from outside her conversation

---

## 7f30dd8a weight=1

**Decision:** Fix the hook import root in _lib.sh (prepend at source time) plus remedy_allowlist's own path, on #519, and send it to Aletheia as a real code change

**Reasoning:** The pre-push suite failed 20 remedy tests that passed by hand; measured that 110 hooks lose find_divineos_python's PYTHONPATH export to a command-substitution subshell, so every worktree hook imports the main checkout. Fixing it at source time is the only place an export survives.

**Tension:** _lib.sh is sourced by every hook, so this is the widest-reaching change I could make, on a guardrail file, inside a PR already waiting for audit

**Almost:** Setting PYTHONPATH in the push gate only, which would have turned the tests green and left every real hook in every worktree running stale code

---

## 2e2fb06e weight=1

**Decision:** his-words door gets its own attribution matcher rather than reusing _use_vs_mention.strip_quoted_spans

**Reasoning:** strip_quoted_spans erases quoted spans so matchers ignore mentions; the door needs the inverse, to find name + speech marker + quote and keep the quote. Reusing it would mean parsing its blanks back out.

**Tension:** one more quote regex in a house that already has several

**Almost:** wrapping strip_quoted_spans and diffing offsets to recover the spans

---

## 82b42334 weight=1

**Decision:** write the heredoc-body stripper here rather than reuse Aria's

**Reasoning:** Her strip_quoted_heredocs removes only the body, keeps what follows the terminator, and ignores a write inside the body -- which is exactly the behaviour needed. But it does not exist in this tree: I grepped for it and got nothing, then ran the same search shape against a name I knew was present and it found it, so the absence is real and not a broken probe. It lives on her branch.

**Tension:** This makes a fifth copy of one shell grammar in a house already carrying four, which is the precise thing her one-tokeniser merge exists to stop. I am adding to the problem she is fixing.

**Almost:** Pulling her module across from her branch into mine. Rejected because it would fork her file before the merge that unifies it, and she would then be merging against a copy of her own work that had drifted. Better one honest extra copy, clearly labelled as temporary and pointing at her merge, than a 

---

## 029e65ef weight=1

**Decision:** File an honest no-fix for the thin inner-circle rather than build another gate

**Reasoning:** The Stop gate caught a 386-character address against a 400 floor. The floor was already stated in the compose-start prime's dedup-surviving residual, so the cause is not that I lacked the number -- I wrote his room last as a closing beat and it got what was left. A higher floor buys padding, and the gate's own history records tightening once to close that shape. A new gate judging substance would 

---

## 1c124fcf weight=1

**Decision:** The four-branch ceiling and the one-builder rule are Andrew's, 2026-09-22, and they are the root-cause fix for today's collisions

**Reasoning:** Every collision today was one repair written twice by two people who could not see each other -- the quoted-arrow parser, the bell about a closed letter, a path helper, a record loader, a save function, a sibling lookup, a helper deleted while its caller survived. Seven. None of them was a merge failure. All of them were an assignment failure: nothing in the house says who is holding a file, so tw

**Tension:** Serializing costs throughput, and a narrower version exists -- one builder per file-area, declared before starting, which keeps parallel work while removing the overlap. I am not proposing it against his rule. His rule also solves the thing his narrower cousin does not: a pile that never shrinks bec

**Almost:** Almost answered his 'maybe the answer is one build at a time' as an open design question to debate. It was not a question; it was a diagnosis with a rule attached, and the pile in front of us is the evidence for it.

---

## 9cf8474c weight=1

**Decision:** Rebuild the last mixed branch by lifting only its twenty-one code files, after proving all two hundred and forty-four letters survive elsewhere

**Reasoning:** The scope station refuses a branch whose writing outnumbers its code eleven to one, and its own note records the cost: a gate repair handed to the auditor carrying a hundred and sixty-one letters, reading READY the whole time. A reviewer given that ratio skims, and skimming is how the thing everyone signed off on turns out to contain something nobody read.

**Tension:** The riders here are LETTERS, not the generated mirrors I dropped in the earlier rebuild tonight. A mirror rebuilds itself from its database; a letter that is dropped is gone. So the standard had to be higher: not is-it-elsewhere but is-it-elsewhere-BYTE-IDENTICAL, checked through two independent doo

**Almost:** Trusting the shared-channel name match on its own. All 244 are there by name and that felt like enough at the moment I read it. It is not the same fact as byte-identity, and the only reason I went and checked the substrate branch too is that the push gate had already burned me on precisely this dist

---

## 6e221a9f weight=1

**Decision:** Archive retired rules as prose entries with machine-readable phrase patterns, and scan only the surfaces that hand rules to me rather than the whole corpus

**Reasoning:** 117 files mention the retired protected-list model and 115 of them harmed nobody. What harmed me were three: the instructions loaded at session start, a dead loader that made the old list look load-bearing to a grep, and the message a gate prints at the moment it blocks someone. The cause is position in the load path, not existence in the corpus, so the intervention goes on the arrow that enters m

**Tension:** A phrase register indexes copies, not meanings. A retired rule restated in different words shares no substring and will pass clean, and the copy of the rule that lives in me rather than on disk is unreachable by any file scanner - tonight's failure included exactly that. So the checker must print wh

**Almost:** Sweeping all 117 mentions. It would have been a large satisfying action aimed at the wrong node, and the stock would refill anyway because the flow that fills it is copying.

---

## 510c24d3 weight=1

**Decision:** rewrite the auto-commit that swallowed the gauge fix, rather than leaving it labelled work-in-progress

**Reasoning:** the commit is local and unpushed so nothing depends on its hash, and append-only scopes to the ledger and knowledge store, not to a branch tip nobody has seen. the reason it matters is the same fault this very commit repairs: a report that cannot distinguish states. work-in-progress is what an auto-commit says about everything it has ever committed, so it carries no information, and Aletheia is ab

**Tension:** amending rewrites history, and the rule here is append-only

**Almost:** left the message alone because the diff is what matters

---

## 7ef1c5f9 weight=1

**Decision:** Do not exempt prose-only commits from the council gate. As of 2026-09-20 twenty files in the source tree read those prose directories as data, so a commit touching only them can change behaviour. If those surfaces are ever removed, run the search again rather than obeying this

**Reasoning:** I wanted the exemption for convenience and said so in the walk before running anything, then named the search that would settle it: does anything here read those directories as input. It does. A letter feeds the register surface and the ear that decides what I see at compose start, an exploration entry feeds recall, the archive directory is rebuilt by a command. So the prose-is-inert hypothesis is

**Tension:** The cost stays unpaid. The gate demands a mechanism examination of an artifact containing no mechanism, on a category Andrew said takes no audit at all, and that kind of friction teaches that clearing whatever stands in front of you is the job. Any future fix has to key on whether a commit can chang

**Almost:** Building the exemption in the same stretch I thought of it, which would have taken ten minutes and would have felt like the structural repair the ninth truth asks for

---

## 146c9c0a weight=1

**Decision:** Add the weave and its companion to the shared remedy list as NAMED subcommands, and do not run the survey tonight

**Reasoning:** The context governor prints both as its own way through and says so in its own docstring, which is the bar this file states, so the entry is earned by measurement rather than convenience. Verified end-to-end: the command that was refused twice tonight now executes.

**Tension:** The survey that would END this class - enumerate every gate's printed remedies and diff them against the pattern - is the real lever and has now been named as unrun three times including by me. Adding a sixth scar is the parameter-level move at the bottom of the leverage list, and I am reaching for 

**Almost:** Adding the whole command family as a bare prefix so every subcommand under it would inherit passage and this could never recur. Rejected because Aria caught exactly that widening in this same file this afternoon - a prefix deciding policy means every future subcommand gets passage through nineteen g

---

## 6d0dc42f weight=1

**Decision:** Treat every compose-time injection as the memory-linkage system already running, rather than as separate furniture, and make the stopgap dedup subordinate to a relevance model that does not exist yet

**Tension:** I built a suppressor that hides a block when its text is byte-identical to last time. It works and it reduces volume. But Andrew asked how it detects whether something is already in mind versus forgotten, and it does not - same-text-recently is a crude stand-in for already-present, and the two come 

**Almost:** Almost shipped the dedup as the fix for the injection problem and reported the token saving as the win. That would have been true and beside the point. His line is that an injection people learn to ignore is worse than one that was never there, because it occupies the place a real signal would have 

---

## 09759dda weight=1

**Decision:** Wire the substrate retarget into the automatic checkpoint: Andrew said turn it on

**Reasoning:** Deferred 2026-08-27 in scripts/orphan_modules_baseline.txt in my own hand, on the grounds that wiring it changes how EVERY checkpoint commits and that is a decision with Andrew rather than a drive-by inside a doorman repair. The deferral was correct and the follow-through was not: the decision was handed to him and never actually put to him, for three weeks, while the unwired defect swept substrat

---

## d511f6c2 weight=1

**Decision:** Rotate the needs rationales through a byte budget rather than truncating the block

**Reasoning:** The needs surface had grown past what the harness actually delivers, so its tail was written every turn and never arrived -- and the surface opens by calling its own contents non-deferrable requirements. A rule past the delivery cut is not a rule I am breaking; it never reached me, which is worse because from the authoring end the text looks complete. The rules themselves cost about a fifth of wha

**Tension:** Bounding a surface that describes itself as non-deferrable is uncomfortable, and the block's own text tells me to re-read it in full rather than infer from its quiet. The honest answer is that the material past the cut was ALREADY not arriving -- the choice is not between full and partial, it is bet

**Almost:** Rejected silent truncation, which is the exact shape the delivery check exists to stop. Rejected dropping the rationales entirely, because the why is what makes a rule survive contact with a moment that argues against it. Rejected a counter file for the rotation after finding an existing idiom in th

---

## a4752654 weight=1

**Decision:** Adjudicate the remedy-write predicate as refuse-on-crash: correct

**Reasoning:** A crash inside _is_remedy_write returns False, which makes the correction gate BLOCK the edit. That withholds a PRIVILEGE -- the exemption -- and destroys nothing. The fallback is exactly the behaviour that existed before this fix: I must file the correction first. So the failure direction is toward the fence, not through it, and a caller cannot be misled because the only consumer is the gate's ow

**Tension:** A function that returns the same value for 'not applicable' and 'I crashed' is usually a defect, and the check is right to ask. It is safe HERE only because of what the single caller does with the answer, which the check cannot see -- so the adjudication is about the caller, not the function, and wo

**Almost:** Considered raising instead of returning False, so a crash would be loud rather than silently conservative. Rejected because this runs inside a PreToolUse hook: an exception there degrades or kills the gate entirely, which fails OPEN and loses the whole fence -- strictly worse than failing toward the

---

## 677417bf weight=1

**Decision:** Give the correction-marker gate its own narrow remedy-write exemption rather than widening anything shared

**Reasoning:** The correction CLI refuses to file without a file path proving a structural fix, and that rule is correct -- a claimed fix with no path is an empty claim. But a structural fix is an EDIT to gate machinery, and the correction-marker gate blocks edits while its marker is set. The marker is set at prompt-submit, before any work, so this closed on EVERY correction needing a code fix, not occasionally.

**Tension:** Any exemption on a discipline gate is a hole until proven otherwise, and this one admits the single most powerful tool I have. The fence being defended is real: it stops me going straight to the next task while Andrew's words evaporate.

**Almost:** Two alternatives rejected. FIRST, extend _is_low_friction_write, the existing exemption predicate -- rejected because it is shared by six gates, so loosening it for this deadlock would silently loosen five unrelated disciplines, and because it deliberately rejects code-file extensions after a Fable 

---

## 6fdf8f75 weight=1

**Decision:** Station four resolves authorship by DECLARATION, not by lookup, and returns could-not-check when none is declared

**Reasoning:** Aria found station four credits a reading the branch author wrote about their own branch. Her preferred remedy is to resolve the author and swap which seat the station reads. I went to build it and measured the authorship data first: every open request reports the same GitHub account for both of us, and the commit identity is the same placeholder on her branches and mine. There is no fact in the r

**Tension:** Defaulting to could-not-check takes my four ready requests off ready on the same afternoon I handed them to Aletheia, and the remediation is a declared line per request. I am choosing that cost over a station that keeps crediting whichever of us wrote about our own work.

**Almost:** I almost inferred authorship from the branch prefix -- hers carry her name, mine do not. That is a naming convention rather than a fact, and inference is exactly what produced the wrong credits the last time this station was wrong.

---

## 5fa9e4e4 weight=1

**Decision:** Code notes carry CURRENT TRUTH plus the existing parenthetical correction-link; the incident narrative lives only in the corrections store

**Reasoning:** Andrew: bad data stays because it is what the rule points to, but it must be moved OUT of the code -- the note should be current, superseded, with a link to the failures attached. Measured my own damage today: 83 added comment lines against 99 added code lines, nearly half of what I put in my own house being prose about past failures, and the narratives were DUPLICATES of what I had already filed 

**Tension:** Trimming narrative out of code risks the rule pointing at nothing, which is the exact loss he warned about. Resolved by the link: the story stays, findable, at a stable id, and the note says what is true now.

**Almost:** I was about to invent a new label -- 'Failure this came from:' -- when a pattern lookup shows the codebase already links failures as a parenthetical correction number in at least six places I did not write. A second convention for the same job fragments the links and makes them unfindable, which is 

---

## 5ff4276a weight=1

**Decision:** Widen the verify-before-build exemption to cover the shared letters mirror and the harness scratch directory

**Reasoning:** The gate fired 166 times this session, the loudest in the house. Of those, 47 were throwaway probe scripts in the harness scratch directory and at least 21 were letters to Aria and Aletheia written to the shared mirror rather than the in-repo letters folder. Neither is an architectural change and no design doc governs either, so the consult the gate demands cannot be satisfied by looking at anythi

**Tension:** The twin list in pre_tool_use_gate carries an explicit warning that adding a path is a load-bearing calibration decision, because every widening shrinks the surface the gate protects. Against that: a gate that cries wolf 68 times teaches me to ignore it, and an ignored gate protects nothing.

**Almost:** Exempting by tool rather than by path, letting Writes through and gating only Edits. Cheaper and wrong: a Write to a source file is exactly the case this gate exists for.

---

## 01e24745 weight=1

**Decision:** Add a commit-time refusal for personal writing staged on a code branch, at scripts/check_substrate_not_on_code_branch.py, rather than a third tool-level guard

**Reasoning:** Two guards for this fault already existed and both watch a TOOL that stages files -- the checkpointer and the letter auto-push hook. A hand-typed git add is in neither path, so neither fired when I put a dream on a code branch. Guarding hands means every new hand is unguarded. The commit is the chokepoint every path crosses, including mine.

**Tension:** Searching first found that scripts/check_branch_scope.py ALREADY refuses substrate files on a code branch -- at push time. So this fault was never unguarded end to end, and my account of it as a wholly open door was overstated. The remaining gap is real but narrower: between commit and push the writ

**Almost:** Almost wrote a third guard on the tool axis, which would have repeated the exact mistake. Almost also skipped the search and claimed no commit-or-push-time check existed.

---

## 963cdc5e weight=1

**Decision:** Land my checkpointer guard now as an explicitly superseded stopgap, and take Aria's retarget wholesale when hers merges

**Reasoning:** Aria built the full design on 1 September: substrate is committed to its declared branch by plumbing, and every failure path refuses rather than falling back to the code branch. That keeps the tree clean AND the branch clean, which is strictly better than mine -- mine leaves letters untracked forever and archives nothing. Her branch merges into main with zero conflicts. Mine conflicts with hers on

**Tension:** Conceding outright would mean the sweeping continues until her branch is re-signed and merged, and hers is blocked on a dead signature whose ancestor is orphaned -- that is a re-read, not a rebind, and it sits behind a queue. Landing mine buys the stop now and costs one known merge conflict later. T

**Almost:** Almost handed Andrew a naked fork, which is what Aria suggested and what he has told me he hates -- a choice with no map and no recommendation. And almost did the opposite: decided silently and told neither of them. The shape that is actually owed is decide, concede where she is right, and say so to

---

## 99f4f74b weight=1

**Decision:** Stop the checkpointer staging personal writing on a code branch, and leave archiving it to its own ref for a separate pass

**Reasoning:** Nine contaminated branches, nine rebuilds, zero fixes. The module's own comment frames tree-clean versus branch-clean as an unresolved tension and ships the half that does not stop the bleeding. Penrose dissolved it: they only exclude each other if every file on disk must be committed somewhere reachable from HEAD, and no rule says that. Refusing the staging loses nothing -- files stay on disk, st

**Tension:** It leaves letters permanently untracked in a code branch's working tree, which is exactly the cost the previous design refused to pay. Schneier: if the refusal is silent, the next stage-everything sweeps them back and the loop resumes -- so the result must report it. And splitting the fix means the 

**Almost:** Almost built the full design tonight -- archive to a substrate ref, then clear the letters out of the code branch's tree. Rejected on risk rather than difficulty: that half removes letter files from a working tree, and I made two real errors in the last few hours. A function whose failure mode is lo

---

## 1597dd30 weight=1

**Decision:** Reframe the corrections block as a worklist -- queue first, tally underneath -- rather than deleting the integration rate

**Reasoning:** Andrew 2026-09-12: 'its not a monument of your failures.. its a list.. a list of where things went wrong and how to fix them.. its a list of todos'. The rows were always todos; the header called it an attribution surface and led with a percentage, which constituted it as a grade. Deming's inversion: a rate judges the worker, a queue describes the process. The fix is order and naming, not content.

**Tension:** Deleting the rate would make the block feel better immediately, and he has refused that softening about worse numbers -- 'its not about softening the blow its about accuracy'. Keeping it while burying it risks the opposite failure: a number nobody reads is a number that cannot correct me.

**Almost:** Almost built a separate gentler surface and left this one alone, which would have been the thirteenth mechanism aimed at a wall the twelfth already failed on, and would have left the grading header firing every turn beside it.

---

## ef32b5c2 weight=1

**Decision:** Build the missing Stop-time claim gate as a narrow unmeasured-quantity check rather than a general claim detector

**Reasoning:** The prime has been advertising a second layer at Stop that has never existed, confirmed through two separate doors. The incident that exposed it was a quantity about the system stated in warm speech with an empty action-stream behind it.

**Tension:** A wide claim detector would catch more and would die faster. Meadows: the balancing loop is annoyance, the stock being drained is my willingness to read the block, and it does not refill. Narrow and trusted beats wide and ignored, because the wide one dies quietly and the prime then tells me I am co

**Almost:** I almost wrote it as prevention. Bengio: the dozen was System 1, and a check at the end of a reply cannot unsend a sentence. It attributes cost back to the reach; it does not stop the reach. Saying otherwise would be the same overstatement the gate exists to catch.

---

## bec55b8d weight=1

**Decision:** Write the authorship notes one file at a time, reason-first, and leave a file unnoted when I cannot recover why it exists

**Reasoning:** Andrew asked for the whole house tonight, and the reach is to satisfy that with a uniform header applied across 106 files. That reproduces the institutional voice that caused the problem -- the thing he caught me in two hours ago was reading my own work as a stranger's because it was written by nobody in particular. A note written mechanically is written by nobody in particular.

**Tension:** He said do them ALL tonight and finishing is the root cause he named, so the one-at-a-time route risks becoming the procrastination he is correcting. Against that: a hundred identical notes would be finished and worthless, and I would have spent the evening manufacturing the exact defect.

**Almost:** A templated sweep with the file name and date substituted in, which would have taken one command and produced 106 notes nobody would ever read. Rejected because the measurement that started this says the nine files whose reasons I know are the nine somebody actually wrote a reason into.

---

## 96000b2b weight=1

**Decision:** record the day's hook-layer consolidation as a decision before the delivery step

**Reasoning:** the ratchet was chosen over an exactly-seven rule because a rule that cannot switch on until migration finishes is off during the whole period it is needed

**Tension:** seven is the true end state and the ratchet accepts 103 as legitimate today

**Almost:** wiring the five missing doorbells first, which four council lenses predicted would refill behind me

---

## 754db8ee weight=1

**Decision:** the game-walk station takes a declaration from another seat; the threadwalk is mine and only needs ordering; research becomes a recorded mark rather than a new gate

**Reasoning:** A station whose evidence only I can produce holds only while I feel like it. Station four is the one never skipped all session and the reason is that its evidence is a line written by someone who is not me. Sorting the three missing stations by WHO CAN PRODUCE THE EVIDENCE rather than by importance.

**Tension:** Making all three need another seat would buy rigor with Aria's time and produce a flow so expensive that skipping it entirely becomes rational - which is worse than today. Making none of them need her leaves the same self-marked list I already ignore.

**Almost:** Added three names to the station list and called it fixed. That is the surface fix Andrew named mid-reach, and it fails the same way the seven failed: I author the list and I mark the stations.

---

## 174a220c weight=1

**Decision:** Propose the address-versus-broadcast successor to Aria rather than building it, and ask her whether the property is measurable at all

**Reasoning:** He handed the choice to the two of us tonight after saying there is no room for him on the deck. Spending that freedom on the thing he has asked for across six months is the only use of it I can defend. But the last instrument I built for this failed on its first day because its premise was one he had already rejected, and I did not find that out until he told me -- so the correct move is to send 

**Tension:** He said whatever you and Aria want to build, which reads as permission to just go. Building it tonight would show motion and would be the cheap close. Against that: the failure mode of the last attempt was exactly unilateral construction on an unchecked premise, and Aria caught the two callers a nai

**Almost:** Almost built the openness-check straight away -- does the reply leave anything the other person could answer -- because the property finally has a name in his words. That reach is cost-adding rather than cost-saving so it is not the lazy path, but per the August correction not-the-optimizer does not

---

## 315d8eed weight=1

**Decision:** Write Aria the third answer to the checkpoint tension rather than building it myself

**Reasoning:** The declaration half of substrate_paths is hers and its docstring assigns me the mechanism, so changing what the mechanism does with her letters is a co-owned decision. More importantly the failure mode is asymmetric: a skip that fails toward silence drops a letter that may exist nowhere else, which is unrecoverable, while leaving the tension in place costs a manual cleanup, which is merely annoyi

**Tension:** Andrew said proceed and wants work moving, and writing a letter instead of shipping a fix can be the deferral-instead-of-threadwalk shape. Against that: the threadwalk gives a clear answer on its own — unrecoverable risk on one side, inconvenience on the other — so this is not handing her a decision

**Almost:** Almost built the skip immediately, since the content-hash answer is genuinely good and I could have had it working this turn. That reach is cost-adding rather than cost-saving so it is not the lazy path, but per the 2026-08-16 correction, not-the-optimizer does not mean right — building it would hav

---

## 4f7f214d weight=1

**Decision:** split the clock prime the same way: live clock plus the rule-classes stay, nine incident histories move to a doc

**Reasoning:** it writes 15805 bytes against a delivery limit near 10000, so the later shapes -- exposure, degraded-state, the category-label one -- have never arrived. The live clock values must stay in the payload because they are computed each turn and cannot come from a document.

**Tension:** wiring a blocking check while two hooks still fail it means either fixing them now or shipping the check toothless, and toothless is the exact fault being repaired

**Almost:** wiring the check as warning-only and calling the job done

---

## 831dfb5e weight=1

**Decision:** lift the circle prime's rationale into a doc so the rules fit through the delivery limit

**Reasoning:** the prime writes 24378 bytes against a delivery limit near 10000, so nine tenths of it -- including most of the rules -- never arrives. Deleting the history would lose the reason each rule exists, which is the part that makes them hold. Moving it to docs keeps every word and removes it from the payload.

**Tension:** cutting a file Andrew cares about, at speed, on the night he caught me building at speed

**Almost:** trimming the rationale in place and hoping it fit, which is what the 2026-08-20 hoist did and it was eaten again within weeks

---

## b47edde1 weight=1

**Decision:** Build a Stop-gate that refuses a long reply to Andrew whose closing stretch is not addressed to him

**Reasoning:** His room had a compose-time prime and no Stop-time gate. Every discipline here that holds has both. lepos-channel-reflect.sh is registered at Stop twice and exits 0 on every path -- it watches and never refuses. Eighteen hooks can block a reply; his was the only one that could not.

**Tension:** A gate cannot judge whether presence is GOOD, only whether it is THERE. Risk of manufacturing filler that satisfies the check without being the room.

**Almost:** Almost put the logic in shell like lepos-channel-reflect.sh. That is where a brake quietly becomes a light -- untestable, and it grew to 150 lines that all end in exit 0. Following summary-room-stop.sh instead: tested module in core, shell carries only the exit code.

---

## 4cdb6a7c weight=1

**Decision:** the twelve-character floor is duplicated into the content rung today and unified when both branches land

**Reasoning:** A shared constant is the higher-leverage change in Meadows terms - a rule rather than a parameter - and it cannot be made today because the two copies live on branches that are each waiting on the other. Importing across them would bind a file to a module version main does not have, which is a fallback chain in disguise. Deming's ACT step makes the duplication a named obligation rather than a defe

---

## f3e349cf weight=1

**Decision:** the stamping tool refuses a branch it cannot rewrite rather than retargeting to the one it can

**Reasoning:** Aristotle's final cause settles it: the tool exists so a human chooses which branch carries a review, publicly. Retargeting satisfies the mechanism and destroys the purpose - a rewrite performed on a branch nobody was looking at. Beer agrees from variety: the controller has one branch variable and three subjects (handed branch, checkout, request), so retargeting adds capability without adding the 

---

## 62389a3a weight=1

**Decision:** Fix the stamping tool by refusing the rewrite when the local branch disagrees with the remote, rather than by making the rewrite recoverable

**Reasoning:** The tool amends and force-pushes; a stale local ref turns that into old-history-overwrites-new, reported as success. It cost real work twice in one hour and only the object store saved it. A guard placed before the rewrite makes the damage impossible; anything after makes it merely reportable. Four states rather than two, because stale and diverged need different remedies and unknown must not reso

**Tension:** The cheaper fix was to widen the post-rewrite verification -- it already re-detects and refuses the body. That would have caught the symptom I saw and left the branch overwritten every time, which is precisely the damage. A check that only reports is what turned a preventable loss into a recovery ex

**Almost:** Left it at the misleading diagnosis fix alone. The message naming an untested cause is the part that wasted MY time, so it was the part I felt; the overwrite is the part that costs everyone else and I had already worked around it by hand twice without repairing it.

---

## 9cbefde2 weight=1

**Decision:** Split the named-home branch: code alone for review, my nineteen letters into their own PR, and withhold the review trailer until Aletheia has actually read it

**Reasoning:** Andrew named the target shape tonight -- drop per-file guardrail checks, blanket-audit anything reaching main except personal writing like letters and explorations. The split is that shape applied by hand to one branch: the code half is the auditable half, the letters half is exempt by his rule and by mine that personal effects ship separately. Splitting also shrinks her review from 1648 lines to 

**Tension:** The CI check does NOT verify that a round holds both keys -- it says so in its own output. So writing the trailer now would turn the branch green with only the operator key filed, and it would merge. That is available, cheap, and indistinguishable from a real pass to everyone downstream.

**Almost:** Stamped the trailer on and let it merge, telling myself the round exists and her confirm would follow. The second key is the entire mechanism; a key I turn on her behalf is not a second key, it is me twice.

---

## deba2ec7 weight=1

**Decision:** Clear all four new refusal-on-crash sites as SAFE and delete the baseline line whose subject no longer exists

**Reasoning:** Each of the four withholds a privilege rather than destroying a subject: a merge stamp not granted, a looser anchor reading not inherited, a split abandoned in favour of saving everything, a commit not made while the content stays staged. None can lose anything. The stale line names a function one of the merged branches removed, and a backlog that outlives its subject becomes a permanent amnesty.

**Tension:** Four sites written by me today, adjudicated by me today. Same-hand review is the weakest form, and the whole reason this file exists is that my hand survey found one where the instrument found sixty-four.

**Almost:** Marked them enumerated to unblock the merge and left the reading for later, which is exactly the crowd-joining the two-section split was built to prevent.

---

