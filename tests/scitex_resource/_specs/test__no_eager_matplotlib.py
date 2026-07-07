"""Regression: importing the spec/usage collectors must NOT import matplotlib.

``scitex_resource._specs`` is on the ``scitex_resource._mcp.server`` import
path (``get_specs`` / ``get_processor_usages`` are MCP tools). A top-level
``import matplotlib.pyplot`` there eagerly triggered matplotlib's
font-cache build, darkening the umbrella MCP aggregator's cold-start.
matplotlib is now deferred into the modules' ``__main__`` demo blocks, so
a fresh interpreter that imports the collectors must leave matplotlib out
of ``sys.modules``.

Uses a subprocess (isolated interpreter) so the assertion holds regardless
of what the pytest process itself has already imported — no mocks.
"""

from __future__ import annotations

import subprocess
import sys


def _matplotlib_absent_after_import(module: str) -> bool:
    code = (
        f"import importlib, sys; importlib.import_module({module!r}); "
        "sys.exit(1 if 'matplotlib' in sys.modules else 0)"
    )
    return subprocess.run([sys.executable, "-c", code]).returncode == 0


def test_importing_specs_module_does_not_import_matplotlib():
    # Arrange
    module = "scitex_resource._specs._specs"
    # Act
    absent = _matplotlib_absent_after_import(module)
    # Assert
    assert absent is True


def test_importing_processor_usages_does_not_import_matplotlib():
    # Arrange
    module = "scitex_resource._specs._processor_usages"
    # Act
    absent = _matplotlib_absent_after_import(module)
    # Assert
    assert absent is True


def test_importing_specs_subpackage_does_not_import_matplotlib():
    # Arrange
    module = "scitex_resource._specs"
    # Act
    absent = _matplotlib_absent_after_import(module)
    # Assert
    assert absent is True
