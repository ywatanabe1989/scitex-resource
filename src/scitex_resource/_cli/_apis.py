"""``list-python-apis`` introspection command (§1a)."""

from __future__ import annotations

import json as _json

import click

_APIS = [
    ("get_machine_name", "Canonical machine name (env > config > hostname)."),
    ("get_machine_config", "The ``machine:`` block from per-host config.yaml."),
    ("load_config", "Merged config dict (project overrides user)."),
    (
        "get_specs",
        "Rich human-formatted system spec dict (system/cpu/gpu/disk/network).",
    ),
    ("get_metrics", "Flat machine-readable metrics dict for heartbeats."),
    ("get_processor_usages", "Single-row DataFrame: CPU/RAM/GPU/VRAM at call time."),
    ("log_processor_usages", "Append processor usage rows to CSV over time."),
]


@click.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity (-v, -vv).")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def list_python_apis(verbose, as_json):
    """List public Python API symbols of scitex_resource.

    \b
    Example:
      $ scitex-resource list-python-apis
      $ scitex-resource list-python-apis --json
    """
    if as_json:
        click.echo(
            _json.dumps(
                {
                    "module": "scitex_resource",
                    "apis": [{"name": n, "description": d} for n, d in _APIS],
                },
                indent=2,
            )
        )
        return
    click.echo("scitex_resource Python API:")
    click.echo()
    for name, desc in _APIS:
        if verbose >= 1:
            click.echo(f"  {name:24s} {desc}")
        else:
            click.echo(f"  {name}")
