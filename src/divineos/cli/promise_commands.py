"""divineos promise: see the open promises and close one with a single line.

A thin door over `core/promise_markers`: it turns arguments into module calls and prints what comes back. Every
rule (what a close needs, what age means) lives in the module; this file imports neither json nor time on
purpose, and a test fails if it ever does (walk-60198f385a28).

Shaped by that walk: there is no bulk path (no close-all, no wildcard); the turn for a re-date comes from the
recorder's own count, never from an option I could type (Bengio); and every refusal prints the corrected
command, so a refused close costs one more line (Norman).
"""

from __future__ import annotations

from pathlib import Path

import click

from divineos.core import promise_markers as pm

_TRY = 'Try: divineos promise close <marker> --done <file> | --waiting-on <who> | --false-alarm "<what was misread>"'

_FOLDER_HELP = "The marker folder (default: this seat's own)."


def _refuse(message: str) -> None:
    click.echo(f"{message}\n{_TRY}")
    raise SystemExit(1)


def register(cli: click.Group) -> None:
    @cli.group("promise")
    def promise_group() -> None:
        """Promises I recorded, and the one line that closes each.

        A TURN is one start the harness stamped: a message from Dad, a letter wake or a timer wake. A promise
        falls due after five of them. A close shows a file is newer than the promise, or gives a reason; it
        cannot prove either true, so every close is logged for a reader other than me.
        """

    @promise_group.command("list")
    @click.option("--folder", type=click.Path(path_type=Path), default=None, help=_FOLDER_HELP)
    def list_cmd(folder: Path | None) -> None:
        """Show what is open, how many turns old it is, and what could not be read."""
        folder = folder or pm.default_folder()
        state = pm.read_folder(folder)
        if state.folder_missing:
            click.echo(f"COULD NOT LOOK: there is no marker folder at {folder}")
            return
        for name in state.unreadable:
            click.echo(
                f"COULD NOT READ {name}: it is not valid marker JSON, and it is not counted as clean"
            )
        now = pm.turn_now(folder)
        if not state.open:
            if not state.unreadable:
                click.echo("Nothing open.")
        else:
            click.echo(f"{len(state.open)} open:")
            if now is None:
                click.echo(
                    "  (the recorder has not written the turn count yet, so ages are unknown)"
                )
            due = {m.name for m in pm.due(state.open, now)} if now is not None else set()
            for m in state.open:
                if m.turn is None or now is None:
                    age = "no turn recorded"
                else:
                    age = f"{now - m.turn} turns old"
                flag = "  DUE" if m.name in due else ""
                click.echo(
                    f"  {m.name.removesuffix('.json')}  ({age}){flag}  {m.data.get('promise_text', '')[:90]}"
                )
        counts = pm.close_counts(folder)
        if counts:
            click.echo("closes so far: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))

    @promise_group.command("close")
    @click.argument("marker")
    @click.option(
        "--done", default=None, help="A file written after the promise, that is the deed."
    )
    @click.option(
        "--waiting-on",
        "waiting_on",
        default=None,
        help="Who it waits on; it stays open and re-dates.",
    )
    @click.option(
        "--false-alarm",
        "false_alarm",
        default=None,
        help="What was misread, in a sentence or more.",
    )
    @click.option("--folder", type=click.Path(path_type=Path), default=None, help=_FOLDER_HELP)
    def close_cmd(
        marker: str,
        done: str | None,
        waiting_on: str | None,
        false_alarm: str | None,
        folder: Path | None,
    ) -> None:
        """Close one promise (or re-date one that waits) with one line. One marker, one line, each time."""
        folder = folder or pm.default_folder()
        given = [
            (k, v)
            for k, v in (("done", done), ("waiting-on", waiting_on), ("false-alarm", false_alarm))
            if v
        ]
        if len(given) != 1:
            _refuse(f"Give exactly one of --done, --waiting-on, --false-alarm for {marker}.")
        kind, detail = given[0]
        current_turn = None
        if kind == "waiting-on":
            now = pm.turn_now(folder)
            if now is None:
                _refuse(
                    "turn_now is missing or unreadable, so a re-date cannot be stamped: the recorder writes "
                    "turn_now.json at the end of every reply."
                )
            # turn_now was counted at the end of the LAST turn and this runs in the middle of the next one.
            current_turn = (now or 0) + 1
        try:
            closed = pm.close(folder, marker, kind, detail, current_turn=current_turn)
        except pm.CloseRefused as exc:
            _refuse(str(exc))
            return
        if kind == "waiting-on":
            click.echo(
                f"{closed.name}: still open, waiting on {detail}; due again after {pm.DUE_AFTER_TURNS} turns."
            )
        else:
            click.echo(f"{closed.name}: closed ({kind}).")
