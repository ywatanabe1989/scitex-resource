#!/usr/bin/env python3
"""scitex-resource — system resource info, monitoring, RAM limit (standalone)."""

from __future__ import annotations

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
from ._log_processor_usages import log_processor_usages, main
from ._machine import get_machine_config, get_machine_name, load_config
from ._specs import get_metrics, get_processor_usages, get_specs

__all__ = [
    "__version__",
    "get_machine_config",
    "get_machine_name",
    "get_metrics",
    "get_processor_usages",
    "get_specs",
    "load_config",
    "log_processor_usages",
    "main",
]
