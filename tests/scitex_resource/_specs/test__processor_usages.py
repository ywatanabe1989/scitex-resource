"""Real-I/O tests for ``scitex_resource._specs._processor_usages.get_processor_usages``.

No mocks — exercises the real psutil / nvidia-smi pipeline.
"""

from __future__ import annotations

import pandas as pd

from scitex_resource import get_processor_usages


def test_get_processor_usages_returns_dataframe():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert isinstance(df, pd.DataFrame)


def test_get_processor_usages_dataframe_has_one_row():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert len(df) == 1


def test_get_processor_usages_dataframe_has_timestamp_column():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert "Timestamp" in df.columns


def test_get_processor_usages_dataframe_has_cpu_column():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert "CPU [%]" in df.columns


def test_get_processor_usages_dataframe_has_ram_column():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert "RAM [GiB]" in df.columns


def test_get_processor_usages_cpu_value_is_finite():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert pd.notna(df.iloc[0]["CPU [%]"])


def test_get_processor_usages_ram_value_non_negative():
    # Arrange
    # Act
    df = get_processor_usages()
    # Assert
    assert df.iloc[0]["RAM [GiB]"] >= 0
