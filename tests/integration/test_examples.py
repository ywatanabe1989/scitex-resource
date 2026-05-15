"""Smoke test: every example script under examples/ runs to completion."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = list(Path(__file__).parent.parent.joinpath("examples").glob("*.py"))


@pytest.mark.parametrize("example_path", EXAMPLES, ids=[p.name for p in EXAMPLES])
def test_example_script_exits_zero(tmp_path, example_path):
    # Arrange
    cmd = [sys.executable, str(example_path)]
    # Act
    result = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, text=True, timeout=60
    )
    # Assert
    assert result.returncode == 0, (
        f"{example_path.name} failed:\nSTDOUT:\n{result.stdout}"
        f"\nSTDERR:\n{result.stderr}"
    )
