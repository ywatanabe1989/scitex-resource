"""``scitex-resource specs`` group — full system specs.

Default human-readable; ``--json`` for programmatic consumers, ``--yaml``
for ``yq`` pipelines.
"""

from __future__ import annotations

import json as _json

import click

from .._specs import get_specs
from ._human_format import format_human


@click.group("specs")
def specs() -> None:
    """Rich system specs (default human-readable; --json for programmatic use, --yaml for yq pipelines)."""


@specs.command("show")
@click.option("--no-system", is_flag=True, help="Skip system/OS info.")
@click.option("--no-cpu", is_flag=True, help="Skip CPU + memory info.")
@click.option("--no-gpu", is_flag=True, help="Skip NVIDIA GPU info.")
@click.option("--no-disk", is_flag=True, help="Skip disk partitions / I/O.")
@click.option("--no-network", is_flag=True, help="Skip network interfaces.")
@click.option("--json", "as_json", is_flag=True, help="Emit strict JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
@click.pass_context
def specs_show(
    ctx: click.Context,
    no_system: bool,
    no_cpu: bool,
    no_gpu: bool,
    no_disk: bool,
    no_network: bool,
    as_json: bool,
    as_yaml: bool,
) -> None:
    """Collect and print rich system specs.

    \b
    Example:
      $ scitex-resource specs show
      $ scitex-resource specs show --no-gpu --no-network --json
      $ scitex-resource specs show --yaml
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    info = get_specs(
        system=not no_system,
        cpu=not no_cpu,
        gpu=not no_gpu,
        disk=not no_disk,
        network=not no_network,
        verbose=False,
        yaml=False,
    )
    if as_json:
        click.echo(_json.dumps(info, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        click.echo(
            _yaml.safe_dump(info, sort_keys=False, default_flow_style=False).rstrip()
        )
        return
    click.echo(format_human(info))
