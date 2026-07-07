"""Regression: importing the spec/usage collectors must NOT import the heavy
scientific stack (matplotlib, pandas).

``scitex_resource._specs`` is on the ``scitex_resource._mcp.server`` import
path (``get_specs`` / ``get_processor_usages`` are MCP tools). The umbrella
MCP aggregator imports every peer's ``_mcp.server`` serially under a
per-peer timeout during cold-start, so a heavy top-level import there
darkens the whole aggregator's boot.

Two eager imports were the offenders:

- ``import matplotlib.pyplot`` (font-cache build) — now deferred into the
  modules' ``__main__`` demo blocks.
- ``import pandas as pd`` in ``_processor_usages`` (~1 s) — now deferred
  into ``get_processor_usages`` (the only function that builds a DataFrame),
  with ``from __future__ import annotations`` keeping the ``-> pd.DataFrame``
  return annotation a string.

A fresh interpreter that imports the collectors (or ``_mcp.server``) must
leave both matplotlib and pandas out of ``sys.modules``. Uses a subprocess
(isolated interpreter) so the assertion holds regardless of what the pytest
process itself has already imported — no mocks.
"""

from __future__ import annotations

import subprocess
import sys


def _module_absent_after_import(imported: str, forbidden: str) -> bool:
    code = (
        f"import importlib, sys; importlib.import_module({imported!r}); "
        f"sys.exit(1 if {forbidden!r} in sys.modules else 0)"
    )
    return subprocess.run([sys.executable, "-c", code]).returncode == 0


def _matplotlib_absent_after_import(module: str) -> bool:
    return _module_absent_after_import(module, "matplotlib")


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


def test_importing_processor_usages_does_not_import_pandas():
    # Arrange
    module = "scitex_resource._specs._processor_usages"
    # Act
    absent = _module_absent_after_import(module, "pandas")
    # Assert
    assert absent is True


def test_importing_specs_subpackage_does_not_import_pandas():
    # Arrange
    module = "scitex_resource._specs"
    # Act
    absent = _module_absent_after_import(module, "pandas")
    # Assert
    assert absent is True


def test_importing_mcp_server_does_not_import_pandas():
    # Arrange — the aggregator imports this exact module per peer.
    module = "scitex_resource._mcp.server"
    # Act
    absent = _module_absent_after_import(module, "pandas")
    # Assert
    assert absent is True
