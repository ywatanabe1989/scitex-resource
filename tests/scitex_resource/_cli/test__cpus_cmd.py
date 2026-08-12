"""CLI tests for ``scitex-resource cpus show``.

Real reads against this host — assertions are on shape and on invariants
that hold everywhere, never on a CPU count only this machine has.

``--count`` is the surface shell scripts interpolate directly
(``WORKERS="$(scitex-resource cpus show --count)"``), so its output being a
bare integer with nothing else on stdout is a contract, not a nicety.
"""

from __future__ import annotations

import json

import yaml as _yaml
from click.testing import CliRunner

from scitex_resource._cli import cli

# ---------------------------------------------------------------------------
# --count : the shell contract


def test_cpus_show_count_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--count"])
    # Assert
    assert result.exit_code == 0


def test_cpus_show_count_prints_a_bare_integer():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--count"])
    # Assert
    assert result.output.strip().isdigit()


def test_cpus_show_count_prints_exactly_one_line():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--count"])
    # Assert
    assert len(result.output.strip().splitlines()) == 1


def test_cpus_show_count_is_at_least_one():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--count"])
    # Assert
    assert int(result.output.strip()) >= 1


def test_cpus_show_count_honours_the_minimum_floor():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--count", "--minimum", "9999"])
    # Assert
    assert int(result.output.strip()) == 9999


# ---------------------------------------------------------------------------
# --json


def test_cpus_show_json_parses_as_dict():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), dict)


def test_cpus_show_json_usable_is_int():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--json"])
    # Assert
    assert isinstance(json.loads(result.output)["usable"], int)


def test_cpus_show_json_reports_every_source_not_only_the_winner():
    # Arrange
    runner = CliRunner()
    expected = {
        "affinity",
        "affinity_source",
        "cpu_count",
        "omp_num_threads",
        "slurm_cpus_on_node",
        "slurm_cpus_per_task",
        "source",
        "usable",
    }
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--json"])
    # Assert
    assert set(json.loads(result.output)) == expected


def test_cpus_show_json_names_the_winning_source():
    # Arrange
    runner = CliRunner()
    valid = {
        "affinity",
        "slurm_cpus_per_task",
        "slurm_cpus_on_node",
        "cpu_count",
        "default",
        "minimum",
    }
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--json"])
    # Assert
    assert json.loads(result.output)["source"] in valid


def test_cpus_show_json_marks_the_source_as_minimum_when_the_floor_wins():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--json", "--minimum", "9999"])
    # Assert
    assert json.loads(result.output)["source"] == "minimum"


# ---------------------------------------------------------------------------
# --yaml and the default human shape


def test_cpus_show_yaml_parses_with_safe_load():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show", "--yaml"])
    # Assert
    assert isinstance(_yaml.safe_load(result.output), dict)


def test_cpus_show_default_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show"])
    # Assert
    assert result.exit_code == 0


def test_cpus_show_default_renders_the_usable_row():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show"])
    # Assert
    assert "usable" in result.output


def test_cpus_show_default_renders_the_losing_sources_too():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["cpus", "show"])
    # Assert
    assert "cpu_count" in result.output


# ---------------------------------------------------------------------------
# Registration in the root group


def test_cpus_group_is_listed_in_root_help():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["--help"])
    # Assert
    assert "cpus" in result.output
