"""``scitex-resource metrics`` group — live machine metrics.

Default output is the human-readable aligned-column shape suitable for
eyeballs at the terminal; ``--json`` emits strict JSON for ``jq`` and
scripts; ``--yaml`` keeps the legacy shape pipeable into ``yq``.
"""

from __future__ import annotations

import json as _json

import click

from .._specs import get_metrics
from ._human_format import format_human


@click.group("metrics")
def metrics() -> None:
    """Live machine metrics (default human-readable; --json for programmatic use, --yaml for yq pipelines)."""


@metrics.command("show")
@click.option("--no-gpu", is_flag=True, help="Skip the nvidia-smi shellout.")
@click.option("--json", "as_json", is_flag=True, help="Emit strict JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
@click.pass_context
def metrics_show(
    ctx: click.Context, no_gpu: bool, as_json: bool, as_yaml: bool
) -> None:
    """Print current heartbeat-shape metrics.

    \b
    Example:
      $ scitex-resource metrics show
      $ scitex-resource metrics show --no-gpu --json
      $ scitex-resource metrics show --yaml
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    data = get_metrics(gpu=not no_gpu)
    if as_json:
        click.echo(_json.dumps(data, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        click.echo(_yaml.safe_dump(data, sort_keys=False).rstrip())
        return
    click.echo(format_human(data))
