"""``scitex-resource hosts`` group — identity + per-host config CRUD.

A hidden deprecated ``machine`` alias group is also exported; both groups
share the same Click commands so behaviour is identical.
"""

from __future__ import annotations

import json as _json
import warnings

import click

from .._host import get_host_name
from ._hosts_config import config_group, show_config_alias


@click.group("hosts")
def hosts() -> None:
    """Host identity + per-host config (canonical name, aliases, role)."""


@hosts.command("show")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
@click.pass_context
def hosts_show(ctx: click.Context, as_json: bool) -> None:
    """Print the canonical host name (env > config > hostname).

    \b
    Example:
      $ scitex-resource hosts show
      $ scitex-resource hosts show --json
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    name = get_host_name()
    if as_json:
        click.echo(_json.dumps({"host": name}, indent=2))
        return
    click.echo(name)


# Wire the CRUD subgroup and the back-compat show-config alias.
hosts.add_command(config_group)
hosts.add_command(show_config_alias)


# ---------------------------------------------------------------------------
# Hidden deprecated alias: ``scitex-resource machine ...`` → ``hosts ...``
#
# Click doesn't let one Group instance be wired under two parents while
# preserving its own name in --help, so we declare a thin shim group with
# the same subcommands. The shim emits a single DeprecationWarning the
# first time it's hit per process; the leaf commands are the same Click
# objects (`hosts_show`, `config_group`, `show_config_alias`) so there's
# zero behavioural drift.

_MACHINE_DEPRECATION_EMITTED = False


def _warn_machine_deprecation() -> None:
    global _MACHINE_DEPRECATION_EMITTED
    if _MACHINE_DEPRECATION_EMITTED:
        return
    _MACHINE_DEPRECATION_EMITTED = True
    warnings.warn(
        "`scitex-resource machine ...` is deprecated; "
        "use `scitex-resource hosts ...` instead.",
        DeprecationWarning,
        stacklevel=2,
    )


@click.group("machine", hidden=True)
def machine() -> None:
    """Deprecated alias for `hosts` — emits DeprecationWarning."""
    _warn_machine_deprecation()


# Reuse the same leaf commands so behaviour is bit-for-bit identical.
machine.add_command(hosts_show, name="show")
machine.add_command(config_group)
machine.add_command(show_config_alias)
