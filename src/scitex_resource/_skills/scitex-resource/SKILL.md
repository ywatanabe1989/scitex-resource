---
name: scitex-resource
description: |
  [WHAT] System resource introspection — canonical machine name, rich
  human-formatted specs (CPU/GPU/disk/network), flat machine-readable
  metrics for heartbeats, single-row processor usage snapshots, a
  long-running CSV usage logger, and per-process RAM limit (RLIMIT_AS).
  [WHEN] Building monitors / dashboards / heartbeats; deciding what host
  a multi-cluster ecosystem is running on; capping a python process's
  memory footprint; logging CPU/RAM/GPU/VRAM time series.
  [HOW] `from scitex_resource import get_specs, get_metrics, get_host_name`,
  or `scitex-resource <noun> <verb> [--json|--yaml]`.
primary_interface: python
interfaces:
  python: 3
  cli: 2
  mcp: 2
  skills: 2
  hook: 0
  http: 0
tags: [scitex-resource]
---

# scitex-resource

The ecosystem's single source of truth for "what machine am I on?" and
"how much CPU/RAM/GPU does it have right now?". All other scitex-*
packages (scitex-orochi, scitex-hpc, scitex-agent-container, ...) consume
`get_machine_name()` so they agree on one canonical identity regardless
of FQDN drift or login-vs-compute-node split.

## Three observation tiers

| Tier | Function | Shape | Use when |
|---|---|---|---|
| Rich human specs | `get_specs(...)` | nested dict (or YAML) | one-off display, experiment header |
| Flat metrics | `get_metrics(gpu=True)` | flat dict | heartbeats, dashboards, wire payloads |
| Live usages | `get_processor_usages()` | 1-row DataFrame | sampling loops, CSV time series |

## Sub-skills

### Core (01-05)
- [01_installation.md](01_installation.md) -- pip install + smoke verify
- [02_quick-start.md](02_quick-start.md) -- snapshot + live metrics
- [03_python-api.md](03_python-api.md) -- public callables reference

### Interfaces (04-09)
- [04_cli-reference.md](04_cli-reference.md) -- CLI cheat sheet
- [05_mcp-tools.md](05_mcp-tools.md) -- MCP tool surface

### Topics (10-19)
- [10_machine-identity.md](10_machine-identity.md) -- resolution cascade
- [11_specs-vs-metrics.md](11_specs-vs-metrics.md) -- which tier to use
- [12_processor-usages-log.md](12_processor-usages-log.md) -- long-running CSV logger
- [13_ram-limit.md](13_ram-limit.md) -- RLIMIT_AS + linux child-proc gotcha
