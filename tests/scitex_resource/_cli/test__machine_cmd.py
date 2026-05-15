"""CLI tests for ``scitex-resource machine ...``.

Uses real env-var mutation (no monkeypatch fixture) to pin a known
canonical name into the resolution cascade.
"""

from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from scitex_resource._cli import cli


@pytest.fixture
def pinned_machine():
    """Pin ``$SCITEX_RESOURCE_MACHINE`` to a known value for one test."""
    # Arrange
    key = "SCITEX_RESOURCE_MACHINE"
    prior = os.environ.get(key)
    os.environ[key] = "test-host-42"
    try:
        yield "test-host-42"
    finally:
        if prior is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = prior


def test_machine_show_exits_zero(pinned_machine):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show"])
    # Assert
    assert result.exit_code == 0


def test_machine_show_prints_pinned_name(pinned_machine):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show"])
    # Assert
    assert pinned_machine in result.output


def test_machine_show_json_matches_pinned_name(pinned_machine):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show", "--json"])
    # Assert
    assert json.loads(result.output) == {"machine": pinned_machine}


def test_machine_show_config_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show-config", "--json"])
    # Assert
    assert result.exit_code == 0


def test_machine_show_config_json_is_dict():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["machine", "show-config", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), dict)
