# Recombination does one matrix and one transaction, not two million pairs and thirty thousand commits

Draft, 2026-11-15. Aether. Reach `reach-b698416984cd` (no code prior art; prose prior art: the 2026-06-24 perf fix that moved embedding out of the pair loop, which this continues). Not walked, not built, nothing pushed.

## Why (Dad, 2026-11-15, 1:18 PM)

*"first 94 seconds for extraction and 770 for sleep seems like a long time, we should see if theres any way to streamline it or make it more efficient as it will only get worse"*

## What I measured (read, not guessed)

Per phase, run alone: consolidation 1s, pruning 2s, affect 1s, maintenance 17s, **recombination 719s**, curiosity 9s, the rest 1s each. Recombination is 96 percent of sleep and runs past the 600-second timeout `run_sleep` gives a subprocess phase.

Inside recombination, over 2,201 eligible entries (2.42 million pairs):
- the word-overlap check runs on EVERY pair before the meaning check: 63 microseconds each, about 153 seconds;
- the meaning check as one matrix multiply: 0.01 seconds (embedding all entries: 1.5 seconds);
- only 33,552 pairs fall in the similarity band; for each, `find_edge` opens a database connection (up to twice), and each already-known pair does `strengthen_edge`, which opens another. Measured: one `find_edge` call costs 12.9 ms, almost all of it the house's connection helper (a bare sqlite connect, update and commit on a throwaway file costs 0.2 ms). 33,552 pairs times one to three connection opens is the rest of the 719 seconds. I first guessed it was the commits; the measurement said the commit is not the cost, the opening is (walk finding, Dillahunty 2).

It grows with the square of the entry count, which is why it "will only get worse".

## What this changes

1. The meaning check becomes one matrix; band pairs are selected from it; the word-overlap check (kept, same threshold) runs only on band pairs, not all pairs. The two conditions were already ANDed, so the set of pairs that pass is identical.
2. Existing RELATED_TO edges are read ONCE into a lookup (both directions) instead of one query per pair.
3. The Hebbian strengthening of already-known pairs is one transaction with one commit, same delta, same cap at 1.0, same "counted as strengthened only if confidence grew".
4. Pairs that involve an entry whose embedding has zero length keep the old per-pair path (rare), so nothing is silently dropped. When the embedding model is not available the old Dice loop stays as it is.

## Two guards the walk added

- If the lookup of existing edges cannot load, the phase records an error and stops. It never goes on with an empty lookup, because that would count every known pair as new (Hoare). Tested by making the lookup raise.
- The sleep report gets `phase_seconds`, one number per phase, printed in the summary, so a slow phase shows itself instead of waiting for Dad to ask (Norman).

## What does not change

Same filters, same band, same order of results (row-major over the entries), same report fields, same edges persisted. The existing recombination tests in `tests/test_sleep.py` are the characterization: they must pass untouched.

## Tests that must fail first

1. A candidate-selection test: on random unit vectors, the matrix selection equals the brute-force pair loop exactly (same pairs, same order).
2. A transaction test: strengthening many edges in one call matches strengthening them one by one (same final confidences, cap at 1.0, missing ids ignored), and uses one commit.
3. An index test: the edge lookup finds an edge in either direction and ignores INACTIVE ones.
4. A budget test on the phase: with a few hundred entries the whole phase runs inside a fixed small number of database connections (counts opens), so it cannot quietly drift back to one connection per pair.

## What the tool decides and what stays mine

The matrix only decides which pairs are in the band; whether a connection means something stays with whoever reads the dream. What ends it: if entries grow past what a full matrix holds in memory (about 20,000 entries is 1.6 GB), block the matrix in chunks of rows; named now, not built, since at 2,201 entries it is 19 MB.
