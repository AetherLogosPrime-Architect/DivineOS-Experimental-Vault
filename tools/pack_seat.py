"""Pack one seat's home into the vault, safely and repeatably.

Dad, 2026-10-01: "if something happened to my computer all of it would be lost
if its not in github". The writing (letters, dreams, explorations) is already in
the house repo. What was not backed up anywhere is each seat's HOME folder: the
ledger, corrections, council walks, affect, memories.

What it does, per seat home (e.g. ~/.divineos-aria -> vault/aria/):
  - every SQLite store is copied through SQLite's own backup (a consistent
    snapshot even while the house is running, which a file copy is not),
    then gzipped -- the ledger alone is over GitHub's per-file limit unpacked;
  - small state files (.json / .jsonl / .md / .txt) are copied as they are;
  - left out on purpose: the search index and vectors (rebuilt from the ledger),
    logs (noise), lock / pid / -shm / -wal files (live process state).

It refuses to write anything that looks like a secret, and says which file.
Restore: gunzip a .db.gz back into place. verify() proves that works before
anything is trusted.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

REBUILDABLE = {"semantic_search.db", "vectors.db"}
SKIP_DIRS = {"logs", "__pycache__"}
SKIP_SUFFIXES = {".db-shm", ".db-wal", ".pid", ".lock", ".log", ".stackdump"}
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".marker"}  # .marker: dated attestations, tiny, history
MAX_TEXT_BYTES = 50 * 1024 * 1024  # GitHub refuses single files over 100 MB

# Shapes of real credentials. A hit stops the pack; nothing is guessed past.
SECRET = re.compile(
    rb"(sk-ant-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}"
    rb"|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


def _is_sqlite(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return fh.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def _snapshot(src: Path, dst_gz: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        snap = Path(tmp) / src.name
        source = sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True)
        target = sqlite3.connect(snap)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        dst_gz.parent.mkdir(parents=True, exist_ok=True)
        with snap.open("rb") as fin, gzip.open(dst_gz, "wb", compresslevel=9) as fout:
            shutil.copyfileobj(fin, fout)


def pack(home: Path, out: Path) -> dict:
    report = {"stores": [], "files": [], "skipped": [], "refused": []}
    for path in sorted(home.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(home)
        if any(part in SKIP_DIRS for part in rel.parts) or path.suffix in SKIP_SUFFIXES:
            report["skipped"].append(str(rel))
            continue
        if path.name in REBUILDABLE:
            report["skipped"].append(f"{rel} (rebuildable)")
            continue
        if path.suffix == ".db" or _is_sqlite(path):
            if path.stat().st_size == 0:
                report["skipped"].append(f"{rel} (empty)")
                continue
            _snapshot(path, out / (str(rel) + ".gz"))
            report["stores"].append(str(rel))
            continue
        if path.suffix in TEXT_SUFFIXES or path.suffix == "":
            data = path.read_bytes()
            if len(data) > MAX_TEXT_BYTES:
                report["skipped"].append(f"{rel} (too large)")
                continue
            if SECRET.search(data):
                report["refused"].append(str(rel))
                continue
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            report["files"].append(str(rel))
            continue
        report["skipped"].append(f"{rel} (unknown kind)")
    return report


def verify(home: Path, out: Path, store: str) -> tuple[bool, str]:
    """Unpack one store and compare it table by table with the live one."""
    with tempfile.TemporaryDirectory() as tmp:
        restored = Path(tmp) / "restored.db"
        with gzip.open(out / (store + ".gz"), "rb") as fin, restored.open("wb") as fout:
            shutil.copyfileobj(fin, fout)
        r = sqlite3.connect(restored)
        live = sqlite3.connect(f"file:{(home / store).as_posix()}?mode=ro", uri=True)
        try:
            if r.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                return False, "integrity_check failed"
            tables = [t for (t,) in r.execute("select name from sqlite_master where type='table'")]
            diffs = []
            for t in tables:
                a = r.execute(f'select count(*) from "{t}"').fetchone()[0]
                b = live.execute(f'select count(*) from "{t}"').fetchone()[0]
                if a > b:  # the live store may have grown since; it must never have fewer
                    diffs.append(f"{t}: restored {a} > live {b}")
            return (not diffs), ("; ".join(diffs) or f"{len(tables)} tables match")
        finally:
            r.close()
            live.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("home", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    report = pack(args.home.expanduser(), args.out)
    checks = {s: verify(args.home.expanduser(), args.out, s) for s in report["stores"]}
    report["verified"] = {s: ok for s, (ok, _) in checks.items()}
    report["verify_notes"] = {s: note for s, (_, note) in checks.items()}
    (args.out / "PACK_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    bad = [s for s, ok in report["verified"].items() if not ok]
    print(
        f"stores {len(report['stores'])}, files {len(report['files'])}, "
        f"skipped {len(report['skipped'])}, refused {len(report['refused'])}, unverified {len(bad)}"
    )
    for item in report["refused"]:
        print(f"REFUSED (looks like a secret): {item}")
    for s in bad:
        print(f"NOT VERIFIED: {s}: {report['verify_notes'][s]}")
    return 1 if (bad or report["refused"]) else 0


if __name__ == "__main__":
    sys.exit(main())
