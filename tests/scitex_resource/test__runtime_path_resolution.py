"""Verify that runtime paths resolve under ``/runtime/``.

This test is the gate for Deliverable 1 of the local-state-directories
convention: regenerable data must resolve under ``<pkg>/runtime/``, never
outside it. See ``06_local-state-directories.md`` §4b.
"""

from __future__ import annotations

from pathlib import Path

from scitex_resource._runtime import _runtime_root, default_log_path


def test_runtime_root_has_runtime_in_path():
    # Arrange
    # Act
    root = _runtime_root()
    # Assert
    assert "runtime" in root.parts


def test_default_log_path_ends_with_csv():
    # Arrange
    # Act
    path = default_log_path()
    # Assert
    assert path.endswith("processor_usages.csv")


def test_default_log_path_starts_with_runtime_root():
    # Arrange
    # Act
    path = Path(default_log_path())
    root = _runtime_root()
    # Assert
    assert str(path).startswith(str(root))
