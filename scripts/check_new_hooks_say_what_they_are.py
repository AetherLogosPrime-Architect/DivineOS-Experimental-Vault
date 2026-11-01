"""A hook added since the base says what it is: scaffolding, or something only I can do.

Dad 2026-11-01: a reminder that something could do for me is scaffolding, needed until the
real structure is built; what only I can do is permanent. A label I could skip is a note I
would forget, so this asks at the moment a hook is added (the pre-commit step), against a
named base, not as something to remember.

It refuses an ADDITION with no label. It does not refuse the hooks that already exist without
one: those are the worklist the measuring tool prints. It does not judge whether a label is
true; code cannot, and a change to a label goes through the same review as any hook edit.

If the base cannot be read it says so and fails, and does not pass: could-not-look must never
render as looked-and-found-nothing. The way through when offline is ``--base HEAD``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from divineos.core import hook_layer  # noqa: E402

_ASK = (
    "{name} is a new hook and says nothing about what it is. Is it scaffolding for something "
    "not built yet, or something only you can do? Say which in its first lines:\n"
    "    HOOK-ROLE: scaffold -- <what will replace it>\n"
    "    HOOK-ROLE: permanent -- <why only you can do it>"
)


def base_registered(root: Path, base_ref: str) -> set[str] | None:
    """The scripts the base ref registers, or None if the base cannot be read."""
    try:
        shown = subprocess.run(
            ["git", "-C", str(root), "show", f"{base_ref}:{hook_layer.SETTINGS_FILE}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        return hook_layer.registered_in(json.loads(shown))
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


def check(root: Path, base_ref: str) -> tuple[int, str]:
    """(0, ok) | (1, the question for each new hook) | (2, could not read the base)."""
    base = base_registered(root, base_ref)
    if base is None:
        return 2, (
            f"NOT CHECKED: could not read {hook_layer.SETTINGS_FILE} at {base_ref}, so no hook "
            "can be called new. This is not a pass. If you are offline, run with --base HEAD."
        )
    missing = hook_layer.new_without_a_role(hook_layer.inventory(root), base)
    if not missing:
        return 0, f"ok: every hook added since {base_ref} says what it is."
    return 1, "\n\n".join(_ASK.format(name=n) for n in missing)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    code, text = check(Path(args.root), args.base)
    print(text, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
