#!/usr/bin/env python3
"""Refuse a push that adds a hook registration with no reason filed before it.

The logic lives in divineos.core.hook_lock; this is only the caller the push gate runs.
Exit 0: nothing unexplained was added. Exit 1: a hook was added with no reason (the
message says which and where to file one). Exit 2: the base could not be read, which is
loud on purpose and never read as "no hooks".

--base REF is the seam: it names the base directly so the exits can be driven on a
throwaway repo. Without it the base is the merge-base of HEAD and origin/main.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from divineos.core.hook_lock import UnreadableBase, check_against_base


def _merge_base(repo: Path) -> str:
    merged = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "HEAD", "origin/main"],
        capture_output=True,
        text=True,
        check=False,
    )
    if merged.returncode:
        raise UnreadableBase(
            "cannot find the merge-base of HEAD and origin/main (a shallow clone, or no "
            "origin/main fetched); the lock will not read that as 'no hooks'"
        )
    return merged.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="base ref; default is the merge-base with origin/main")
    args = parser.parse_args()
    repo = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    try:
        verdict = check_against_base(repo, args.base or _merge_base(repo))
    except UnreadableBase as exc:
        print(f"[new-hooks] COULD NOT CHECK: {exc}", file=sys.stderr)
        return 2
    if verdict.refused:
        print(f"[new-hooks] REFUSED\n{verdict.message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
