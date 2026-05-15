---
description: |
  [TOPIC] Per-process RAM limit (RLIMIT_AS)
  [DETAILS] How `limit_ram(factor)` sets RLIMIT_AS, and why the limit
  does NOT propagate to fork+exec children on Linux.
tags: [scitex-resource-ram-limit]
---

# Per-process RAM limit (RLIMIT_AS)

`limit_ram(factor)` caps the current python process's virtual address
space at `factor * (MemFree + Buffers + Cached)`, with `0 < factor <= 1`.

```python
from scitex_resource import limit_ram

limit_ram.limit_ram(0.25)   # cap at 25% of currently-free RAM
```

Backed by `resource.setrlimit(resource.RLIMIT_AS, ...)`. Allocations
above the cap raise `MemoryError`.

## Gotcha: linux exec children do not inherit

On linux, `RLIMIT_AS` set via `setrlimit()` DOES inherit across `fork()`
and across `subprocess.Popen` (which fork+execs). But:

- `os.execv` / `os.execve` (replace-current-process) keep the limit.
- A child python that itself calls `setrlimit(RLIMIT_AS, (RLIM_INFINITY,
  hard))` to raise its own soft limit will succeed only up to the
  current hard limit.
- Containers (Docker / cgroups) impose a *separate* cap that
  `setrlimit` cannot exceed -- the effective cap is the
  minimum of the two.

In short: the cap is a per-process address-space ceiling. For ecosystem
guarantees ("this whole tree uses <= N GiB") use cgroups
(`systemd-run --user --scope -p MemoryMax=...`) instead.

## Companion: get_ram()

```python
from scitex_resource.limit_ram import get_ram
free_kib = get_ram()   # MemFree + Buffers + Cached, in KiB
```

Reads `/proc/meminfo`. Linux-only. The CLI surfaces this:

```bash
$ scitex-resource ram-limit get
free_kib: 8127436
$ scitex-resource ram-limit set 0.5
```
