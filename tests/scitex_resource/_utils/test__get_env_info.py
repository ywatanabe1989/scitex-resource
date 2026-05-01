#!/usr/bin/env python3
"""Tests for scitex_resource._utils._get_env_info.

The function shells out to gather system info — tests verify that it
returns a populated SystemEnv namedtuple with the expected fields, and
that the helper module exports the SystemEnv type.
"""

import pytest

from scitex_resource._utils._get_env_info import (
    SystemEnv,
    get_env_info,
)


class TestSystemEnvNamedTuple:
    def test_is_namedtuple(self):
        # NamedTuples are tuple subclasses with named fields.
        assert issubclass(SystemEnv, tuple)
        assert hasattr(SystemEnv, "_fields")

    def test_has_expected_fields(self):
        # Spot-check the canonical SystemEnv shape.
        for f in (
            "torch_version",
            "is_debug_build",
            "cuda_compiled_version",
            "gcc_version",
            "os",
            "python_version",
        ):
            assert f in SystemEnv._fields, f"missing field: {f}"


class TestGetEnvInfo:
    def test_returns_systemenv_instance(self):
        info = get_env_info()
        assert isinstance(info, SystemEnv)

    def test_python_version_populated(self):
        info = get_env_info()
        # Python version should at least contain "3." since this runs on
        # any modern Python.
        assert info.python_version
        assert "3." in str(info.python_version)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
