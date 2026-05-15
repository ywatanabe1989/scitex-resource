"""``scitex-resource processor-usages`` group — show / log.

Default human-readable (pandas ``to_string``); ``--json`` for scripts,
``--yaml`` for ``yq`` pipelines, ``--csv`` for spreadsheet ingest.
"""

from __future__ import annotations

import json as _json

import click

from .._log_processor_usages import log_processor_usages
from .._specs import get_processor_usages


@click.group("processor-usages")
def processor_usages() -> None:
    """Processor usage snapshots / time-series (default human-readable; --json for programmatic use, --yaml for yq pipelines)."""


@processor_usages.command("show")
@click.option("--json", "as_json", is_flag=True, help="Emit strict JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
@click.option("--csv", "as_csv", is_flag=True, help="Emit CSV output.")
@click.pass_context
def processor_usages_show(
    ctx: click.Context, as_json: bool, as_yaml: bool, as_csv: bool
) -> None:
    """Take one snapshot and print it.

    \b
    Example:
      $ scitex-resource processor-usages show
      $ scitex-resource processor-usages show --json
      $ scitex-resource processor-usages show --csv
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    df = get_processor_usages()
    if as_json:
        records = df.to_dict(orient="records")
        click.echo(_json.dumps(records, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        records = df.to_dict(orient="records")
        click.echo(
            _yaml.safe_dump(records, sort_keys=False, default_flow_style=False).rstrip()
        )
        return
    if as_csv:
        click.echo(df.to_csv(index=False).rstrip())
        return
    # Default human shape: aligned columns + thousand-separators for large ints.
    formatters = {}
    for col in df.columns:
        if df[col].dtype.kind in ("i", "u"):
            formatters[col] = lambda v: f"{v:,}" if abs(v) >= 1000 else str(v)
    click.echo(df.to_string(index=False, formatters=formatters or None))


@processor_usages.command("log")
@click.option(
    "--interval",
    "interval_s",
    type=float,
    default=1.0,
    help="Sampling interval in seconds. Default: 1.",
)
@click.option(
    "--path",
    "path",
    type=click.Path(),
    default="/tmp/scitex/processor_usages.csv",
    help="CSV path to append rows to.",
)
@click.option(
    "--max-rows",
    "max_rows",
    type=int,
    default=60,
    help="Stop after this many rows. Default: 60.",
)
@click.option(
    "--no-init",
    is_flag=True,
    help="Keep existing CSV file rather than re-initializing.",
)
def processor_usages_log(
    interval_s: float,
    path: str,
    max_rows: int,
    no_init: bool,
) -> None:
    """Append CPU/RAM/GPU/VRAM rows to a CSV over time.

    Stops after ``--max-rows`` samples (or Ctrl-C).

    \b
    Example:
      $ scitex-resource processor-usages log --interval 5 --max-rows 12
      $ scitex-resource processor-usages log --path ./usage.csv --max-rows 100
    """
    limit_min = (max_rows * interval_s) / 60.0
    if limit_min <= 0:
        raise click.ClickException("--max-rows * --interval must be > 0")
    log_processor_usages(
        path=path,
        limit_min=limit_min,
        interval_s=interval_s,
        init=not no_init,
        verbose=False,
        background=False,
    )
    click.echo(f"wrote {max_rows} rows to {path}")
