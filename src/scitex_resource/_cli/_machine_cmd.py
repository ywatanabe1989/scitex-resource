"""``scitex-resource machine`` group — show / config."""

from __future__ import annotations

import json as _json

import click

from .._machine import get_machine_config, get_machine_name


@click.group("machine")
def machine() -> None:
    """Machine identity + per-host config."""


@machine.command("show")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
def machine_show(as_json: bool) -> None:
    """Print the canonical machine name (env > config > hostname).

    \b
    Example:
      $ scitex-resource machine show
      $ scitex-resource machine show --json
    """
    name = get_machine_name()
    if as_json:
        click.echo(_json.dumps({"machine": name}, indent=2))
        return
    click.echo(name)


@machine.command("show-config")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
def machine_show_config(as_json: bool, as_yaml: bool) -> None:
    """Print the ``machine:`` block from per-host config.yaml.

    \b
    Example:
      $ scitex-resource machine show-config
      $ scitex-resource machine show-config --json
      $ scitex-resource machine show-config --yaml
    """
    cfg = get_machine_config()
    if as_json:
        click.echo(_json.dumps(cfg, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        click.echo(_yaml.safe_dump(cfg, sort_keys=False).rstrip())
        return
    if not cfg:
        click.echo("(no machine config — using hostname fallback)")
        return
    for k, v in cfg.items():
        click.echo(f"  {k}: {v}")
