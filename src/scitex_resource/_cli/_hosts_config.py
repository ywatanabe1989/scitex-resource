"""``scitex-resource hosts config`` CRUD subgroup.

Uses ruamel.yaml round-trip mode to preserve comments and key order.
Read path stays on PyYAML via :mod:`scitex_resource._host`; this
module only handles writes plus a small set of read leaves layered on
top so the umbrella ``--json`` flag is honoured uniformly.
"""

from __future__ import annotations

import json as _json
import os
import warnings
from io import StringIO
from pathlib import Path
from typing import Any

import click

from .._host import _PKG_SHORT, _config_paths, get_host_config

# ---------------------------------------------------------------------------
# Path resolution


def _user_config_path() -> Path:
    """Return the user-scope ``config.yaml`` path (may not yet exist)."""
    root = Path(os.environ.get("SCITEX_DIR") or (Path.home() / ".scitex"))
    return root / _PKG_SHORT / "config.yaml"


def _project_config_path() -> Path:
    """Return the first project-scope ``config.yaml`` from cwd upward.

    Walks cwd→parent→... stopping at ``$HOME``. If no existing project
    file is found, returns the would-be path at ``cwd/.scitex/<pkg>/``
    so callers can ``init`` it.
    """
    cwd_root = Path.cwd()
    home = Path.home().resolve()
    for parent in (cwd_root, *cwd_root.parents):
        try:
            resolved = parent.resolve()
        except OSError:
            resolved = parent
        if resolved == home:
            break
        candidate = parent / ".scitex" / _PKG_SHORT / "config.yaml"
        if candidate.is_file():
            return candidate
    return cwd_root / ".scitex" / _PKG_SHORT / "config.yaml"


def _resolve_target(scope_user: bool, scope_project: bool) -> Path:
    """Return the write-target file for set/unset/init/edit.

    Precedence: explicit flag → first existing project file → user file.
    """
    if scope_user and scope_project:
        raise click.UsageError("--user and --project are mutually exclusive.")
    if scope_user:
        return _user_config_path()
    if scope_project:
        return _project_config_path()
    # No flag: prefer existing project file, else user.
    for p in _config_paths():
        # _config_paths returns existing files only, project first.
        # If the first hit lives under HOME and equals user path, treat as user.
        if p == _user_config_path():
            return p
        return p
    return _user_config_path()


# ---------------------------------------------------------------------------
# ruamel.yaml round-trip helpers


def _ruamel():
    from ruamel.yaml import YAML

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def _load_rt(path: Path) -> Any:
    yaml = _ruamel()
    if not path.is_file():
        return None
    with path.open() as f:
        return yaml.load(f)


def _dump_rt(data: Any, path: Path) -> None:
    yaml = _ruamel()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        yaml.dump(data, f)


