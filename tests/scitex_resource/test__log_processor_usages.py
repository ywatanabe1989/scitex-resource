"""Real-I/O tests for ``scitex_resource._log_processor_usages``.

No mocks. ``_log_processor_usages`` is exercised with sub-second intervals
against a real tmp_path CSV file.
"""

from __future__ import annotations

import pandas as pd
import pytest

from scitex_resource._log_processor_usages import (
    _add,
    _ensure_log_file,
    _log_processor_usages,
)


def test_ensure_log_file_creates_file(tmp_path):
    # Arrange
    path = str(tmp_path / "log.csv")
    # Act
    _ensure_log_file(path, init=True)
    # Assert
    assert (tmp_path / "log.csv").is_file()


def test_ensure_log_file_writes_header_row(tmp_path):
    # Arrange
    path = str(tmp_path / "log.csv")
    # Act
    _ensure_log_file(path, init=True)
    # Assert
    assert (tmp_path / "log.csv").read_text().startswith("Timestamp,CPU [%]")


def test_ensure_log_file_reinit_truncates_existing(tmp_path):
    # Arrange
    path = tmp_path / "log.csv"
    path.write_text("garbage,data,here\n1,2,3\n")
    # Act
    _ensure_log_file(str(path), init=True)
    # Assert
    assert path.read_text().startswith("Timestamp,CPU [%]")


def test_ensure_log_file_no_init_keeps_existing(tmp_path):
    # Arrange
    path = tmp_path / "log.csv"
    path.write_text("untouched\n")
    # Act
    _ensure_log_file(str(path), init=False)
    # Assert
    assert path.read_text() == "untouched\n"


def test_add_appends_one_row(tmp_path):
    # Arrange
    path = str(tmp_path / "log.csv")
    _ensure_log_file(path, init=True)
    # Act
    _add(path, verbose=False)
    # Assert
    assert len(pd.read_csv(path)) == 1


def test_log_processor_usages_rejects_non_csv_path(tmp_path):
    # Arrange
    path = str(tmp_path / "log.txt")
    # Act
    raised_ctx = pytest.raises(AssertionError)
    # Assert
    with raised_ctx:
        _log_processor_usages(path=path, limit_min=0.01, interval_s=0.5)


def test_log_processor_usages_creates_csv_with_rows(tmp_path):
    # Arrange
    path = str(tmp_path / "log.csv")
    # Act
    _log_processor_usages(
        path=path,
        limit_min=0.02,
        interval_s=0.5,
        init=True,
        verbose=False,
    )
    # Assert
    assert len(pd.read_csv(path)) >= 1
