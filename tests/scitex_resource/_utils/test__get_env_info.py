"""Tests for ``scitex_resource._utils._get_env_info``.

Shells out to gather real system info — no mocks.
"""

from __future__ import annotations

import pytest

from scitex_resource._utils._get_env_info import SystemEnv, get_env_info


def test_systemenv_is_tuple_subclass():
    # Arrange
    # Act
    is_tuple = issubclass(SystemEnv, tuple)
    # Assert
    assert is_tuple


def test_systemenv_has_namedtuple_fields_attr():
    # Arrange
    # Act
    has_fields = hasattr(SystemEnv, "_fields")
    # Assert
    assert has_fields


@pytest.mark.parametrize(
    "field",
    [
        "torch_version",
        "is_debug_build",
        "cuda_compiled_version",
        "gcc_version",
        "os",
        "python_version",
    ],
)
def test_systemenv_has_expected_field(field):
    # Arrange
    # Act
    fields = SystemEnv._fields
    # Assert
    assert field in fields


def test_get_env_info_returns_systemenv_instance():
    # Arrange
    # Act
    info = get_env_info()
    # Assert
    assert isinstance(info, SystemEnv)


def test_get_env_info_python_version_populated():
    # Arrange
    # Act
    info = get_env_info()
    # Assert
    assert "3." in str(info.python_version)
