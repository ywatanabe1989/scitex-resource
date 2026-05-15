"""``scitex-resource metrics`` group — flat machine-readable metrics."""

from __future__ import annotations

import json as _json

import click

from .._specs import get_metrics


@click.group("metrics")
def metrics() -> None:
    """Flat machine-readable metrics suitable for heartbeats."""


@metrics.command("show")
@click.option("--no-gpu", is_flag=True, help="Skip the nvidia-smi shellout.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
def metrics_show(no_gpu: bool, as_json: bool) -> None:
    """Print current heartbeat-shape metrics.

    \b
    Example:
      $ scitex-resource metrics show
      $ scitex-resource metrics show --no-gpu --json
    """
    data = get_metrics(gpu=not no_gpu)
    if as_json:
        click.echo(_json.dumps(data, indent=2, default=str))
        return
    for k, v in data.items():
        if k == "gpus":
            if not v:
                click.echo("  gpus: []")
            else:
                click.echo("  gpus:")
                for gpu in v:
                    click.echo(
                        f"    - {gpu.get('name', '?')}  "
                        f"{gpu.get('vram_used_mb', 0)}/{gpu.get('vram_total_mb', 0)} MiB"
                    )
        else:
            click.echo(f"  {k}: {v}")
