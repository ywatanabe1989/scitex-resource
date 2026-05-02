#!/usr/bin/env python3
"""System spec/metric/usage collectors.

Subpackage grouping the three system-info getters that previously sat as
flat ``_get_*.py`` modules at the package root (PS108 reorganization).
"""

from __future__ import annotations

from ._metrics import get_metrics
from ._processor_usages import get_processor_usages
from ._specs import (
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

__all__ = [
    "get_metrics",
    "get_processor_usages",
    "get_specs",
]
