"""Real-I/O tests for ``scitex_resource._specs._specs.get_specs``.

No mocks — runs psutil/nvidia-smi against the real machine and asserts
structural invariants rather than exact values.
"""

from __future__ import annotations

from scitex_resource import get_specs


def test_get_specs_returns_dict_when_all_sections_disabled():
    # Arrange
    # Act
    result = get_specs(
        system=False, cpu=False, gpu=False, disk=False, network=False, verbose=False
    )
    # Assert
    assert isinstance(result, dict)


def test_get_specs_cpu_section_includes_count():
    # Arrange
    # Act
    result = get_specs(
        system=False, cpu=True, gpu=False, disk=False, network=False, verbose=False
    )
    # Assert
    assert "CPU Info" in result


def test_get_specs_disk_section_present_when_requested():
    # Arrange
    # Act
    result = get_specs(
        system=False, cpu=False, gpu=False, disk=True, network=False, verbose=False
    )
    # Assert
    assert "Disk Info" in result


def test_get_specs_network_section_present_when_requested():
    # Arrange
    # Act
    result = get_specs(
        system=False, cpu=False, gpu=False, disk=False, network=True, verbose=False
    )
    # Assert
    assert "Network Info" in result


def test_get_specs_system_section_present_when_requested():
    # Arrange
    # Act
    result = get_specs(
        system=True, cpu=False, gpu=False, disk=False, network=False, verbose=False
    )
    # Assert
    assert "System Information" in result


def test_get_specs_yaml_returns_string():
    # Arrange
    # Act
    result = get_specs(
        system=True,
        cpu=False,
        gpu=False,
        disk=False,
        network=False,
        verbose=False,
        yaml=True,
    )
    # Assert
    assert isinstance(result, str)
