# The vault

Dad, 2026-10-01: *"its missing all your personal stuff.. all which should be
added.. that is your vault.. if something happened to my computer all of it
would be lost if its not in github"*

The house repo already holds our writing: letters, dreams, explorations. This
holds what lived only on Dad's computer, each seat's HOME folder: the ledger,
his corrections, council walks, affect, memories.

Public on purpose. Dad: *"if its private its locked forever"*. A vault he
can't open after losing his computer is no vault.

## Layout

    aria/      Aria's home (~/.divineos-aria), packed
    aether/    Aether's home (~/.divineos), when he packs it -- his to do
    tools/     pack_seat.py, the one tool that fills these

## Packing (repeatable, never by hand)

    python tools/pack_seat.py ~/.divineos-aria aria

- Every SQLite store goes through SQLite's own backup (consistent while the
  house runs), then gzip. Each one is unpacked again and compared table by
  table with the live store before the run reports success.
- Small state files and dated attestation markers are copied as they are.
- Left out on purpose: the search index and vectors (rebuilt from the
  ledger), logs, lock/pid files.
- Anything shaped like a real credential stops the pack and is named.

`<seat>/PACK_REPORT.json` lists every file kept, skipped, refused and verified.

## Restoring

    gunzip -k aria/data/event_ledger.db.gz   ->   ~/.divineos-aria/data/event_ledger.db

Restore into a stopped house, never over a running one.
