"""CLI tests for ``scitex-resource processor-usages ...``.

Real psutil reads, real CSV writes to tmp_path — no mocks.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from scitex_resource._cli import cli


def test_show_exits_zero():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["processor-usages", "show"])
    # Assert
    assert result.exit_code == 0


def test_show_text_has_timestamp_column():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["processor-usages", "show"])
    # Assert
    assert "Timestamp" in result.output


def test_show_json_is_a_list():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["processor-usages", "show", "--json"])
    # Assert
    assert isinstance(json.loads(result.output), list)


def test_show_csv_first_line_contains_timestamp():
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(cli, ["processor-usages", "show", "--csv"])
    # Assert
    assert "Timestamp" in result.output.splitlines()[0]


def test_log_creates_csv_file(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    target = tmp_path / "u.csv"
    # Act
    runner.invoke(
        cli,
        [
            "processor-usages",
            "log",
            "--path",
            str(target),
            "--interval",
            "0.01",
            "--max-rows",
            "2",
        ],
    )
    # Assert
    assert target.is_file()


def test_log_csv_has_at_least_one_data_row(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    target = tmp_path / "u.csv"
    # Act
    runner.invoke(
        cli,
        [
            "processor-usages",
            "log",
            "--path",
            str(target),
            "--interval",
            "0.01",
            "--max-rows",
            "2",
        ],
    )
    # Assert
    assert len(target.read_text().splitlines()) >= 2  # header + >=1 data row


def test_log_csv_header_includes_cpu_column(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    target = tmp_path / "u.csv"
    # Act
    runner.invoke(
        cli,
        [
            "processor-usages",
            "log",
            "--path",
            str(target),
            "--interval",
            "0.01",
            "--max-rows",
            "1",
        ],
    )
    # Assert
    assert "CPU [%]" in target.read_text().splitlines()[0]


def test_log_rejects_zero_max_rows(tmp_path: Path):
    # Arrange
    runner = CliRunner()
    target = tmp_path / "u.csv"
    # Act
    result = runner.invoke(
        cli,
        [
            "processor-usages",
            "log",
            "--path",
            str(target),
            "--interval",
            "1",
            "--max-rows",
            "0",
        ],
    )
    # Assert
    assert result.exit_code != 0
