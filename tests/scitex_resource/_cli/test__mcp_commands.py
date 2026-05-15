"""CLI tests for ``scitex-resource mcp ...`` group."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_resource._cli import cli


def test_mcp_doctor_exits_zero():
    # Arrange
    pytest.importorskip("fastmcp")
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "doctor"])
    # Assert
    assert result.exit_code == 0


def test_mcp_install_text_includes_pip_command():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "install"])
    # Assert
    assert "pip install scitex-resource[mcp]" in result.output


def test_mcp_install_json_has_mcp_servers_key():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "install", "--json"])
    # Assert
    assert "mcpServers" in json.loads(result.output)["config"]


def test_mcp_list_tools_includes_get_machine_name():
    # Arrange
    pytest.importorskip("fastmcp")
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "list-tools"])
    # Assert
    assert "get_machine_name" in result.output


def test_mcp_list_tools_json_total_matches_array_length():
    # Arrange
    pytest.importorskip("fastmcp")
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "list-tools", "--json"])
    # Assert
    payload = json.loads(result.output)
    assert payload["total"] == len(payload["tools"])


def test_mcp_start_dry_run_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["mcp", "start", "--dry-run"])
    # Assert
    assert result.exit_code == 0