def _dump_rt_str(data: Any) -> str:
    yaml = _ruamel()
    buf = StringIO()
    yaml.dump(data, buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Dot-path traversal


def _parse_value(raw: str, json_value: bool) -> Any:
    if not json_value:
        return raw
    try:
        return _json.loads(raw)
    except _json.JSONDecodeError as e:
        raise click.UsageError(f"--json-value but VALUE is not valid JSON: {e}")


def _set_dot(root: Any, dotted: str, value: Any) -> Any:
    """Set ``dotted`` path inside ``root`` (creating dicts as needed).

    Returns the (possibly new) root. Uses ruamel CommentedMap when
    creating nested mappings so the file stays round-trip clean.
    """
    from ruamel.yaml.comments import CommentedMap

    keys = dotted.split(".")
    if root is None:
        root = CommentedMap()
    cursor = root
    for k in keys[:-1]:
        if (
            not isinstance(cursor, dict)
            or k not in cursor
            or not isinstance(cursor[k], dict)
        ):
            cursor[k] = CommentedMap()
        cursor = cursor[k]
    cursor[keys[-1]] = value
    return root


def _unset_dot(root: Any, dotted: str) -> tuple[Any, bool]:
    """Remove ``dotted`` path; return (root, was_present)."""
    if root is None:
        return root, False
    keys = dotted.split(".")
    cursor = root
    for k in keys[:-1]:
        if not isinstance(cursor, dict) or k not in cursor:
            return root, False
        cursor = cursor[k]
    if not isinstance(cursor, dict) or keys[-1] not in cursor:
        return root, False
    del cursor[keys[-1]]
    return root, True


# ---------------------------------------------------------------------------
# Confirmation helper


def _require_yes_for_new_file(path: Path, yes: bool) -> None:
    """Refuse to create a new file unless ``--yes`` is passed.

    Non-interactive by design: agents/cron must opt in explicitly via
    ``--yes`` rather than answering an interactive prompt.
    """
    if path.is_file() or yes:
        return
    raise click.UsageError(f"{path} does not exist; pass --yes to create it.")


# ---------------------------------------------------------------------------
# CLI group


@click.group("config")
def config_group() -> None:
    """CRUD for the per-host ``config.yaml`` (host identity + role).

    \b
    Files searched (project first, user fallback):
      ./.scitex/resource/config.yaml   (and parents up to $HOME)
      ~/.scitex/resource/config.yaml
    """


@config_group.command("show")
@click.option("--json", "as_json", is_flag=True, help="Emit strict JSON.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML.")
@click.pass_context
def config_show(ctx: click.Context, as_json: bool, as_yaml: bool) -> None:
    """Print the resolved ``host:`` block (project overrides user).

    \b
    Example:
      $ scitex-resource hosts config show
      $ scitex-resource hosts config show --json
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    cfg = get_host_config()
    if as_json:
        click.echo(_json.dumps(cfg, indent=2, default=str))
        return
    if as_yaml:
        import yaml as _yaml

        click.echo(_yaml.safe_dump(cfg, sort_keys=False).rstrip())
        return
    if not cfg:
        click.echo("(no host config — using hostname fallback)")
        return
    from ._human_format import format_human

    click.echo(format_human(cfg))


@config_group.command("show-path")
@click.option(
    "--all", "show_all", is_flag=True, help="List every file in cascade order."
)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
@click.pass_context
def config_show_path(ctx: click.Context, show_all: bool, as_json: bool) -> None:
    """Print which config file is in effect.

    \b
    Example:
      $ scitex-resource hosts config show-path
      $ scitex-resource hosts config show-path --all
    """
    parent_as_json = bool(ctx.obj and ctx.obj.get("as_json"))
    as_json = as_json or parent_as_json
    paths = _config_paths()
    if show_all:
        as_strs = [str(p) for p in paths]
        if as_json:
            click.echo(_json.dumps(as_strs, indent=2))
            return
        if not as_strs:
            click.echo("(no config files found)")
            return
        for p in as_strs:
            click.echo(p)
        return
    if not paths:
        if as_json:
            click.echo("null")
            return
        click.echo("(no config files found)")
        return
    if as_json:
        click.echo(_json.dumps(str(paths[0])))
        return
    click.echo(str(paths[0]))


_STARTER = """\
# scitex-resource per-host config.yaml
# Authoritative answer to "what host is this?" across the scitex-* ecosystem.
host:
  canonical_name: ""
  aliases: []
  role: ""
"""


@config_group.command("init")
@click.option(
    "--user", "scope_user", is_flag=True, help="Target the user-scope file (default)."
)
@click.option(
    "--project", "scope_project", is_flag=True, help="Target the project-scope file."
)
@click.option("--force", is_flag=True, help="Overwrite an existing file.")
@click.option(
    "--dry-run", "dry_run", is_flag=True, help="Print the target path without writing."
)
@click.option(
    "--yes", "-y", "yes", is_flag=True, help="Confirm; required for non-dry-run."
)
def config_init(
    scope_user: bool,
    scope_project: bool,
    force: bool,
    dry_run: bool,
    yes: bool,
) -> None:
    """Scaffold a starter ``config.yaml`` with the ``host:`` block stubbed.

    \b
    Example:
      $ scitex-resource hosts config init --yes          # user scope
      $ scitex-resource hosts config init --project --yes
      $ scitex-resource hosts config init --dry-run
    """
    # Default to --user when nothing specified.
    if not scope_user and not scope_project:
        scope_user = True
    target = _resolve_target(scope_user, scope_project)
    if target.is_file() and not force:
        click.echo(f"{target} already exists; pass --force to overwrite.")
        return
    if dry_run:
        click.echo(f"[dry-run] would write {target}")
        return
    if not yes:
        raise click.UsageError(
            "refusing to write without --yes/-y (use --dry-run to preview)."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_STARTER)
    click.echo(f"wrote {target}")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--user", "scope_user", is_flag=True, help="Target the user-scope file.")
@click.option(
    "--project", "scope_project", is_flag=True, help="Target the project-scope file."
)
@click.option("--json-value", "json_value", is_flag=True, help="Parse VALUE as JSON.")
@click.option("--yes", is_flag=True, help="Don't prompt before creating a new file.")
def config_set(
    key: str,
    value: str,
    scope_user: bool,
    scope_project: bool,
    json_value: bool,
    yes: bool,
) -> None:
    """Set a dot-path key (creates nested dicts as needed).

    \b
    Example:
      $ scitex-resource hosts config set host.canonical_name spartan
      $ scitex-resource hosts config set host.aliases '["a","b"]' --json-value
    """
    target = _resolve_target(scope_user, scope_project)
    _require_yes_for_new_file(target, yes)
    parsed = _parse_value(value, json_value)
    data = _load_rt(target)
    data = _set_dot(data, key, parsed)
    _dump_rt(data, target)
    click.echo(f"set {key} in {target}")


@config_group.command("unset")
@click.argument("key")
@click.option("--user", "scope_user", is_flag=True, help="Target the user-scope file.")
@click.option(
    "--project", "scope_project", is_flag=True, help="Target the project-scope file."
)
def config_unset(key: str, scope_user: bool, scope_project: bool) -> None:
    """Remove a dot-path key. No-op (with notice) if absent.

    \b
    Example:
      $ scitex-resource hosts config unset host.canonical_name
    """
    target = _resolve_target(scope_user, scope_project)
    if not target.is_file():
        click.echo(f"{target} does not exist; nothing to unset.")
        return
    data = _load_rt(target)
    data, removed = _unset_dot(data, key)
    if not removed:
        click.echo(f"{key} not present in {target}")
        return
    _dump_rt(data, target)
    click.echo(f"unset {key} in {target}")


@config_group.command("edit")
@click.option("--user", "scope_user", is_flag=True, help="Target the user-scope file.")
@click.option(
    "--project", "scope_project", is_flag=True, help="Target the project-scope file."
)
@click.option(
    "--dry-run",
    "dry_run",
    is_flag=True,
    help="Print the target path without launching $EDITOR.",
)
@click.option(
    "--yes",
    "-y",
    "yes",
    is_flag=True,
    help="Confirm; required to scaffold the file if missing.",
)
def config_edit(
    scope_user: bool, scope_project: bool, dry_run: bool, yes: bool
) -> None:
    """Open the resolved config file in ``$EDITOR`` (default ``vi``).

    \b
    Example:
      $ scitex-resource hosts config edit
      $ scitex-resource hosts config edit --dry-run
    """
    target = _resolve_target(scope_user, scope_project)
    if dry_run:
        click.echo(f"[dry-run] would open {target} in $EDITOR")
        return
    if not target.is_file() and not yes:
        raise click.UsageError(
            f"{target} does not exist; pass --yes/-y to scaffold it before editing."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file():
        target.write_text(_STARTER)
    editor = os.environ.get("EDITOR") or "vi"
    click.edit(filename=str(target), editor=editor)


# ---------------------------------------------------------------------------
# Back-compat alias: hidden ``show-config`` -> ``config show``


@click.command("show-config", hidden=True)
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
@click.option("--yaml", "as_yaml", is_flag=True, help="Emit YAML output.")
@click.pass_context
def show_config_alias(ctx: click.Context, as_json: bool, as_yaml: bool) -> None:
    """Deprecated alias for ``hosts config show``."""
    warnings.warn(
        "`scitex-resource hosts show-config` is deprecated; "
        "use `scitex-resource hosts config show` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    ctx.invoke(config_show, as_json=as_json, as_yaml=as_yaml)


# Re-export for use in tests / advanced callers.
__all__ = [
    "config_group",
    "show_config_alias",
    "_resolve_target",
    "_user_config_path",
    "_project_config_path",
]
