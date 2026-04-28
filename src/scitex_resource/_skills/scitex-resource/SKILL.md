---
name: scitex-resource
description: System resource introspection + monitoring. `get_specs()` returns full hardware/OS/Python snapshot (CPU, memory, disk, network, GPU, OS, Python version) as a nested dict. `get_metrics()` is the lightweight live snapshot (CPU%, mem%, disk%). `get_processor_usages()` returns per-core CPU usage. `log_processor_usages(...)` runs a long-running monitor that appends usage to a JSONL log under `<scitex_dir>/resource/runtime/` for later inspection. `get_machine_name()` returns a stable identifier (hostname + uniquifier) usable as a key in cross-host configs; `get_machine_config()` looks up the per-host overrides via `local_state`. Drop-in replacement for ad-hoc `psutil.cpu_percent() + psutil.virtual_memory()` snippets, hand-rolled `socket.gethostname()` keying, and bespoke "what hardware is this script running on" header blocks at the top of analysis scripts.
primary_interface: python
interfaces:
  python: 3
  cli: 1
  mcp: 0
  skills: 2
  hook: 0
  http: 0
canonical-location: scitex-resource/src/scitex_resource/_skills/scitex-resource/SKILL.md
tags: [scitex-resource, scitex-package, system-info, monitoring, hardware]
---

> **Interfaces:** Python ⭐⭐⭐ (primary) · CLI ⭐ · MCP — · Skills ⭐⭐ · Hook — · HTTP —

# scitex-resource

Single-call system introspection + lightweight monitoring.

## One-shot snapshot

```python
import scitex_resource as res

specs = res.get_specs()
# {'cpu': {...}, 'memory': {...}, 'disk': {...}, 'network': {...},
#  'gpu': {...}, 'os': {...}, 'python': {...}}
```

Use as a header in analysis scripts so you can later answer "what
machine produced this result?".

## Live metrics

```python
m = res.get_metrics()              # CPU%, mem%, disk%
cpu_per_core = res.get_processor_usages()
```

## Monitoring loop

```python
res.log_processor_usages(interval_s=10, duration_s=3600)
# Appends JSONL entries to <scitex_dir>/resource/runtime/usages-*.jsonl
```

Reads back as standard JSONL (`pandas.read_json(path, lines=True)`).

## Per-host configuration

```python
name = res.get_machine_name()                # stable across reboots
cfg = res.get_machine_config()               # honors $SCITEX_DIR / project scope
```

`get_machine_config` resolves through `scitex_config._ecosystem.local_state`,
so a project can override the global host config via
`<repo>/.scitex/resource/config.yaml`.

## When to use

- ✅ Reproducibility — record `get_specs()` at the top of an experiment
- ✅ HPC dashboards — feed `get_metrics()` into a status panel
- ✅ Per-host CLI behavior — branch on `get_machine_name()`
- ❌ Sub-second profiling — `psutil` is rate-limited; use `perf` /
  `py-spy` instead

## See also

- `scitex-events` — emit `get_metrics()` as periodic events for cloud
  forwarding
- `scitex-config` — per-host config layered over `$SCITEX_DIR`
- General skill `01_arch_06_local-state-directories.md` — runtime path
  policy

<!-- EOF -->
