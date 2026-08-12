"""Usable CPUs — how many processors this process may ACTUALLY run on.

``get_metrics()["cpu_count"]`` and ``get_specs()["CPU Info"]`` answer a
different question: *how big is this machine?* They report
``psutil.cpu_count()``, the kernel's total. That is the right number for a
hardware inventory and the WRONG number for "how many workers should I
start?", because a process is routinely confined to a subset of the box —
by an HPC scheduler, a cgroup, a container, or a plain ``taskset``.

This module answers the sizing question. Every caller picking a worker
count, a thread-pool size, or an ``xdist -n`` should use
:func:`get_usable_cpus`, not the machine total.

Resolution cascade (highest precedence first)
---------------------------------------------

1. **The kernel's affinity mask** — ``os.sched_getaffinity(0)``, falling
   back to parsing ``Cpus_allowed_list`` in ``/proc/self/status`` where the
   syscall is unavailable. This is *literally* "the CPUs the kernel will
   schedule THIS process on": it already accounts for cpusets, containers,
   ``taskset`` and SLURM's own pinning, and **no environment variable can
   override it**. It is first because it is the only source that is a fact
   rather than a hint.

2. **SLURM's environment** — ``SLURM_CPUS_PER_TASK``, then
   ``SLURM_CPUS_ON_NODE``. What the scheduler says it allocated. The right
   second source: where the affinity mask is unreadable, this is still the
   allocation the job is being billed for.

   ``SLURM_JOB_CPUS_PER_NODE`` is deliberately NOT consulted — it uses a
   compressed form (``"48(x2)"``, ``"36,48"``) whose partial parses are
   plausible-looking wrong numbers, which is exactly the failure this
   module exists to prevent.

3. **The machine total** — ``os.cpu_count()``. Last, so the module still
   returns something sensible off any scheduler.

WHY NOT ``nproc``
-----------------

Coreutils ``nproc`` honours ``OMP_NUM_THREADS`` / ``OMP_THREAD_LIMIT``
**ahead of** the affinity mask. Measured on the ``spartan-bm153`` CI runner
inside a 48-CPU SLURM allocation (job 29015324)::

    OMP_NUM_THREADS        1
    nproc (as-is)          1
    nproc (OMP_* cleared)  48
    nproc --all          128
    sched_getaffinity     48
    SLURM_CPUS_PER_TASK   48

A CI script read ``nproc``, got 1, and ran its test suite on a floor of 4
xdist workers inside an allocation holding 48 CPUs — 12x the cores idle,
for weeks, invisibly. Clearing the variable moves ``nproc`` from 1 to 48,
which establishes the cause rather than merely fitting it.

``os.cpu_count()`` is the Python equivalent of ``nproc --all``, not of
``nproc``: it reports the machine and is immune to the OpenMP variables.
That is why step 3 uses it.

**DO NOT "FIX" THE ABOVE BY UNSETTING ``OMP_NUM_THREADS``.** It is set to 1
on purpose and it is CORRECT: each worker is a separate process, and
BLAS/OpenMP inside numpy will happily start one thread per core in EVERY
one of them. 48 workers x 48 OMP threads is 2304 threads on 48 CPUs.
``OMP_NUM_THREADS=1`` with 48 PROCESSES is exactly the right shape — one
thread per core, no oversubscription. The bug was never the variable; it
was reading a THREAD-BUDGET knob as a CPU-COUNT fact. This module therefore
*reports* ``omp_num_threads`` and never lets it influence the answer.

Reporting every source
----------------------

:func:`get_cpu_sources` returns what each source said, not just the winner.
When these disagree on some host nobody has met yet, the disagreement is
the finding, and it belongs in the log rather than costing someone a probe
run::

    xdist workers=48 (affinity=48 cpu_count=128 SLURM_CPUS_PER_TASK=48)

Testability
-----------

The decision is a PURE function — :func:`resolve_cpu_sources` takes every
input explicitly and touches nothing. The I/O lives in thin readers whose
collaborators (``environ``, the affinity reader, the CPU counter, the
``/proc`` path) are all injectable, so the tests substitute reality rather
than patching this module's internals.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Mapping

__all__ = [
    "get_cpu_sources",
    "get_usable_cpus",
    "parse_cpu_list",
    "read_affinity",
    "resolve_cpu_sources",
]

PROC_STATUS_PATH = "/proc/self/status"
_CPUS_ALLOWED_KEY = "Cpus_allowed_list:"

#: Consulted in order. Both hold a plain integer; see the module docstring
#: for why the compressed ``SLURM_JOB_CPUS_PER_NODE`` is excluded.
SLURM_CPU_VARS = ("SLURM_CPUS_PER_TASK", "SLURM_CPUS_ON_NODE")


# ---------------------------------------------------------------------------
# Parsing — every malformed form fails CLOSED


def _strict_nonnegative_int(value: str) -> int | None:
    """Parse a bare non-negative decimal integer. ``None`` on anything else.

    ``str.isdigit`` rejects signs, floats, whitespace-in-the-middle and
    unicode junk, which is what makes this strict rather than forgiving.
    """
    text = value.strip()
    if not text or not text.isdigit():
        return None
    return int(text)


def _strict_positive_int(value: str | None) -> int | None:
    """Parse a bare POSITIVE decimal integer. ``None`` on anything else.

    Zero is rejected as well as garbage: a source claiming zero usable CPUs
    is not usable information, so the caller should fall through to the next
    source rather than believe it.
    """
    if value is None:
        return None
    parsed = _strict_nonnegative_int(value)
    if parsed is None or parsed <= 0:
        return None
    return parsed


def parse_cpu_list(spec: str | None) -> int | None:
    """Count the CPUs in a Linux CPU-list string. ``None`` if unparseable.

    Accepts the kernel's ``Cpus_allowed_list`` / cpuset syntax: comma-
    separated singletons and inclusive ``lo-hi`` ranges.

    >>> parse_cpu_list("0-127")
    128
    >>> parse_cpu_list("1,2,6,10,13-14,17")
    7

    Every malformed form fails CLOSED (``None``) so the caller falls through
    to the next source instead of trusting a half-parse — a parser that
    returns a plausible number from malformed input is how a wrong CPU count
    becomes invisible again:

    >>> [parse_cpu_list(bad) for bad in ("", "garbage", "0-", "3-1", "1,,2")]
    [None, None, None, None, None]
    """
    if spec is None:
        return None
    text = spec.strip()
    if not text:
        return None
    total = 0
    for part in text.split(","):
        token = part.strip()
        if not token:
            return None
        if "-" in token:
            bounds = token.split("-")
            if len(bounds) != 2:
                return None
            low = _strict_nonnegative_int(bounds[0])
            high = _strict_nonnegative_int(bounds[1])
            if low is None or high is None or high < low:
                return None
            total += high - low + 1
        else:
            if _strict_nonnegative_int(token) is None:
                return None
            total += 1
    return total or None


# ---------------------------------------------------------------------------
# Readers — the only parts that touch the OS


def affinity_from_syscall(
    getaffinity: Callable[[int], set[int]] | None = None,
) -> int | None:
    """CPU count from ``sched_getaffinity`` (Linux; absent on macOS/Windows).

    Parameters
    ----------
    getaffinity : callable, optional
        The syscall wrapper to use. Defaults to ``os.sched_getaffinity``;
        pass ``None`` explicitly-unavailable platforms simulate by supplying
        a callable that raises ``OSError``.
    """
    if getaffinity is None:
        getaffinity = getattr(os, "sched_getaffinity", None)
    if getaffinity is None:
        return None
    try:
        count = len(getaffinity(0))
    except OSError:
        return None
    return count or None


def affinity_from_proc_status(path: str = PROC_STATUS_PATH) -> int | None:
    """CPU count from ``Cpus_allowed_list`` in a ``/proc/<pid>/status`` file.

    Backstop for sandboxes that block ``sched_getaffinity`` but still mount
    ``/proc`` — the same kernel fact, read as text. ``path`` is a parameter
    so tests can point it at a real file holding real bytes.
    """
    try:
        with open(path) as handle:
            for line in handle:
                if line.startswith(_CPUS_ALLOWED_KEY):
                    return parse_cpu_list(line[len(_CPUS_ALLOWED_KEY) :])
    except OSError:
        return None
    return None


def read_affinity(
    getaffinity: Callable[[int], set[int]] | None = None,
    proc_status_path: str = PROC_STATUS_PATH,
) -> tuple[int | None, str | None]:
    """Affinity count plus the name of the mechanism that produced it.

    Returns ``(None, None)`` when neither mechanism can answer.
    """
    count = affinity_from_syscall(getaffinity)
    if count is not None:
        return count, "sched_getaffinity"
    count = affinity_from_proc_status(proc_status_path)
    if count is not None:
        return count, "proc_status"
    return None, None


# ---------------------------------------------------------------------------
# Decision — pure, no I/O, every input explicit


def resolve_cpu_sources(
    *,
    affinity: int | None = None,
    affinity_source: str | None = None,
    environ: Mapping[str, str] | None = None,
    cpu_count: int | None = None,
) -> dict[str, Any]:
    """Choose the usable CPU count from already-read inputs. PURE.

    Separated from :func:`get_cpu_sources` so the ordering and the
    fail-closed rules can be exercised directly, with real values, rather
    than by patching this module's internals.

    Returns the same flat dict :func:`get_cpu_sources` documents.
    """
    env = {} if environ is None else environ
    slurm_per_task = _strict_positive_int(env.get(SLURM_CPU_VARS[0]))
    slurm_on_node = _strict_positive_int(env.get(SLURM_CPU_VARS[1]))
    machine = cpu_count if (cpu_count is not None and cpu_count > 0) else None
    affinity = affinity if (affinity is not None and affinity > 0) else None

    usable, source = 1, "default"
    for value, name in (
        (affinity, "affinity"),
        (slurm_per_task, "slurm_cpus_per_task"),
        (slurm_on_node, "slurm_cpus_on_node"),
        (machine, "cpu_count"),
    ):
        if value is not None:
            usable, source = value, name
            break

    return {
        "affinity": affinity,
        "affinity_source": affinity_source if affinity is not None else None,
        "slurm_cpus_per_task": slurm_per_task,
        "slurm_cpus_on_node": slurm_on_node,
        "cpu_count": machine,
        # REPORTED FOR DIAGNOSIS ONLY. Never consulted above — see the
        # module docstring; reading this as a CPU count is the original bug.
        "omp_num_threads": _strict_positive_int(env.get("OMP_NUM_THREADS")),
        "usable": usable,
        "source": source,
    }


# ---------------------------------------------------------------------------
# Public API


def get_cpu_sources(
    *,
    environ: Mapping[str, str] | None = None,
    getaffinity: Callable[[int], set[int]] | None = None,
    cpu_counter: Callable[[], int | None] | None = None,
    proc_status_path: str = PROC_STATUS_PATH,
) -> dict[str, Any]:
    """Report what EVERY CPU source says, plus which one won.

    Returns a flat dict (treat as a public contract; bump minor on rename):

    ``affinity``            int|None   kernel affinity mask size
    ``affinity_source``     str|None   ``sched_getaffinity`` | ``proc_status``
    ``slurm_cpus_per_task`` int|None   ``$SLURM_CPUS_PER_TASK``, strictly parsed
    ``slurm_cpus_on_node``  int|None   ``$SLURM_CPUS_ON_NODE``, strictly parsed
    ``cpu_count``           int|None   ``os.cpu_count()`` — the machine total
    ``omp_num_threads``     int|None   REPORTED ONLY; never influences the answer
    ``usable``              int        the chosen count
    ``source``              str        which key ``usable`` came from

    A ``None`` means "this source had nothing to say", which is different
    from "this source said zero" — both malformed and absent values land on
    ``None`` deliberately, because a source that cannot be trusted must not
    be used.

    All collaborators are injectable; the defaults read the real OS.
    """
    affinity, affinity_source = read_affinity(getaffinity, proc_status_path)
    counter = os.cpu_count if cpu_counter is None else cpu_counter
    return resolve_cpu_sources(
        affinity=affinity,
        affinity_source=affinity_source,
        environ=os.environ if environ is None else environ,
        cpu_count=counter(),
    )


def get_usable_cpus(minimum: int = 1, **kwargs: Any) -> int:
    """Return the number of CPUs this process may actually run on.

    The number to size a worker pool with — ``xdist -n``, a
    ``ProcessPoolExecutor``, a ``--jobs`` flag. See the module docstring for
    the full cascade and for why ``nproc`` is not part of it.

    Parameters
    ----------
    minimum : int
        Floor for the returned value (default 1). A pool of zero workers
        does no work, so callers that would otherwise clamp the result
        themselves can state the floor here instead.
    **kwargs
        Forwarded to :func:`get_cpu_sources` (``environ``, ``getaffinity``,
        ``cpu_counter``, ``proc_status_path``).

    Returns
    -------
    int
        Always ``>= max(1, minimum)``.

    Examples
    --------
    >>> get_usable_cpus() >= 1
    True
    >>> get_usable_cpus(minimum=4) >= 4
    True
    """
    floor = max(1, int(minimum))
    return max(floor, get_cpu_sources(**kwargs)["usable"])
