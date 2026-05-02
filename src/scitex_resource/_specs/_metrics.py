"""Flat, machine-readable resource metrics for monitoring/heartbeat use.

Companion to ``get_specs()`` (which is rich + human-formatted). ``get_metrics()``
returns a flat dict of integers, floats and short strings — the shape any hub,
dashboard, or heartbeat producer can ship over the wire without reshaping.

Cross-platform via ``psutil`` (Linux / macOS / Windows / WSL). Container-aware:
inside Docker / cgroups, ``psutil.virtual_memory()`` reports the cgroup limit,
not the host kernel's view, so the numbers reflect what the process can
actually use.

Schema (treat as a public contract; bump minor on rename):

    cpu_count          int     logical CPU count (psutil.cpu_count())
    cpu_model          str     human-readable CPU model name; "" if unknown
    load_avg_1m/5m/15m float   POSIX load averages; psutil emulates on Windows
    mem_total_mb       int     RAM total in MiB
    mem_used_mb        int     "used" excluding cache/buffers (psutil's notion)
    mem_free_mb        int     psutil's available — what apps can grab now
    mem_used_percent   float   psutil.virtual_memory().percent
    disk_total_mb      int     home-directory partition total in MiB
    disk_used_mb       int     home-directory partition used in MiB
    disk_used_percent  float   home-directory partition percent
    gpus               list    [{"name", "vram_total_mb", "vram_used_mb"}, ...]
                               empty list when no NVIDIA GPU / nvidia-smi missing

The ``gpu=False`` flag skips the ~200 ms ``nvidia-smi`` shellout for hot paths
that don't need GPU info (e.g. 30 s heartbeats on GPU-less hosts).
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from typing import Any

import psutil as _psutil

log = logging.getLogger(__name__)


def get_metrics(gpu: bool = True) -> dict[str, Any]:
    """Return a flat dict of current system metrics suitable for heartbeats.

    Parameters
    ----------
    gpu : bool
        When ``True`` (default) probe NVIDIA GPUs via ``nvidia-smi``. Set to
        ``False`` on hot paths to skip the ~200 ms shellout when you know
        there's no GPU or when you cache GPU info separately.

    Returns
    -------
    dict
        See module docstring for the full key list and contract.
    """
    metrics: dict[str, Any] = {}

    metrics["cpu_count"] = _psutil.cpu_count(logical=True) or 0
    metrics["cpu_model"] = _cpu_model()

    load1, load5, load15 = _load_avg()
    metrics["load_avg_1m"] = load1
    metrics["load_avg_5m"] = load5
    metrics["load_avg_15m"] = load15

    vm = _psutil.virtual_memory()
    metrics["mem_total_mb"] = int(vm.total // (1024 * 1024))
    metrics["mem_used_mb"] = int((vm.total - vm.available) // (1024 * 1024))
    metrics["mem_free_mb"] = int(vm.available // (1024 * 1024))
    metrics["mem_used_percent"] = round(float(vm.percent), 1)

    try:
        du = _psutil.disk_usage(os.path.expanduser("~"))
        metrics["disk_total_mb"] = int(du.total // (1024 * 1024))
        metrics["disk_used_mb"] = int(du.used // (1024 * 1024))
        metrics["disk_used_percent"] = round(float(du.percent), 1)
    except OSError:
        metrics["disk_total_mb"] = 0
        metrics["disk_used_mb"] = 0
        metrics["disk_used_percent"] = 0.0

    metrics["gpus"] = _nvidia_gpus() if gpu else []

    return metrics


def _cpu_model() -> str:
    """Cross-platform CPU model string. Empty string if undetectable."""
    import platform

    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
    if platform.system() == "Darwin":
        try:
            out = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                text=True,
                timeout=1,
            )
            return out.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or ""


def _load_avg() -> tuple[float, float, float]:
    """POSIX load averages. psutil emulates on Windows from CPU samples."""
    try:
        load1, load5, load15 = _psutil.getloadavg()
        return round(float(load1), 2), round(float(load5), 2), round(float(load15), 2)
    except (OSError, AttributeError):
        return 0.0, 0.0, 0.0


def _nvidia_gpus() -> list[dict[str, Any]]:
    """List of NVIDIA GPUs via nvidia-smi. Empty list if not available."""
    if not shutil.which("nvidia-smi"):
        return []
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    gpus: list[dict[str, Any]] = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 3:
            continue
        try:
            gpus.append(
                {
                    "name": parts[0],
                    "vram_total_mb": int(parts[1]),
                    "vram_used_mb": int(parts[2]),
                }
            )
        except ValueError:
            continue
    return gpus
