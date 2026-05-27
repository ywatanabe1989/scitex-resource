"""scitex-resource MCP server — single FastMCP instance per package (§1).

Tool names mirror the canonical Python API (`get_machine_name`,
`get_specs`, …) so `list-python-apis` ↔ `mcp list-tools` are 1:1 (audit
§6 parity). Each tool delegates to the Python API directly — no logic
duplication. `log_processor_usages` blocks for the requested duration;
callers wanting background mode should call the Python API directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from fastmcp import FastMCP
except ImportError as e:  # pragma: no cover — fastmcp is optional
    raise ImportError(
        "fastmcp is required for scitex-resource MCP support.\n"
        "Install with: pip install scitex-resource[mcp]"
    ) from e

from .._machine import get_machine_config, get_machine_name
from .._runtime import default_log_path
from .._specs import get_metrics, get_processor_usages, get_specs

mcp = FastMCP("scitex-resource")


# ----------------------------------------------------------- skills helpers


def _skills_root() -> Path:
    import scitex_resource

    return Path(scitex_resource.__file__).parent / "_skills" / "scitex-resource"


def _list_skill_files() -> list[Path]:
    root = _skills_root()
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file() and p.name != "SKILL.md")


@mcp.tool()
def skills_list() -> list[dict]:
    """List skill files bundled with scitex-resource."""
    return [{"name": p.stem, "path": str(p)} for p in _list_skill_files()]


@mcp.tool()
def skills_get(name: str) -> dict:
    """Return the contents of a bundled skill file by NAME."""
    target = name[:-3] if name.endswith(".md") else name
    match = next((p for p in _list_skill_files() if p.stem == target), None)
    if match is None:
        return {"error": f"skill not found: {name}"}
    return {
        "name": match.stem,
        "path": str(match),
        "content": match.read_text(encoding="utf-8"),
    }


# ----------------------------------------------------- Python-API mirrors


@mcp.tool(name="get_machine_name")
def _tool_get_machine_name() -> str:
    """Canonical machine name — env > config > short hostname."""
    return get_machine_name()


@mcp.tool(name="get_machine_config")
def _tool_get_machine_config() -> dict[str, Any]:
    """`machine:` block from config.yaml (empty dict if no config)."""
    return get_machine_config()


@mcp.tool(name="get_specs")
def _tool_get_specs(
    system: bool = True,
    cpu: bool = True,
    gpu: bool = True,
    disk: bool = True,
    network: bool = True,
) -> dict[str, Any]:
    """Rich human-formatted system specs (dict shape, not YAML)."""
    return get_specs(
        system=system,
        cpu=cpu,
        gpu=gpu,
        disk=disk,
        network=network,
        verbose=False,
        yaml=False,
    )


@mcp.tool(name="get_metrics")
def _tool_get_metrics(gpu: bool = True) -> dict[str, Any]:
    """Flat heartbeat-shape metrics. `gpu=False` skips nvidia-smi."""
    return get_metrics(gpu=gpu)


@mcp.tool(name="get_processor_usages")
def _tool_get_processor_usages() -> list[dict]:
    """One snapshot of CPU/RAM/GPU/VRAM — list-of-records shape."""
    return get_processor_usages().to_dict(orient="records")


@mcp.tool(name="log_processor_usages")
def _tool_log_processor_usages(
    path: str | None = None,
    interval_s: float = 1.0,
    max_rows: int = 60,
    init: bool = True,
) -> dict[str, Any]:
    """Append CPU/RAM/GPU/VRAM rows to a CSV. Blocks until done."""
    if path is None:
        path = default_log_path()
    from .._log_processor_usages import log_processor_usages

    limit_min = (max_rows * interval_s) / 60.0
    log_processor_usages(
        path=path,
        limit_min=limit_min,
        interval_s=interval_s,
        init=init,
        verbose=False,
        background=False,
    )
    return {"path": path, "rows": max_rows, "interval_s": interval_s}


@mcp.tool(name="limit_ram")
def _tool_limit_ram(factor: float) -> dict[str, Any]:
    """Cap current-process RLIMIT_AS at FACTOR×free RAM (0 < factor ≤ 1).

    Does NOT bound child processes on Linux.
    """
    from .. import limit_ram as _lr

    if not (0 < factor <= 1):
        return {"ok": False, "error": "factor must satisfy 0 < factor <= 1"}
    _lr.limit_ram(factor)
    return {"ok": True, "factor": factor}


@mcp.tool(name="get_ram")
def _tool_get_ram() -> dict[str, Any]:
    """MemFree+Buffers+Cached from /proc/meminfo, in KiB."""
    from .. import limit_ram as _lr

    return {"free_kib": _lr.get_ram()}


def main() -> int:
    """Console-script entry point — runs the MCP server over stdio."""
    mcp.run()
    return 0
