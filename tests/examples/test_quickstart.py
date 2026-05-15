"""Compile-only smoke test for examples/quickstart.py."""

from __future__ import annotations

import py_compile
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "quickstart.py"


def test_quickstart_example_file_exists():
    # Arrange
    # Act
    is_file = EXAMPLE.is_file()
    # Assert
    assert is_file, f"missing example: {EXAMPLE}"


def test_quickstart_example_compiles_without_syntax_error():
    # Arrange
    target = str(EXAMPLE)
    # Act
    compiled = py_compile.compile(target, doraise=True)
    # Assert
    assert compiled is not None
