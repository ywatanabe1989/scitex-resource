"""Schema tests for ``scitex_resource.get_metrics``.

Heartbeat consumers depend on the exact key names and value types.
"""

from __future__ import annotations

import pytest

from scitex_resource import get_metrics


def test_get_metrics_returns_dict():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert isinstance(m, dict)


def test_get_metrics_output_has_no_nested_dicts():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert all(not isinstance(v, dict) for v in m.values())


@pytest.mark.parametrize(
    "key",
    [
        "cpu_count",
        "mem_total_mb",
        "mem_used_mb",
        "mem_free_mb",
        "disk_total_mb",
        "disk_used_mb",
    ],
)
def test_required_int_key_is_present(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert key in m


@pytest.mark.parametrize(
    "key",
    [
        "cpu_count",
        "mem_total_mb",
        "mem_used_mb",
        "mem_free_mb",
        "disk_total_mb",
        "disk_used_mb",
    ],
)
def test_required_int_key_is_int(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert isinstance(m[key], int)


@pytest.mark.parametrize(
    "key",
    [
        "cpu_count",
        "mem_total_mb",
        "mem_used_mb",
        "mem_free_mb",
        "disk_total_mb",
        "disk_used_mb",
    ],
)
def test_required_int_key_is_non_negative(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert m[key] >= 0


@pytest.mark.parametrize(
    "key",
    [
        "load_avg_1m",
        "load_avg_5m",
        "load_avg_15m",
        "mem_used_percent",
        "disk_used_percent",
    ],
)
def test_required_float_key_is_present(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert key in m


@pytest.mark.parametrize(
    "key",
    [
        "load_avg_1m",
        "load_avg_5m",
        "load_avg_15m",
        "mem_used_percent",
        "disk_used_percent",
    ],
)
def test_required_float_key_is_numeric(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert isinstance(m[key], (int, float))


def test_cpu_model_value_is_string():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert isinstance(m["cpu_model"], str)


def test_gpus_value_is_list():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert isinstance(m["gpus"], list)


def test_gpu_false_yields_empty_gpus_list():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert m["gpus"] == []


def test_mem_used_plus_free_within_total():
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert m["mem_used_mb"] + m["mem_free_mb"] <= m["mem_total_mb"] + 1


@pytest.mark.parametrize("key", ["mem_used_percent", "disk_used_percent"])
def test_percent_key_in_valid_range(key):
    # Arrange
    # Act
    m = get_metrics(gpu=False)
    # Assert
    assert 0.0 <= m[key] <= 100.0


def test_default_call_returns_gpus_as_list():
    # Arrange
    # Act
    m = get_metrics()
    # Assert
    assert isinstance(m["gpus"], list)


def test_gpu_true_call_returns_gpus_as_list():
    # Arrange
    # Act
    m = get_metrics(gpu=True)
    # Assert
    assert isinstance(m["gpus"], list)
