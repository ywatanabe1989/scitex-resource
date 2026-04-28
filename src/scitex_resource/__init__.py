#!/usr/bin/env python3
"""scitex-resource — system resource info, monitoring, RAM limit (standalone)."""

try:
    from importlib.metadata import version as _v, PackageNotFoundError
    try:
        __version__ = _v("scitex-resource")
    except PackageNotFoundError:
        __version__ = "0.0.0+local"
    del _v, PackageNotFoundError
except ImportError:  # pragma: no cover — only on ancient Pythons
    __version__ = "0.0.0+local"
from ._get_metrics import get_metrics
from ._get_processor_usages import get_processor_usages
from ._get_specs import (
    _cpu_info,
    _disk_info,
    _memory_info,
    _network_info,
    _supple_nvidia_info,
    _supple_os_info,
    _supple_python_info,
    _system_info,
    get_specs,
)
from ._log_processor_usages import log_processor_usages, main
from ._machine import get_machine_config, get_machine_name, load_config

__all__ = [
    "get_machine_config",
    "get_machine_name",
    "get_metrics",
    "get_processor_usages",
    "get_specs",
    "load_config",
    "log_processor_usages",
    "main",
    "_cpu_info",
    "_disk_info",
    "_memory_info",
    "_network_info",
    "_supple_nvidia_info",
    "_supple_os_info",
    "_supple_python_info",
    "_system_info",
]
