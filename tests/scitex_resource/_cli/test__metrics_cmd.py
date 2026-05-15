"""CLI tests for ``scitex-resource metrics show``.

Default output is human-readable; ``--json`` for scripts, ``--yaml`` for
``yq``. Real psutil reads — assertions are on shape, never exact values.
"""

from __future__ import annotations

import json
import re

import yaml as _yaml
from click.testing import CliRunner

from scitex_resource._cli import cli

# ---------------------------------------------------------------------------
# --json


def test_metrics_show_json_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert result.exit_code == 0


def test_metrics_show_json_parses_as_dict():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), dict)


def test_metrics_show_json_has_cpu_count_key():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert "cpu_count" in json.loads(result.output)


def test_metrics_show_json_cpu_count_is_int():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert isinstance(json.loads(result.output)["cpu_count"], int)


def test_metrics_show_no_gpu_yields_empty_gpu_list():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert json.loads(result.output)["gpus"] == []


# ---------------------------------------------------------------------------
# --yaml


def test_metrics_show_yaml_parses_with_safe_load():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--yaml"])
    # Assert
    assert isinstance(_yaml.safe_load(result.output), dict)


# ---------------------------------------------------------------------------
# Default (human-readable)


def test_metrics_show_default_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert result.exit_code == 0


def test_metrics_show_default_strips_mb_suffix_on_mem_total():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert re.search(r"\bmem_total\b", result.output)


def test_metrics_show_default_renders_load_avg_group():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert "1m / 5m / 15m" in result.output


def test_metrics_show_default_renders_empty_gpu_list_as_none():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert "gpus: (none)" in result.output


def test_metrics_show_default_scales_mem_total_to_gb_or_tb():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert re.search(r"mem_total\s+\d+(?:\.\d+)?\s+(GB|TB)", result.output)
