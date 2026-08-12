"""§13 — the canonical ``dev`` group for scitex-resource's self-maintenance.

Operator directive. Doctrine: ``20_dev-commands.md`` (§13, the one-group
rule) plus the classification table in
``18_dev-subgroup-and-ecosystem-placement.md`` (§11), both under
``scitex_dev/_skills/general/03_interface/02_cli/``.

    A package's top-level CLI is its DOMAIN. Self-maintenance plumbing is
    housekeeping, and housekeeping belongs under `dev`.
    `<pkg> --help` then reads as the tool, not the tool's own upkeep.

THE DISCRIMINATOR, applied here: "is this command about the tool's DOMAIN
— this machine's identity, specs, live metrics, processor usage, RAM cap —
or about the PACKAGE itself?"

  moved to `dev`   skills, list-python-apis, list-commands
  kept top level   hosts, specs, metrics, processor-usages, ram-limit
                       the domain verbs — the package's reason to exist
                   mcp, install-shell-completion, print-shell-completion

The last row is not an oversight. §11 names both the ``mcp`` group and the
completion surface in its explicit NOT-in-`dev` column ("user-facing, stays
top-level"), §4a files ``mcp`` under `Service` and completion under `Shell`,
§1a requires ``<cli> mcp list-tools`` to resolve, and scitex-dev's own §13
migration (``_cli/_dev_group.py``) likewise records ``mcp`` under "kept top
level". §13's canonical ``shell`` verb is a dev/repl shell, not tab
completion — §1b's canonical home for completion is a top-level
``completion`` noun group, still to be adopted here.

MIGRATION, NOT RENAME. Every spelling moved below keeps working from its
old top-level position as a Phase W warn-forward alias (§5
``11_deprecation.md``): hidden from ``--help``, forwarding argv verbatim,
warning once per shell session. The old spellings live in scripts, cron
lines, agent prompts and documentation that are not greppable from this
repository, so dropping one would break callers this repo cannot see.
"""

from __future__ import annotations

import click
from scitex_dev.ecosystem import deprecated_alias

#: Version the Phase W aliases disappear in. Deliberately distant — see the
#: module docstring on why the old spellings cannot be enumerated from here.
_ALIAS_REMOVE_IN = "0.8.0"

#: Commands moving from top level into ``dev``. Data rather than code so the
#: alias loop cannot drift from the mount loop — the drift that would leave a
#: command mounted under ``dev`` with no alias, its old spelling resolving
#: nowhere.
_MOVED = ("skills", "list-python-apis", "list-commands")

__all__ = ["install_dev_aliases", "register_dev_group"]


def register_dev_group(main: click.Group) -> click.Group:
    """Mount ``dev`` on *main* and populate it with self-maintenance surfaces.

    Declared here and nowhere else. Two builders would each register a
    ``dev`` on ``main`` and the later call would silently replace the
    earlier group — click's ``add_command`` is a dict assignment, so
    whichever surfaces the loser had mounted would vanish with no error.

    Returns the group so the caller can hand it to :func:`install_dev_aliases`
    once every mount is in place.
    """
    from ._apis import list_python_apis
    from ._introspection import list_commands
    from ._skills_cmd import skills_group

    @main.group("dev", invoke_without_command=True)
    @click.pass_context
    def dev(ctx: click.Context) -> None:
        """Package self-maintenance — introspection and bundled skills.

        \b
        Examples:
          $ scitex-resource dev skills list
          $ scitex-resource dev list-python-apis --json
          $ scitex-resource dev list-commands
        """
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())

    dev.add_command(skills_group, name="skills")
    dev.add_command(list_python_apis, name="list-python-apis")
    dev.add_command(list_commands, name="list-commands")
    return dev


def install_dev_aliases(main: click.Group, dev: click.Group) -> None:
    """Phase W warn-forward aliases for every command that moved.

    Call AFTER ``dev`` is fully populated: an alias must point at a command
    that exists, and one built earlier would forward to nothing — the exact
    failure this migration is meant to be invisible against.
    """
    for name in _MOVED:
        command = dev.commands.get(name)
        if command is None:
            # Fail loud rather than skip. A missing command here means a
            # mount did not happen, and a silently-absent alias is
            # indistinguishable from a successful migration.
            raise RuntimeError(
                f"§13 dev-group migration: {name!r} is not mounted on `dev`, "
                "so its Phase W alias cannot be built. Fix the mount rather "
                f"than dropping the alias, or the old `scitex-resource "
                f"{name}` spelling resolves nowhere."
            )
        deprecated_alias(
            main,
            name,
            target=command,
            target_name=f"dev {name}",
            remove_in=_ALIAS_REMOVE_IN,
            phase="warn",
        )
