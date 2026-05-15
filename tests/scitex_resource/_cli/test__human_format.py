"""Unit tests for the shared human-readable formatter."""

from __future__ import annotations

from scitex_resource._cli._human_format import format_human


def test_thousand_separator_added_to_large_int():
    # Arrange
    payload = {"items_seen": 12_345}
    # Act
    out = format_human(payload)
    # Assert
    assert "12,345" in out


def test_small_int_left_uncommaed():
    # Arrange
    payload = {"items_seen": 42}
    # Act
    out = format_human(payload)
    # Assert
    assert "items_seen  42" in out


def test_mb_suffix_label_stripped():
    # Arrange
    payload = {"mem_total_mb": 23_000}
    # Act
    out = format_human(payload)
    # Assert
    assert "mem_total_mb" not in out


def test_mb_suffix_displays_base_label():
    # Arrange
    payload = {"mem_total_mb": 23_000}
    # Act
    out = format_human(payload)
    # Assert
    assert "mem_total " in out


def test_mb_suffix_value_rendered_as_gb():
    # Arrange
    payload = {"mem_total_mb": 23_000}
    # Act
    out = format_human(payload)
    # Assert
    assert "GB" in out


def test_kib_suffix_scales_to_gb():
    # Arrange
    payload = {"buf_kib": 5_242_880}  # 5 MiB in KiB scales to GB threshold
    # Act
    out = format_human(payload)
    # Assert
    assert "GB" in out


def test_load_avg_group_collapses():
    # Arrange
    payload = {"load_avg_1m": 1.91, "load_avg_5m": 1.69, "load_avg_15m": 2.59}
    # Act
    out = format_human(payload)
    # Assert
    assert "1.91 / 1.69 / 2.59" in out


def test_load_avg_comment_present():
    # Arrange
    payload = {"load_avg_1m": 1.0, "load_avg_5m": 1.0, "load_avg_15m": 1.0}
    # Act
    out = format_human(payload)
    # Assert
    assert "# 1m / 5m / 15m" in out


def test_empty_list_renders_as_none():
    # Arrange
    payload = {"gpus": []}
    # Act
    out = format_human(payload)
    # Assert
    assert "(none)" in out


def test_two_space_indent_applied_to_top_level():
    # Arrange
    payload = {"k": "v"}
    # Act
    out = format_human(payload)
    # Assert
    assert out.startswith("  ")


def test_aligned_columns_share_label_width():
    # Arrange
    payload = {"short": 1, "much_longer_key": 2}
    # Act
    out = format_human(payload)
    lines = out.splitlines()
    # Assert — value column for both lines starts at the same column.
    val_col_short = lines[0].index("1")
    val_col_long = lines[1].index("2")
    assert val_col_short == val_col_long
