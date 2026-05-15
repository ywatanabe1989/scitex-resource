"""CLI tests for ``scitex-resource ram-limit ...``.

NOTE: We deliberately do NOT actually call ``ram-limit set`` with a low
factor because RLIMIT_AS persists for the rest of the pytest process —
that would surface as MemoryError in unrelated tests. Validation tests
use factors out of range so the CLI rejects them before touching
``setrlimit``.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from scitex_resource._cli import cli


def test_get_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "get"])
    # Assert
    assert result.exit_code == 0


def test_get_text_includes_free_kib_label():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "get"])
    # Assert
    assert "free_kib" in result.output


def test_get_json_has_int_free_kib():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "get", "--json"])
    # Assert
    assert isinstance(json.loads(result.output)["free_kib"], int)


def test_set_rejects_factor_above_one():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "set", "2.0"])
    # Assert
    assert result.exit_code != 0


def test_set_rejects_factor_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "set", "0"])
    # Assert
    assert result.exit_code != 0


def test_set_rejects_negative_factor():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["ram-limit", "set", "-0.5"])
    # Assert
    assert result.exit_code != 0
