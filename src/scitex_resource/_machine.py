"""Deprecated alias module — use :mod:`scitex_resource._host` instead.

This module is kept for back-compat. The canonical API moved to
``scitex_resource._host``:

* :func:`get_machine_name` → :func:`scitex_resource.get_host_name`
* :func:`get_machine_config` → :func:`scitex_resource.get_host_config`

Importing this module still works (no warning at import time so cold
import paths stay quiet); the deprecation fires only when the legacy
function names are actually called.
"""

from __future__ import annotations

import warnings
from typing import Any

# Re-export the underlying helpers + names used by tests / CLI internals.
from ._host import (  # noqa: F401
    _ENV_VAR_LEGACY as _ENV_VAR,
)
from ._host import (
    _PKG_SHORT,
    _config_paths,
    _load_yaml,
    _short_hostname,
    get_host_config,
    get_host_name,
    load_config,
)

_DEPRECATION_EMITTED: set[str] = set()


def _warn_once(name: str, replacement: str) -> None:
    if name in _DEPRECATION_EMITTED:
        return
    _DEPRECATION_EMITTED.add(name)
    warnings.warn(
        f"scitex_resource.{name} is deprecated; use scitex_resource.{replacement} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def get_machine_config() -> dict[str, Any]:
    """Deprecated alias for :func:`get_host_config`."""
    _warn_once("get_machine_config", "get_host_config")
    return get_host_config()


def get_machine_name() -> str:
    """Deprecated alias for :func:`get_host_name`."""
    _warn_once("get_machine_name", "get_host_name")
    return get_host_name()


__all__ = [
    "get_machine_config",
    "get_machine_name",
    "get_host_config",
    "get_host_name",
    "load_config",
    "_PKG_SHORT",
    "_ENV_VAR",
    "_config_paths",
    "_load_yaml",
    "_short_hostname",
]
