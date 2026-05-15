"""Shared human-readable formatter for ``... show`` leaves.

Goals (per scitex-resource 0.4.1 CLI overhaul):

* Aligned key/value columns, two-space indent.
* Integers >= 1000 get thousand-separator commas.
* ``*_mb`` / ``*_kib`` fields auto-scale to GB/TB (one decimal); column
  label loses the unit suffix.
* Group rendering: load-avg keys (1m/5m/15m) collapse to
  ``1.91 / 1.69 / 2.59  # 1m / 5m / 15m``.
* Empty lists render as ``(none)``.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


def _scale_mb(value: float) -> str:
    """Scale a megabyte value to GB or TB with one decimal."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} TB"
    if n >= 1024:
        return f"{n / 1024:.1f} GB"
    return f"{n:.0f} MB"


def _scale_kib(value: float) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)
    if n >= 1024 * 1024 * 1024:
        return f"{n / (1024 * 1024 * 1024):.1f} TB"
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} GB"
    if n >= 1024:
        return f"{n / 1024:.1f} MB"
    return f"{n:.0f} KiB"


def _format_scalar(key: str, value: Any) -> tuple[str, str]:
    """Return (display_key, formatted_value) for a scalar field.

    Strips ``_mb``/``_kib`` from key when value is auto-scaled.
    """
    if isinstance(value, bool):
        return key, "true" if value else "false"
    if value is None:
        return key, "(none)"
    if isinstance(value, int) and not isinstance(value, bool):
        if key.endswith("_mb"):
            return key[:-3], _scale_mb(value)
        if key.endswith("_kib"):
            return key[:-4], _scale_kib(value)
        return key, f"{value:,}" if abs(value) >= 1000 else str(value)
    if isinstance(value, float):
        if key.endswith("_mb"):
            return key[:-3], _scale_mb(value)
        if key.endswith("_kib"):
            return key[:-4], _scale_kib(value)
        return key, f"{value}"
    return key, str(value)


def _is_load_avg_block(d: Mapping[str, Any]) -> bool:
    return all(f"load_avg_{w}" in d for w in ("1m", "5m", "15m"))


def _render_dict(d: Mapping[str, Any], indent: int, out: list[str]) -> None:
    pad = "  " * indent
    # Collapse load-avg group if present.
    keys = list(d.keys())
    if _is_load_avg_block(d):
        v1, v5, v15 = d["load_avg_1m"], d["load_avg_5m"], d["load_avg_15m"]
        out.append(f"{pad}load_avg: {v1} / {v5} / {v15}  # 1m / 5m / 15m")
        keys = [
            k for k in keys if k not in ("load_avg_1m", "load_avg_5m", "load_avg_15m")
        ]
    # Compute label width for alignment among scalar keys.
    scalar_labels: list[
        tuple[str, str, str]
    ] = []  # (orig_key, display_key, formatted_val)
    nested: list[tuple[str, Any]] = []
    for k in keys:
        v = d[k]
        if isinstance(v, dict):
            nested.append((k, v))
        elif isinstance(v, list):
            nested.append((k, v))
        else:
            disp_k, disp_v = _format_scalar(k, v)
            scalar_labels.append((k, disp_k, disp_v))
    width = max((len(dk) for _, dk, _ in scalar_labels), default=0)
    for _, dk, dv in scalar_labels:
        out.append(f"{pad}{dk.ljust(width)}  {dv}")
    for k, v in nested:
        if isinstance(v, dict):
            out.append(f"{pad}{k}:")
            _render_dict(v, indent + 1, out)
        else:
            _render_list(k, v, indent, out)


def _render_list(key: str, items: Iterable[Any], indent: int, out: list[str]) -> None:
    pad = "  " * indent
    seq = list(items)
    if not seq:
        out.append(f"{pad}{key}: (none)")
        return
    out.append(f"{pad}{key}:")
    inner = "  " * (indent + 1)
    for item in seq:
        if isinstance(item, dict):
            out.append(f"{inner}-")
            _render_dict(item, indent + 2, out)
        else:
            out.append(f"{inner}- {item}")


def format_human(obj: Any) -> str:
    """Render ``obj`` (dict/list/scalar) as the human leaf shape."""
    out: list[str] = []
    if isinstance(obj, dict):
        _render_dict(obj, 1, out)
    elif isinstance(obj, list):
        _render_list("items", obj, 0, out)
    else:
        out.append(f"  {obj}")
    return "\n".join(out)
