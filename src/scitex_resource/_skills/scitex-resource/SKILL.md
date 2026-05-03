---
name: scitex-resource
description: |
  [WHAT] System resource introspection + monitoring.
  [WHEN] Use when working with scitex-resource APIs or when the user mentions scitex.resource..
  [HOW] `import scitex_resource` then call `get_specs()`.
tags: [scitex-resource]
primary_interface: python
interfaces:
  python: 3
  cli: 1
  mcp: 0
  skills: 2
  hook: 0
  http: 0
canonical-location: scitex-resource/src/scitex_resource/_skills/scitex-resource/SKILL.md
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
