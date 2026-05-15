"""CLI tests for ``scitex-resource skills ...`` (list / get / install)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from scitex_resource._cli import cli


def test_list_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "list"])
    # Assert
    assert result.exit_code == 0


def test_list_mentions_known_skill_stem():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "list"])
    # Assert
    assert "10_machine-identity" in result.output


def test_list_json_returns_a_list():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "list", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), list)


def test_get_known_skill_prints_yaml_frontmatter():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "get", "10_machine-identity"])
    # Assert
    assert result.output.startswith("---")


def test_get_unknown_skill_exits_nonzero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "get", "no-such-skill"])
    # Assert
    assert result.exit_code != 0


def test_install_dry_run_does_not_create_dest(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    dest = tmp_path / "install-here"
    # Act
    runner.invoke(cli, ["skills", "install", "--dest", str(dest), "--dry-run"])
    # Assert
    assert not (dest / "scitex-resource").exists()


def test_install_copy_mode_creates_target(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    dest = tmp_path / "install-here"
    # Act
    runner.invoke(
        cli,
        ["skills", "install", "--dest", str(dest), "--no-link", "-y"],
    )
    # Assert
    assert (dest / "scitex-resource" / "SKILL.md").is_file()
