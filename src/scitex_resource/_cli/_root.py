"""Root click group + ``main()`` entry point for scitex-resource.

Click-based CLI satisfying the SciTeX universal-flag contract:

* top-level: ``-V/--version``, ``-h/--help``, ``--help-recursive``, ``--json``
* ``mcp list-tools`` and ``list-python-apis`` introspection commands
* ``skills {list,get,install}`` for bundled markdown leaves
* ``install-shell-completion`` / ``print-shell-completion``
"""

from __future__ import annotations

import sys
from typing import Sequence

import click

from .. import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

PROG_NAME = "scitex-resource"
PKG = "scitex-resource"


COMMAND_CATEGORIES = [
    ("Hosts", ["hosts"]),
    ("Specs & Metrics", ["specs", "metrics", "processor-usages"]),
    ("RAM Limit", ["ram-limit"]),
    ("Introspection", ["list-python-apis", "list-commands", "mcp", "skills"]),
    ("Shell", ["install-shell-completion", "print-shell-completion"]),
]


class CategorizedGroup(click.Group):
    """Click.Group that groups commands into named sections in --help."""

    def format_commands(self, ctx, formatter):
        commands = {}
        for name in self.list_commands(ctx):
            cmd = self.get_command(ctx, name)
            if cmd is not None and not cmd.hidden:
                commands[name] = cmd
        if not commands:
            return
        displayed = set()
        for category_name, category_commands in COMMAND_CATEGORIES:
            items = []
            for name in category_commands:
                if name in commands and name not in displayed:
                    cmd = commands[name]
                    items.append((name, cmd.get_short_help_str(limit=formatter.width)))
                    displayed.add(name)
            if items:
                with formatter.section(category_name):
                    formatter.write_dl(items)
        leftover = [
            (n, commands[n].get_short_help_str(limit=formatter.width))
            for n in sorted(commands.keys())
            if n not in displayed
        ]
        if leftover:
            with formatter.section("Other"):
                formatter.write_dl(leftover)


def _show_recursive_help(ctx: click.Context) -> None:
    click.echo(ctx.get_help())
    click.echo()
    group = ctx.command
    if isinstance(group, click.Group):
        for name in sorted(group.list_commands(ctx)):
            cmd = group.get_command(ctx, name)
            sub_ctx = click.Context(cmd, parent=ctx, info_name=name)
            click.echo("=" * 60)
            click.echo(f"Command: {name}")
            click.echo("=" * 60)
            click.echo(sub_ctx.get_help())
            click.echo()
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx)):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    sub_sub_ctx = click.Context(
                        sub_cmd, parent=sub_ctx, info_name=sub_name
                    )
                    click.echo("  " + "-" * 56)
                    click.echo(f"  Subcommand: {name} {sub_name}")
                    click.echo("  " + "-" * 56)
                    click.echo(sub_sub_ctx.get_help())
                    click.echo()


@click.group(
    cls=CategorizedGroup,
    invoke_without_command=True,
    context_settings=CONTEXT_SETTINGS,
)
@click.version_option(__version__, "-V", "--version", prog_name=PROG_NAME)
@click.help_option("-h", "--help")
@click.option(
    "--help-recursive",
    is_flag=True,
    help="Show help for all commands recursively.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit structured JSON output (propagates to subcommands that honour it).",
)
@click.pass_context
def cli(ctx: click.Context, help_recursive: bool, as_json: bool) -> None:
    """scitex-resource - System resource info, processor-usage logging, RAM limit.

    \b
    Host identity, specs and live metrics are read via psutil + nvidia-smi.
    Per-host config can override the canonical host name; see:
      ~/.scitex/resource/config.yaml  (host.canonical_name, aliases, role)
    or set $SCITEX_RESOURCE_HOST to short-circuit.
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Wire subcommands. Imports are at the bottom to avoid circular imports.
from ._apis import list_python_apis as _list_python_apis  # noqa: E402
from ._completion import attach_shell_completion  # noqa: E402
from ._hosts_cmd import hosts as _hosts_grp  # noqa: E402
from ._hosts_cmd import machine as _machine_grp  # noqa: E402
from ._introspection import list_commands as _list_commands  # noqa: E402
from ._mcp_commands import mcp_group as _mcp_group  # noqa: E402
from ._metrics_cmd import metrics as _metrics_grp  # noqa: E402
from ._processor_usages_cmd import processor_usages as _proc_grp  # noqa: E402
from ._ram_limit_cmd import ram_limit as _ram_grp  # noqa: E402
from ._skills_cmd import skills_group as _skills_group  # noqa: E402
from ._specs_cmd import specs as _specs_grp  # noqa: E402

cli.add_command(_hosts_grp)
cli.add_command(_machine_grp)
cli.add_command(_specs_grp)
cli.add_command(_metrics_grp)
cli.add_command(_proc_grp)
cli.add_command(_ram_grp)
cli.add_command(_list_python_apis)
cli.add_command(_list_commands)
cli.add_command(_mcp_group)
cli.add_command(_skills_group)
attach_shell_completion(cli, prog_name=PROG_NAME)


def main(argv: Sequence[str] | None = None) -> int:
    """Argv-style entry point.

    Delegates to the Click ``cli`` group with ``standalone_mode=False``
    so Click's ``SystemExit`` is surfaced as a return code instead of
    terminating the interpreter.
    """
    try:
        result = cli.main(
            args=list(argv) if argv is not None else None,
            prog_name=PROG_NAME,
            standalone_mode=False,
        )
    except SystemExit as e:
        code = e.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    except click.exceptions.Exit as e:
        return int(e.exit_code)
    except click.ClickException as e:
        e.show()
        return e.exit_code
    if isinstance(result, int):
        return result
    return 0


# audit §4 — inject version into root --help
try:
    from importlib.metadata import version as _v

    cli.help = (
        f"scitex-resource (v{_v('scitex-resource')}) — " + (cli.help or "").lstrip()
    )
except Exception:
    pass


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
