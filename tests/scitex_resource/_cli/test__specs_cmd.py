"""CLI tests for ``scitex-resource specs show``.

psutil reads real /proc — we only assert structure, never exact values.
"""

from __future__ import annotations

import json

import yaml as _yaml
from click.testing import CliRunner

from scitex_resource._cli import cli


def test_specs_show_json_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        ["specs", "show", "--no-gpu", "--no-network", "--no-disk", "--json"],
    )
    # Assert
    assert result.exit_code == 0


def test_specs_show_json_has_collected_time():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        ["specs", "show", "--no-gpu", "--no-network", "--no-disk", "--json"],
    )
    # Assert
    assert "Collected Time" in json.loads(result.output)


def test_specs_show_yaml_parses_with_safe_load():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        ["specs", "show", "--no-gpu", "--no-network", "--no-disk", "--yaml"],
    )
    # Assert
    assert isinstance(_yaml.safe_load(result.output), dict)


def test_specs_show_default_includes_collected_time():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        ["specs", "show", "--no-gpu", "--no-network", "--no-disk"],
    )
    # Assert
    assert "Collected Time" in result.output


def test_specs_show_default_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        ["specs", "show", "--no-gpu", "--no-network", "--no-disk"],
    )
    # Assert
    assert result.exit_code == 0


def test_specs_show_no_system_omits_node_name_field():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(
        cli,
        [
            "specs",
            "show",
            "--no-system",
            "--no-gpu",
            "--no-disk",
            "--no-network",
            "--json",
        ],
    )
    # Assert
    assert "System Information" not in json.loads(result.output)
