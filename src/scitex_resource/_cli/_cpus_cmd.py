"""``scitex-resource cpus`` group — how many CPUs this process may use.

Distinct from ``metrics``/``specs``, which report how big the MACHINE is.
This group answers the sizing question ("how many workers should I start?")
and is the surface shell scripts call::

    WORKERS="$(scitex-resource cpus show --count)"

``--count`` prints a bare integer and nothing else, so it is safe to
interpolate directly. The default human output shows every source rather
than only the winner — when they disagree, the disagreement is the finding.
"""

from __future__ import annotations

import json as _json

import click

from .._cpus import get_cpu_sources
from ._human_format import format_human


@click.group("cpus")
def cpus() -> None:
    """Usable CPU count for sizing worker pools (affinity → SLURM → machine)."""


@cpus.command("show")
@click.option(
    "--count",
    "count_only",
    is_flag=True,
    help="Print ONLY the usable count as a bare integer (for shell capture).",
)
@click.option(
    "--minimum",
    type=int,
    default=1,
    show_default=True,
    help="Floor for the reported count.",
)
@click.option("--json", "as_json", is_flag=True, help="Emit strict JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
@click.pass_context
def cpus_show(
    ctx: click.Context,
    count_only: bool,
    minimum: int,
    as_json: bool,
    as_yaml: bool,
) -> None:
    """Print the usable CPU count and what each source reported.

    \b
    Example:
      $ scitex-resource cpus show
      $ scitex-resource cpus show --count          # bare integer
      $ scitex-resource cpus show --minimum 4 --json

    \b
    On a host inside a 48-CPU SLURM allocation on a 128-CPU node:
      usable                48
      source                affinity
      affinity              48
      cpu_count            128
      slurm_cpus_per_task   48
    """
    data = get_cpu_sources()
    floor = max(1, int(minimum))
    if data["usable"] < floor:
        data["usable"] = floor
        data["source"] = "minimum"

    if count_only:
        click.echo(data["usable"])
        return

    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    if as_json:
        click.echo(_json.dumps(data, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        click.echo(_yaml.safe_dump(data, sort_keys=False).rstrip())
        return
    click.echo(format_human(data))
