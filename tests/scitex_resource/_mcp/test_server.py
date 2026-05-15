"""Smoke + tool-registration tests for the scitex-resource MCP server."""

from __future__ import annotations

import asyncio

import pytest


def test_mcp_server_module_imports_cleanly():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    from scitex_resource._mcp.server import mcp

    # Assert
    assert mcp is not None


def test_mcp_server_has_expected_name():
    # Arrange
    pytest.importorskip("fastmcp")
    from scitex_resource._mcp.server import mcp

    # Act
    name = getattr(mcp, "name", None)
    # Assert
    assert name == "scitex-resource"


def _tool_names() -> set[str]:
    from scitex_resource._mcp.server import mcp

    tools = asyncio.run(mcp.list_tools())
    return {getattr(t, "name", None) for t in tools}


def test_skills_list_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "skills_list" in names


def test_skills_get_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "skills_get" in names


def test_get_machine_name_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_machine_name" in names


def test_get_machine_config_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_machine_config" in names


def test_get_specs_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_specs" in names


def test_get_metrics_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_metrics" in names


def test_get_processor_usages_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_processor_usages" in names


def test_log_processor_usages_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "log_processor_usages" in names


def test_limit_ram_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "limit_ram" in names


def test_get_ram_tool_registered():
    # Arrange
    pytest.importorskip("fastmcp")
    # Act
    names = _tool_names()
    # Assert
    assert "get_ram" in names
