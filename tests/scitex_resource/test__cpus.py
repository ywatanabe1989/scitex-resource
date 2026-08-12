"""Unit tests for usable-CPU detection.

No patching: the decision is a pure function over explicit inputs, the
readers take their collaborators as parameters, and the ``/proc`` reader
takes a path so these tests hand it a real file holding real bytes.

Two properties matter more than any individual case:

* **The parser fails CLOSED.** A parser that returns a plausible number
  from malformed input is how a wrong CPU count becomes invisible again, so
  the rejection cases are tested as deliberately as the acceptance ones.
* **``OMP_NUM_THREADS`` never influences the answer.** That variable is a
  thread budget, not a CPU count; reading it as one is the exact bug this
  module exists to prevent — coreutils ``nproc`` returned 1 inside a 48-CPU
  SLURM allocation because of it.
"""

from __future__ import annotations

import os

import pytest

from scitex_resource._cpus import (
    affinity_from_proc_status,
    affinity_from_syscall,
    get_cpu_sources,
    get_usable_cpus,
    parse_cpu_list,
    read_affinity,
    resolve_cpu_sources,
)


def _mask(size):
    """A stand-in for ``os.sched_getaffinity`` reporting ``size`` CPUs."""
    return lambda _pid: set(range(size))


def _blocked_syscall(_pid):
    """A ``sched_getaffinity`` whose syscall is denied by the sandbox."""
    raise OSError("sched_getaffinity blocked")


def _write_proc_status(directory, cpus_allowed_line):
    """Write a real /proc-shaped status file and return its path."""
    path = directory / "status"
    path.write_text(
        "Name:\tpython3\n"
        "State:\tR (running)\n"
        f"{cpus_allowed_line}"
        "Mems_allowed_list:\t0-1\n"
    )
    return str(path)


# ---------------------------------------------------------------------------
# parse_cpu_list — acceptance


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("0-127", 128),
        ("0-47", 48),
        ("0", 1),
        ("1,2,6,10", 4),
        ("1,2,6,10,13-14,17", 7),
        ("  0-3  ", 4),
        ("5-5", 1),
    ],
)
def test_parse_cpu_list_accepts_valid_forms(spec, expected):
    # Arrange
    candidate = spec
    # Act
    result = parse_cpu_list(candidate)
    # Assert
    assert result == expected


# ---------------------------------------------------------------------------
# parse_cpu_list — rejection (fail closed, never a plausible half-parse)


@pytest.mark.parametrize(
    "spec",
    [
        None,
        "",
        "   ",
        "garbage",
        "0-",
        "-5",
        "1,,2",
        "3-1",
        "0-x",
        "1-2-3",
        "1.5",
        "+3",
        "0,",
        "1 2",
    ],
)
def test_parse_cpu_list_rejects_malformed_input(spec):
    # Arrange
    candidate = spec
    # Act
    result = parse_cpu_list(candidate)
    # Assert
    assert result is None


# ---------------------------------------------------------------------------
# Source ordering: affinity -> SLURM -> machine total


def test_affinity_wins_over_slurm_and_machine():
    # Arrange
    env = {"SLURM_CPUS_PER_TASK": "8"}
    # Act
    result = resolve_cpu_sources(affinity=48, environ=env, cpu_count=128)
    # Assert
    assert (result["usable"], result["source"]) == (48, "affinity")


def test_slurm_cpus_per_task_used_when_affinity_unavailable():
    # Arrange
    env = {"SLURM_CPUS_PER_TASK": "48"}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=128)
    # Assert
    assert (result["usable"], result["source"]) == (48, "slurm_cpus_per_task")


def test_slurm_cpus_on_node_used_when_per_task_absent():
    # Arrange
    env = {"SLURM_CPUS_ON_NODE": "36"}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=128)
    # Assert
    assert (result["usable"], result["source"]) == (36, "slurm_cpus_on_node")


def test_per_task_outranks_on_node_when_both_present():
    # Arrange
    env = {"SLURM_CPUS_PER_TASK": "12", "SLURM_CPUS_ON_NODE": "36"}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=128)
    # Assert
    assert (result["usable"], result["source"]) == (12, "slurm_cpus_per_task")


