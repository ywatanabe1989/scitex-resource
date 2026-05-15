"""``list-commands`` introspection — flat listing of every leaf command."""

from __future__ import annotations

import json as _json

import click


def _walk(group: click.Group, prefix: str = ""):
    for name in sorted(group.list_commands(None) or []):
        cmd = group.get_command(None, name)
        if cmd is None or cmd.hidden:
            continue
        full = f"{prefix}{name}" if not prefix else f"{prefix} {name}"
        if isinstance(cmd, click.Group):
            yield from _walk(cmd, full)
        else:
            yield full, (cmd.get_short_help_str() or "")


@click.command("list-commands")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def list_commands(ctx, as_json):
    """List every leaf CLI command (recursive).

    \b
    Example:
      $ scitex-resource list-commands
      $ scitex-resource list-commands --json
    """
    root = ctx.find_root().command
    items = list(_walk(root))
    if as_json:
        click.echo(
            _json.dumps(
                [{"command": c, "help": h} for c, h in items],
                indent=2,
            )
        )
        return
    for cmd, help_text in items:
        click.echo(f"  {cmd:40s} {help_text}")
