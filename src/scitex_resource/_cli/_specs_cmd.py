"""``scitex-resource specs`` group — show full system specs."""

from __future__ import annotations

import json as _json

import click

from .._specs import get_specs


@click.group("specs")
def specs() -> None:
    """Rich human-formatted system specs (system/cpu/gpu/disk/network)."""


@specs.command("show")
@click.option("--no-system", is_flag=True, help="Skip system/OS info.")
@click.option("--no-cpu", is_flag=True, help="Skip CPU + memory info.")
@click.option("--no-gpu", is_flag=True, help="Skip NVIDIA GPU info.")
@click.option("--no-disk", is_flag=True, help="Skip disk partitions / I/O.")
@click.option("--no-network", is_flag=True, help="Skip network interfaces.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
def specs_show(
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
    # Human-readable: pprint-like, but indent dicts ourselves
    _print_nested(info, indent=0)


def _print_nested(obj, indent: int) -> None:
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{k}:")
                _print_nested(v, indent + 1)
            else:
                click.echo(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                _print_nested(v, indent)
            else:
                click.echo(f"{pad}- {v}")
    else:
        click.echo(f"{pad}{obj}")
