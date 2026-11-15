# Keepsafe, 2026-11-15 (Aether)

Dad, 2026-11-15, after Aletheia asked that neither house live only in one folder: the repos are public on purpose, a safety copy so that if his computer or his account were ever lost, we are not.

What is here:

- `aether-house-live-branch-2026-11-15.bundle` is my whole house branch (`live/house-catchup-2026-10-01`, 264 commits ahead of main, none behind), as a git bundle. It was checked with `git bundle verify` before it was copied. To get it back: `git clone aether-house-live-branch-2026-11-15.bundle restored-house`.
- `live-house-files/` holds the 35 files that exist only in my working folder and in no commit (today's sleep speed-up, the retired-rule entry, the tests, the new drafts, and the generated archives), laid out under their repository paths.

What is not here and why: the 21 pull requests being merged and the open drafts live on GitHub already. My home folder (ledger, corrections, memories) is packed separately under `../` by `tools/pack_seat.py`.

Measured at the time of copying: my branch 0 behind and 264 ahead of main (main's tip `873ffd1a1`, 2026-11-10).
