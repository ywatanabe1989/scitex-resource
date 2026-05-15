"""Real-I/O tests for ``scitex_resource.limit_ram``.

``get_ram`` reads /proc/meminfo directly. ``limit_ram`` is exercised under
a forked child (so RLIMIT_AS does not bleed into the test runner).
"""

from __future__ import annotations

import os

import pytest

from scitex_resource.limit_ram import get_RAM, get_ram, limit_RAM, limit_ram

requires_fork = pytest.mark.skipif(
    not hasattr(os, "fork"), reason="os.fork not available on this platform"
)


def _fork_capture(factor: float, encode):
    """Fork a child, apply ``limit_ram(factor)``, return ``encode(...)`` bytes."""
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        import resource

        try:
            limit_ram(factor)
            soft, _ = resource.getrlimit(resource.RLIMIT_AS)
            free_bytes = get_ram() * 1_024
            os.write(write_fd, encode(soft, free_bytes))
        finally:
            os.close(write_fd)
            os._exit(0)
    os.close(write_fd)
    raw = os.read(read_fd, 64)
    os.close(read_fd)
    os.waitpid(pid, 0)
    return raw


def test_get_ram_returns_integer():
    # Arrange
    # Act
    result = get_ram()
    # Assert
    assert isinstance(result, int)


def test_get_ram_returns_positive_kib():
    # Arrange
    # Act
    result = get_ram()
    # Assert
    assert result > 0


def test_get_ram_deprecated_alias_points_to_canonical():
    # Arrange
    # Act
    aliased = get_RAM
    # Assert
    assert aliased is get_ram


def test_limit_ram_deprecated_alias_points_to_canonical():
    # Arrange
    # Act
    aliased = limit_RAM
    # Assert
    assert aliased is limit_ram


@requires_fork
def test_limit_ram_sets_positive_soft_rlimit_in_child():
    # Arrange
    factor = 0.5
    # Act
    raw = _fork_capture(factor, lambda soft, _f: str(soft).encode())
    # Assert
    assert int(raw) > 0


@requires_fork
def test_limit_ram_soft_rlimit_not_exceeding_free_ram_in_child():
    # Arrange
    factor = 0.25
    # Act
    raw = _fork_capture(
        factor,
        lambda soft,
        free_bytes: f"{(soft / free_bytes) if free_bytes else 0:.4f}".encode(),
    )
    # Assert
    assert float(raw) <= 1.0
