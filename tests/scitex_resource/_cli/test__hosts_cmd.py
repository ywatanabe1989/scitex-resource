"""CLI tests for ``scitex-resource hosts ...`` (and deprecated ``machine`` alias).

Uses real env-var mutation (yield-based teardown) to pin a known
canonical name; uses ``tmp_path`` for filesystem isolation so the
user's ``~/.scitex/resource/config.yaml`` is never touched.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml as _yaml
from click.testing import CliRunner

from scitex_resource._cli import cli

# ---------------------------------------------------------------------------
# Fixtures


@pytest.fixture
def pinned_host():
    """Pin ``$SCITEX_RESOURCE_HOST`` to a known value for one test."""
    # Arrange
    key = "SCITEX_RESOURCE_HOST"
    prior = os.environ.get(key)
    os.environ[key] = "test-host-42"
    try:
        yield "test-host-42"
    finally:
        if prior is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = prior


@pytest.fixture
def isolated_scitex_dir(tmp_path: Path):
    """Point $SCITEX_DIR + $HOME at tmp_path and cd into a child dir.

    Guarantees writes from ``hosts config ...`` never touch the user's
    real config files.
    """
    # Arrange
    scitex_key, home_key = "SCITEX_DIR", "HOME"
    host_key = "SCITEX_RESOURCE_HOST"
    legacy_key = "SCITEX_RESOURCE_MACHINE"
    prior_scitex = os.environ.get(scitex_key)
    prior_home = os.environ.get(home_key)
    prior_host = os.environ.get(host_key)
    prior_legacy = os.environ.get(legacy_key)
    prior_cwd = Path.cwd()
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    workdir = fake_home / "work"
    workdir.mkdir()
    os.environ[scitex_key] = str(fake_home / ".scitex")
    os.environ[home_key] = str(fake_home)
    # Drop env pins so we test config-file resolution, not env shortcut.
    os.environ.pop(host_key, None)
    os.environ.pop(legacy_key, None)
    os.chdir(workdir)
    try:
        yield {
            "home": fake_home,
            "work": workdir,
            "user_cfg": fake_home / ".scitex" / "resource" / "config.yaml",
            "project_cfg": workdir / ".scitex" / "resource" / "config.yaml",
        }
    finally:
        os.chdir(prior_cwd)
        for k, v in (
            (scitex_key, prior_scitex),
            (home_key, prior_home),
            (host_key, prior_host),
            (legacy_key, prior_legacy),
        ):
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ---------------------------------------------------------------------------
# `hosts show`


def test_hosts_show_exits_zero(pinned_host):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "show"])
    # Assert
    assert result.exit_code == 0


def test_hosts_show_prints_pinned_name(pinned_host):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "show"])
    # Assert
    assert pinned_host in result.output


def test_hosts_show_json_matches_pinned_name(pinned_host):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "show", "--json"])
    # Assert
    assert json.loads(result.output) == {"host": pinned_host}


# ---------------------------------------------------------------------------
# Deprecated ``machine`` alias still works


def test_machine_alias_show_exits_zero(pinned_host):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show"])
    # Assert
    assert result.exit_code == 0


def test_machine_alias_show_prints_pinned_name(pinned_host):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show"])
    # Assert
    assert pinned_host in result.output


# ---------------------------------------------------------------------------
# `hosts config show`


def test_config_show_exits_zero(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show", "--json"])
    # Assert
    assert result.exit_code == 0


def test_config_show_json_is_dict(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), dict)


def test_config_show_default_human_message_when_empty(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show"])
    # Assert
    assert "no host config" in result.output


# ---------------------------------------------------------------------------
# `hosts config show-path`


def test_config_show_path_reports_no_files_when_empty(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show-path"])
    # Assert
    assert "no config files" in result.output


def test_config_show_path_all_emits_empty_list_json_when_empty(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show-path", "--all", "--json"])
    # Assert
    assert json.loads(result.output) == []


# ---------------------------------------------------------------------------
# `hosts config init`


def test_config_init_user_creates_file(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Assert
    assert isolated_scitex_dir["user_cfg"].is_file()


def test_config_init_user_starter_contains_host_block(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Assert
    assert "host:" in isolated_scitex_dir["user_cfg"].read_text()


def test_config_init_does_not_overwrite_existing_file(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    body_before = isolated_scitex_dir["user_cfg"].read_text()
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Assert
    assert isolated_scitex_dir["user_cfg"].read_text() == body_before


def test_config_init_reports_already_exists_message(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Act
    result = runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Assert
    assert "already exists" in result.output


def test_config_init_force_overwrites(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    isolated_scitex_dir["user_cfg"].write_text("# manual edit\n")
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--force", "--yes"])
    # Assert
    assert "host:" in isolated_scitex_dir["user_cfg"].read_text()


def test_config_init_project_creates_project_file(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--project", "--yes"])
    # Assert
    assert isolated_scitex_dir["project_cfg"].is_file()


def test_config_init_dry_run_does_not_write_file(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--dry-run"])
    # Assert
    assert not isolated_scitex_dir["user_cfg"].is_file()


def test_config_init_dry_run_announces_target(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "init", "--user", "--dry-run"])
    # Assert
    assert "dry-run" in result.output


def test_config_init_requires_yes(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "config", "init", "--user"])
    # Assert
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# `hosts config set` / `unset`


def test_config_set_updates_user_file(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(
        cli,
        [
            "hosts",
            "config",
            "set",
            "host.canonical_name",
            "spartan",
            "--user",
            "--yes",
        ],
    )
    # Assert
    data = _yaml.safe_load(isolated_scitex_dir["user_cfg"].read_text())
    assert data["host"]["canonical_name"] == "spartan"


def test_config_set_then_show_reflects_value(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "hosts",
            "config",
            "set",
            "host.canonical_name",
            "spartan",
            "--user",
            "--yes",
        ],
    )
    # Act
    result = runner.invoke(cli, ["hosts", "config", "show", "--json"])
    # Assert
    assert json.loads(result.output)["canonical_name"] == "spartan"


def test_config_set_json_value_parses_list(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(
        cli,
        [
            "hosts",
            "config",
            "set",
            "host.aliases",
            '["a","b"]',
            "--user",
            "--yes",
            "--json-value",
        ],
    )
    # Assert
    data = _yaml.safe_load(isolated_scitex_dir["user_cfg"].read_text())
    assert data["host"]["aliases"] == ["a", "b"]


def test_config_unset_removes_key(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "hosts",
            "config",
            "set",
            "host.canonical_name",
            "spartan",
            "--user",
            "--yes",
        ],
    )
    # Act
    runner.invoke(
        cli,
        ["hosts", "config", "unset", "host.canonical_name", "--user"],
    )
    # Assert
    data = _yaml.safe_load(isolated_scitex_dir["user_cfg"].read_text())
    assert "canonical_name" not in (data.get("host") or {})


def test_config_unset_absent_key_is_noop(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    runner.invoke(cli, ["hosts", "config", "init", "--user", "--yes"])
    # Act
    result = runner.invoke(
        cli,
        ["hosts", "config", "unset", "missing.key", "--user"],
    )
    # Assert
    assert "not present" in result.output


def test_config_set_preserves_comments_via_ruamel(isolated_scitex_dir):
    # Arrange — write a YAML body with a top-of-file comment.
    runner = CliRunner()
    user_cfg = isolated_scitex_dir["user_cfg"]
    user_cfg.parent.mkdir(parents=True, exist_ok=True)
    user_cfg.write_text("# user comment do not lose\nhost:\n  canonical_name: old\n")
    # Act
    runner.invoke(
        cli,
        ["hosts", "config", "set", "host.role", "head", "--user", "--yes"],
    )
    # Assert
    assert "# user comment do not lose" in user_cfg.read_text()


# ---------------------------------------------------------------------------
# Back-compat alias


def test_show_config_alias_still_works(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "show-config", "--json"])
    # Assert
    assert result.exit_code == 0


def test_show_config_alias_is_hidden_in_help(isolated_scitex_dir):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["hosts", "--help"])
    # Assert
    assert "show-config" not in result.output


def test_show_config_alias_emits_deprecation_warning(isolated_scitex_dir, recwarn):
    # Arrange
    runner = CliRunner()
    # Act
    runner.invoke(cli, ["hosts", "show-config", "--json"])
    # Assert
    assert any(issubclass(w.category, DeprecationWarning) for w in recwarn.list)
