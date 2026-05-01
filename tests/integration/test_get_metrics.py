"""Schema and shape tests for ``scitex_resource.get_metrics``.

The output is a public contract — heartbeat producers and dashboards depend
on the exact key names and types. Bumping the minor version is the signal
to consumers that something here changed.
"""

from __future__ import annotations

import pytest

from scitex_resource import get_metrics

REQUIRED_INT_KEYS = (
    "cpu_count",
    "mem_total_mb",
    "mem_used_mb",
    "mem_free_mb",
    "disk_total_mb",
    "disk_used_mb",
)

REQUIRED_FLOAT_KEYS = (
    "load_avg_1m",
    "load_avg_5m",
    "load_avg_15m",
    "mem_used_percent",
    "disk_used_percent",
)


def test_returns_flat_dict():
    m = get_metrics(gpu=False)
    assert isinstance(m, dict)
    for k, v in m.items():
        assert not isinstance(v, dict), f"{k} is nested; output must stay flat"


def test_required_int_keys_present_and_typed():
    m = get_metrics(gpu=False)
    for k in REQUIRED_INT_KEYS:
        assert k in m, f"missing required key: {k}"
        assert isinstance(m[k], int), f"{k} should be int, got {type(m[k]).__name__}"
        assert m[k] >= 0, f"{k} must be non-negative"


def test_required_float_keys_present_and_typed():
    m = get_metrics(gpu=False)
    for k in REQUIRED_FLOAT_KEYS:
        assert k in m, f"missing required key: {k}"
        assert isinstance(m[k], (int, float)), f"{k} should be numeric"


def test_cpu_model_is_string():
    m = get_metrics(gpu=False)
    assert isinstance(m["cpu_model"], str)


def test_gpus_is_list():
    m = get_metrics(gpu=False)
    assert isinstance(m["gpus"], list)
    assert m["gpus"] == [], "gpu=False must skip GPU probing"


def test_mem_used_plus_free_within_total():
    m = get_metrics(gpu=False)
    assert m["mem_used_mb"] + m["mem_free_mb"] <= m["mem_total_mb"] + 1


def test_percent_in_valid_range():
    m = get_metrics(gpu=False)
    for k in ("mem_used_percent", "disk_used_percent"):
        assert 0.0 <= m[k] <= 100.0, f"{k} out of [0, 100]: {m[k]}"


@pytest.mark.parametrize("call", [lambda: get_metrics(), lambda: get_metrics(gpu=True)])
def test_gpu_probe_returns_list(call):
    m = call()
    assert isinstance(m["gpus"], list)
    for gpu in m["gpus"]:
        assert {"name", "vram_total_mb", "vram_used_mb"} <= gpu.keys()
