#!/usr/bin/env python3
"""scitex-resource — system resource info, monitoring, RAM limit (standalone).

Public API is loaded lazily via PEP 562 `__getattr__` so `import
scitex_resource` stays fast (<100ms cold-start) — Click runs the CLI
program once per Tab press for completion, and pulling in
matplotlib/psutil/yaml at top-level made that path ~2s slow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _v

    try:
        __version__ = _v("scitex-resource")
    except PackageNotFoundError:
        __version__ = "0.0.0+local"
    del _v, PackageNotFoundError
except ImportError:  # pragma: no cover — only on ancient Pythons
    __version__ = "0.0.0+local"


_LAZY = {
    # name → (relative module, attribute)
    "get_machine_config": ("._machine", "get_machine_config"),
    "get_machine_name": ("._machine", "get_machine_name"),
    "load_config": ("._machine", "load_config"),
    "get_metrics": ("._specs", "get_metrics"),
    "get_processor_usages": ("._specs", "get_processor_usages"),
    "get_specs": ("._specs", "get_specs"),
    "log_processor_usages": ("._log_processor_usages", "log_processor_usages"),
    "main": ("._log_processor_usages", "main"),
}

__all__ = ["__version__", *_LAZY.keys()]


def __getattr__(name: str):
    if name not in _LAZY:
        raise AttributeError(f"module 'scitex_resource' has no attribute {name!r}")
    import importlib

    modpath, attr = _LAZY[name]
    obj = getattr(importlib.import_module(modpath, __name__), attr)
    globals()[name] = obj  # cache for next access
    return obj


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


if TYPE_CHECKING:  # pragma: no cover — IDE / static-check support
    from ._log_processor_usages import log_processor_usages, main
    from ._machine import get_machine_config, get_machine_name, load_config
    from ._specs import get_metrics, get_processor_usages, get_specs
