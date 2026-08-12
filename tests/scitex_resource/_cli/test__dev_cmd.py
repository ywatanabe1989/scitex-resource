"""§13 `dev` group + the Phase W aliases that keep the old spellings alive.

The CLI is a published contract: `scitex-resource skills list` and friends
live in scripts, cron lines and agent prompts that are not greppable from
this repository. These tests pin BOTH halves of the migration — the new
`dev`-nested path works, and the old top-level path still executes while
being hidden from `--help`.

AAA, one-assert-per-test, no mocks. Uses click's CliRunner.
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_resource._cli import cli
from scitex_resource._cli._dev_cmd import _MOVED

# ----------------------------------------------------------- the `dev` group


def test_dev_group_is_registered():
    # Arrange
    root = cli
    # Act
    dev = root.commands.get("dev")
    # Assert
    assert dev is not None


@pytest.mark.parametrize("name", _MOVED)
def test_moved_command_is_mounted_under_dev(name):
    # Arrange
    dev = cli.commands["dev"]
    # Act
    mounted = dev.commands.get(name)
    # Assert
    assert mounted is not None


def test_dev_help_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "--help"])
    # Assert
    assert result.exit_code == 0


def test_root_help_advertises_dev_group():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"])
    # Assert
    assert "dev" in result.output


# ------------------------------------------------- the new `dev`-nested paths


def test_dev_skills_list_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "skills", "list"])
    # Assert
    assert result.exit_code == 0


def test_dev_list_python_apis_lists_get_specs():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-python-apis"])
    # Assert
    assert "get_specs" in result.output


def test_dev_list_commands_reports_dev_nested_paths():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["dev", "list-commands", "--json"])
    # Assert
    commands = {item["command"] for item in json.loads(result.output)}
    assert "dev list-python-apis" in commands


# --------------------------------------------- the Phase W deprecated aliases


@pytest.mark.parametrize("name", _MOVED)
def test_alias_is_registered_at_top_level(name):
    # Arrange
    root = cli
    # Act
    alias = root.commands.get(name)
    # Assert
    assert alias is not None


@pytest.mark.parametrize("name", _MOVED)
def test_alias_is_hidden_from_help(name):
    # Arrange
    alias = cli.commands[name]
    # Act
    hidden = alias.hidden
    # Assert
    assert hidden is True


@pytest.mark.parametrize("name", _MOVED)
def test_alias_carries_deprecation_metadata_for_the_auditor(name):
    # Arrange
    alias = cli.commands[name]
    # Act
    meta = getattr(alias, "_deprecated_alias", None)
    # Assert — the §13 escape hatch keys on hidden + this dict
    assert meta == {
        "target": f"dev {name}",
        "remove_in": "0.8.0",
        "phase": "warn",
    }


@pytest.mark.parametrize("name", _MOVED)
def test_alias_is_absent_from_root_help_listing(name):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"])
    # Assert — the whole point of hiding: `--help` reads as the tool
    assert f"\n  {name} " not in result.output


def test_old_skills_list_still_executes():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["skills", "list"])
    # Assert
    assert result.exit_code == 0


def test_old_skills_list_returns_same_payload_as_new_path(tmp_path):
    # Arrange
    runner = CliRunner()
    env = {"XDG_RUNTIME_DIR": str(tmp_path)}
    # Act
    old = runner.invoke(cli, ["skills", "list", "--json"], env=env)
    new = runner.invoke(cli, ["dev", "skills", "list", "--json"], env=env)
    # Assert — read `stdout`, never `output`: this click merges stderr into
    # `output`, so the once-per-shell warning would corrupt the payload.
    assert json.loads(old.stdout) == json.loads(new.stdout)


def test_old_skills_get_forwards_its_argument(tmp_path):
    # Arrange
    runner = CliRunner()
    env = {"XDG_RUNTIME_DIR": str(tmp_path)}
    # Act — a positional through the alias must reach the target
    result = runner.invoke(
        cli, ["skills", "get", "10_machine-identity"], env=env
    )
    # Assert
    assert result.stdout.startswith("---")


def test_old_list_python_apis_still_executes():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["list-python-apis"])
    # Assert
    assert "get_specs" in result.stdout


def test_old_list_python_apis_forwards_the_json_flag(tmp_path):
    # Arrange
    runner = CliRunner()
    env = {"XDG_RUNTIME_DIR": str(tmp_path)}
    # Act — an OPTION through the alias must be re-parsed by the target
    result = runner.invoke(cli, ["list-python-apis", "--json"], env=env)
    # Assert
    assert json.loads(result.stdout)["module"] == "scitex_resource"


def test_old_list_commands_still_executes():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["list-commands"])
    # Assert
    assert "hosts show" in result.stdout


def test_old_skills_help_reaches_the_target_group(tmp_path):
    # Arrange
    runner = CliRunner()
    # Act — a GROUP alias must hand `--help` to the target, not answer itself
    result = runner.invoke(
        cli, ["skills", "--help"], env={"XDG_RUNTIME_DIR": str(tmp_path)}
    )
    # Assert
    assert "install" in result.stdout


def test_alias_warns_once_per_shell_session(tmp_path):
    # Arrange
    runner = CliRunner()
    env = {"XDG_RUNTIME_DIR": str(tmp_path)}
    # Act
    result = runner.invoke(cli, ["skills", "list"], env=env)
    # Assert
    assert "'skills' is deprecated — use 'dev skills'" in result.stderr


# ---------------------------------------------------------- surfaces that STAY


@pytest.mark.parametrize(
    "name",
    ["hosts", "specs", "metrics", "processor-usages", "ram-limit", "mcp"],
)
def test_domain_and_service_verbs_stay_at_top_level(name):
    # Arrange
    root = cli
    # Act
    command = root.commands.get(name)
    # Assert — §11 keeps `mcp` and the domain verbs out of `dev`
    assert command is not None and not command.hidden


@pytest.mark.parametrize(
    "name", ["install-shell-completion", "print-shell-completion"]
)
def test_completion_leaves_stay_at_top_level(name):
    # Arrange
    root = cli
    # Act
    command = root.commands.get(name)
    # Assert — §11 lists the completion surface as NOT-in-`dev`
    assert command is not None and not command.hidden


def test_section_13_audit_reports_no_violation():
    # Arrange
    from scitex_dev._cli.audit._summary._dev_group import (
        check_dev_command_group,
    )

    findings: list = []
    # Act
    check_dev_command_group(cli, "scitex-resource", findings)
    # Assert
    assert findings == []
