"""Root CLI plumbing: --version, --help, --help-recursive, dev introspection.

`list-commands` / `list-python-apis` moved under the §13 `dev` group; their
old top-level spellings survive as Phase W aliases, pinned in
``test__dev_cmd.py``.

AAA, one-assert-per-test, no mocks. Uses click's CliRunner.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from scitex_resource._cli import cli


def test_help_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"])
    # Assert
    assert result.exit_code == 0


def test_help_advertises_machine_group():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"])
    # Assert
    assert "machine" in result.output


def test_version_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--version"])
    # Assert
    assert result.exit_code == 0


def test_version_prints_program_name():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--version"])
    # Assert
    assert "scitex-resource" in result.output


def test_help_recursive_includes_subcommand_help():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help-recursive"])
    # Assert
    assert "specs show" in result.output


def test_list_commands_includes_hosts_show():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-commands"])
    # Assert
    assert "hosts show" in result.output


def test_list_commands_json_is_parseable():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-commands", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), list)


def test_list_commands_json_includes_metrics_show():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-commands", "--json"])
    # Assert
    assert any(item["command"] == "metrics show" for item in json.loads(result.output))


def test_list_python_apis_lists_get_specs():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-python-apis"])
    # Assert
    assert "get_specs" in result.output


def test_list_python_apis_json_lists_get_metrics():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-python-apis", "--json"])
    # Assert
    names = {a["name"] for a in json.loads(result.output)["apis"]}
    assert "get_metrics" in names
