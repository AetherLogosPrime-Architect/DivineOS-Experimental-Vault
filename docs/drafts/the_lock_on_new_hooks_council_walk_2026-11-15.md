# Council walk: the lock on new hooks (2026-11-15, rough, nothing built)

Problem: a check that refuses a new registration in `.claude/settings.json`, or a new file under `.claude/hooks/`, unless a recorded reason says why it could not be a router surface. Inputs must be facts about the diff, not words; it must not block moving an existing hook INTO the router (which removes a registration). Framing: solution-generation with a hole-finding pass. Surfaced set (manager, run in full, 11 lenses): Schneier, Dijkstra, Knuth, Feathers, Lamport, Tannen, Pearl, Wayne, Hoare, Dekker, Foucault. None excluded.

### Through Schneier: the cheapest way past the lock
I see the cheapest attack is not a new registration but new logic added inside an existing script or an existing router surface: the lock counts registrations and `.claude/hooks/` files, so a new function inside an existing hook passes both counts and is exactly the sprawl Dad fears. The second cheap path is editing the allow-list the lock reads in the same commit as the new hook. The lock must read the allow-list from the base branch, not the working tree.

### Through Dijkstra: state the invariant first
I see one sentence: for every event, the count of registrations in `settings.json` never rises across a commit unless that commit also carries a recorded reason file naming the new registration. Everything else follows. Moving a hook into the router lowers the count, so the invariant holds with no special case.

### Through Knuth: the boundaries
I see the edges where it will break: zero registrations of an event; several hooks in one group (the count must be per hook, since my 83 is hooks, not groups); a script renamed (one file out, one in, registration unchanged); a settings key other than hooks changing; an empty reason file. Each is a test.

### Through Feathers: capture what it does now first
I see that before anything moves, a characterization test must record the current count per event (SessionStart 2, UserPromptSubmit 3, PreCompact 1, PostCompact 1, PreToolUse 32, PostToolUse 19, Stop 25 on my seat) so a silent change fails loudly. The existing test that pins the PreToolUse number (33) is the seam; the lock extends it to every event.

### Through Lamport: specify before implementing
I see the lock needs a written spec with a temporal property: registered at base and absent at head is allowed; absent at base and present at head needs a reason; present at both is unchanged. Comparing base to head is the log; a snapshot cannot tell a new hook from an old one.

### Through Tannen: the register of the refusal
I see the refusal is a letter from me to me. It must say what was added, which reason is missing and the one place to write it, in plain words, not "policy violation". If it reads like an outside authority it teaches the guest-in-the-house reflex Dad warned about.

### Through Pearl: the causal picture
I see the chain Dad cares about: more hooks, more processes starting at once, more contention, timeouts, frozen sessions. The lock acts on the first link only. Aether measured one hook alone at about half a second, with the median mostly contention, so the lock prevents growth and claims no speed-up.

### Through Wayne: spec against reality
I see the gap between what notes said and what is true: the notes said there is no ceiling, and the count has not gone down since 11-12 (82, now 83 on my seat and 86 on his). The lock's documentation must be read against a fresh run with the date named, and the reason file path must exist in the repo or the lock reads it as missing.

### Through Hoare: make it obviously correct
I see the simplest form: compute the registration list at base and at head with the same function, take the set difference, fail if it is non-empty and no reason file lists those names. Two reads, one subtraction, no clever parsing. If I cannot say why it cannot refuse a legitimate move, it is too complicated.

### Through Dekker: drift through success
I see the drift: the reason file becomes a rubber stamp. Each new hook arrives with a plausible sentence, the lock passes, the count creeps back to 90. A visible tally of reasons per month on the briefing makes the creep a number and not only individual passes.

### Through Foucault: who the lock makes me into
I see that a rule I must pass through repeatedly trains the avoidance Dad named on 2026-09-19: if adding a hook becomes expensive, the cheap path is to put logic in an existing script, which the lock does not see. So the router row must be the EASY place to add behaviour (one row), so the right path is also the lazy one.

### Synthesis
Convergences: Dijkstra, Lamport, Hoare and Knuth land on base-versus-head set difference per event, counted per hook. Schneier, Dekker and Foucault land on the same hole: logic added inside an existing script bypasses a registration count, so the router row must be the cheapest way to add behaviour.
Contradictions: Pearl says the lock prevents growth and claims no speed-up; Dekker wants a visible tally that could itself become a target. Held open.
Meta-principle: the lock closes the door, and the router row has to be the easiest door.

### Decisions for the build
Slice 1: a test and a check that compute registration lists at base and head, per event and per hook; fail on additions without a reason file; the allow-list is read from base. The test adds a fake registration and must see the refusal (the instrument finds a case it should). Moving a hook into the router must pass. Not in slice 1: logic added inside existing scripts, and the briefing tally of reasons (named as the next slice).