def test_machine_total_used_when_affinity_and_slurm_absent():
    # Arrange
    env = {}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=12)
    # Assert
    assert (result["usable"], result["source"]) == (12, "cpu_count")


def test_falls_back_to_one_when_every_source_is_silent():
    # Arrange
    env = {}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=None)
    # Assert
    assert (result["usable"], result["source"]) == (1, "default")


# ---------------------------------------------------------------------------
# Malformed values fail closed rather than poisoning the answer


@pytest.mark.parametrize("bad", ["", "   ", "many", "48(x2)", "-4", "0", "4.5", "1e2"])
def test_malformed_slurm_cpus_per_task_is_ignored(bad):
    # Arrange
    env = {"SLURM_CPUS_PER_TASK": bad}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=7)
    # Assert
    assert (result["usable"], result["source"]) == (7, "cpu_count")


def test_nonsense_affinity_of_zero_is_ignored():
    # Arrange
    env = {}
    # Act
    result = resolve_cpu_sources(affinity=0, environ=env, cpu_count=7)
    # Assert
    assert (result["usable"], result["source"]) == (7, "cpu_count")


# ---------------------------------------------------------------------------
# OMP_NUM_THREADS is a thread budget, NEVER a CPU count. This is the bug.


def test_omp_num_threads_does_not_change_the_answer():
    # Arrange
    env = {"OMP_NUM_THREADS": "1", "SLURM_CPUS_PER_TASK": "48"}
    # Act
    result = resolve_cpu_sources(affinity=48, environ=env, cpu_count=128)
    # Assert
    assert result["usable"] == 48


def test_omp_num_threads_is_reported_for_diagnosis():
    # Arrange
    env = {"OMP_NUM_THREADS": "1"}
    # Act
    result = resolve_cpu_sources(affinity=48, environ=env, cpu_count=128)
    # Assert
    assert result["omp_num_threads"] == 1


def test_omp_num_threads_cannot_win_even_as_the_only_input():
    # Arrange
    env = {"OMP_NUM_THREADS": "1"}
    # Act
    result = resolve_cpu_sources(affinity=None, environ=env, cpu_count=None)
    # Assert
    assert result["source"] == "default"


# ---------------------------------------------------------------------------
# Every source is reported, not just the winner


def test_sources_report_the_losers_too():
    # Arrange -- the Spartan shape: 48 usable on a 128-CPU node
    env = {"SLURM_CPUS_PER_TASK": "48"}
    # Act
    result = resolve_cpu_sources(affinity=48, environ=env, cpu_count=128)
    # Assert
    assert (result["affinity"], result["cpu_count"], result["slurm_cpus_per_task"]) == (
        48,
        128,
        48,
    )


def test_affinity_source_is_cleared_when_affinity_is_unusable():
    # Arrange
    env = {}
    # Act
    result = resolve_cpu_sources(
        affinity=None, affinity_source="sched_getaffinity", environ=env, cpu_count=8
    )
    # Assert
    assert result["affinity_source"] is None


# ---------------------------------------------------------------------------
# Readers


def test_syscall_reader_counts_the_mask_it_is_given():
    # Arrange
    getaffinity = _mask(48)
    # Act
    result = affinity_from_syscall(getaffinity)
    # Assert
    assert result == 48


def test_syscall_reader_returns_none_when_the_syscall_is_blocked():
    # Arrange
    getaffinity = _blocked_syscall
    # Act
    result = affinity_from_syscall(getaffinity)
    # Assert
    assert result is None


def test_proc_status_reader_parses_a_real_file(tmp_path):
    # Arrange
    path = _write_proc_status(tmp_path, "Cpus_allowed_list:\t0-47\n")
    # Act
    result = affinity_from_proc_status(path)
    # Assert
    assert result == 48


def test_proc_status_reader_rejects_a_garbage_line(tmp_path):
    # Arrange
    path = _write_proc_status(tmp_path, "Cpus_allowed_list:\tnonsense\n")
    # Act
    result = affinity_from_proc_status(path)
    # Assert
    assert result is None


