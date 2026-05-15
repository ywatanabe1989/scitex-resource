"""``scitex-resource ram-limit`` group — set / get RLIMIT_AS in the current process."""

from __future__ import annotations

import json as _json

import click

from .. import limit_ram as _lr


@click.group("ram-limit")
def ram_limit() -> None:
    """Linux RLIMIT_AS for the current process (does NOT bound child procs)."""


@ram_limit.command("set")
@click.argument("factor", type=float)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
def ram_limit_set(factor: float, as_json: bool) -> None:
    """Cap RAM at FACTOR x current-free RAM (0 < FACTOR <= 1).

    Only affects the current python process — exec()'d children do not
    inherit the limit on linux. See the 04_ram-limit skill.

    \b
    Example:
      $ scitex-resource ram-limit set 0.5
      $ scitex-resource ram-limit set 0.25 --json
    """
    if not (0 < factor <= 1):
        raise click.ClickException("FACTOR must satisfy 0 < FACTOR <= 1.")
    _lr.limit_ram(factor)
    if as_json:
        click.echo(_json.dumps({"factor": factor, "ok": True}))


@ram_limit.command("get")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
def ram_limit_get(as_json: bool) -> None:
    """Print MemFree+Buffers+Cached from /proc/meminfo (in KiB).

    \b
    Example:
      $ scitex-resource ram-limit get
      $ scitex-resource ram-limit get --json
    """
    free_kib = _lr.get_ram()
    if as_json:
        click.echo(_json.dumps({"free_kib": free_kib}))
        return
    click.echo(f"free_kib: {free_kib}")
