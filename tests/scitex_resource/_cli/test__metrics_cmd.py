"""CLI tests for ``scitex-resource metrics show``."""

from __future__ import annotations

import json

from click.testing import CliRunner

from scitex_resource._cli import cli


def test_metrics_show_json_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu", "--json"])
    # Assert
    assert result.exit_code == 0


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


def test_metrics_show_text_includes_mem_total_label():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["metrics", "show", "--no-gpu"])
    # Assert
    assert "mem_total_mb" in result.output