def test_proc_status_reader_returns_none_when_the_key_is_absent(tmp_path):
    # Arrange
    path = _write_proc_status(tmp_path, "")
    # Act
    result = affinity_from_proc_status(path)
    # Assert
    assert result is None


def test_proc_status_reader_returns_none_when_the_file_is_missing(tmp_path):
    # Arrange
    path = str(tmp_path / "definitely-absent")
    # Act
    result = affinity_from_proc_status(path)
    # Assert
    assert result is None


def test_read_affinity_prefers_the_syscall_over_proc(tmp_path):
    # Arrange
    path = _write_proc_status(tmp_path, "Cpus_allowed_list:\t0-3\n")
    # Act
    result = read_affinity(_mask(48), path)
    # Assert
    assert result == (48, "sched_getaffinity")


def test_read_affinity_backstops_a_blocked_syscall_with_proc(tmp_path):
    # Arrange
    path = _write_proc_status(tmp_path, "Cpus_allowed_list:\t0-47\n")
    # Act
    result = read_affinity(_blocked_syscall, path)
    # Assert
    assert result == (48, "proc_status")


def test_read_affinity_gives_up_when_neither_mechanism_answers(tmp_path):
    # Arrange
    path = str(tmp_path / "definitely-absent")
    # Act
    result = read_affinity(_blocked_syscall, path)
    # Assert
    assert result == (None, None)


# ---------------------------------------------------------------------------
# get_cpu_sources / get_usable_cpus wiring


def test_get_cpu_sources_threads_injected_collaborators_through(tmp_path):
    # Arrange
    path = str(tmp_path / "definitely-absent")
    # Act
    result = get_cpu_sources(
        environ={"SLURM_CPUS_PER_TASK": "8"},
        getaffinity=_mask(48),
        cpu_counter=lambda: 128,
        proc_status_path=path,
    )
    # Assert
    assert (result["usable"], result["affinity"], result["cpu_count"]) == (48, 48, 128)


def test_usable_cpus_matches_the_chosen_source():
    # Arrange
    getaffinity = _mask(6)
    # Act
    result = get_usable_cpus(getaffinity=getaffinity, environ={}, cpu_counter=lambda: 6)
    # Assert
    assert result == 6


def test_minimum_raises_a_small_count_to_the_floor():
    # Arrange
    getaffinity = _mask(1)
    # Act
    result = get_usable_cpus(
        minimum=4, getaffinity=getaffinity, environ={}, cpu_counter=lambda: 1
    )
    # Assert
    assert result == 4


def test_minimum_never_caps_a_large_count():
    # Arrange
    getaffinity = _mask(48)
    # Act
    result = get_usable_cpus(
        minimum=4, getaffinity=getaffinity, environ={}, cpu_counter=lambda: 128
    )
    # Assert
    assert result == 48


def test_result_is_never_below_one_even_with_a_nonsense_minimum(tmp_path):
    # Arrange
    path = str(tmp_path / "definitely-absent")
    # Act
    result = get_usable_cpus(
        minimum=0,
        getaffinity=_blocked_syscall,
        environ={},
        cpu_counter=lambda: None,
        proc_status_path=path,
    )
    # Assert
    assert result == 1


# ---------------------------------------------------------------------------
# The no-op property, measured against this real host: wherever the affinity
# mask is readable, the answer must equal it. This is what licenses replacing
# an existing `nproc` call -- identical behaviour where nproc is already right.


@pytest.mark.skipif(
    not hasattr(os, "sched_getaffinity"), reason="Linux-only affinity syscall"
)
def test_unconstrained_result_equals_this_hosts_real_affinity_mask():
    # Arrange
    expected = len(os.sched_getaffinity(0))
    # Act
    result = get_usable_cpus()
    # Assert
    assert result == expected


@pytest.mark.skipif(
    not os.path.exists("/proc/self/status"), reason="requires a mounted /proc"
)
def test_the_two_affinity_mechanisms_agree_on_this_host():
    # Arrange
    from_syscall = affinity_from_syscall()
    # Act
    from_proc = affinity_from_proc_status()
    # Assert
    assert from_proc == from_syscall
