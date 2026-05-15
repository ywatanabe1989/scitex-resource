---
description: |
  [TOPIC] scitex-resource MCP tools
  [DETAILS] The MCP tools exposed by `scitex-resource-mcp` (FastMCP over stdio). Each tool delegates to the canonical Python API — no logic duplication. Wire scitex-resource into an MCP-aware agent / IDE; sanity-check via `scitex-resource mcp list-tools`. Install: `pip install scitex-resource[mcp]`; launch: `scitex-resource-mcp`.
tags: [scitex-resource-mcp-tools]
---

# MCP tools

The MCP server is a single `FastMCP("scitex-resource")` instance. Tools use
bare names (no `resource_` prefix); an umbrella bridge can re-export them
under a namespace via `safe_mount(..., namespace="resource")`.

## Tool surface

| Tool | Maps to Python API | Notes |
|---|---|---|
| `machine_show` | `get_machine_name()` | env > config > short hostname |
| `machine_config` | `get_machine_config()` | per-host `machine:` block |
| `specs_show` | `get_specs(system,cpu,gpu,disk,network,verbose=False,yaml=False)` | nested dict |
| `metrics_show` | `get_metrics(gpu=True)` | flat dict for heartbeats |
| `processor_usages_show` | `get_processor_usages()` | list-of-records (1 row) |
| `processor_usages_log` | `log_processor_usages(...)` | blocks; bg=False |
| `ram_limit_set` | `limit_ram(factor)` | 0 < factor <= 1 |
| `ram_limit_get` | `get_ram()` | KiB free |
| `get_machine_name` | alias of `machine_show` | API-name parity (audit §7) |
| `get_machine_config` | alias of `machine_config` | API-name parity |
| `get_specs` | alias of `specs_show` | API-name parity |
| `get_metrics` | alias of `metrics_show` | API-name parity |
| `get_processor_usages` | alias of `processor_usages_show` | API-name parity |
| `log_processor_usages` | alias of `processor_usages_log` | API-name parity |
| `skills_list`, `skills_get` | -- | bundled markdown access |

## Listing what is actually registered

```bash
scitex-resource mcp list-tools
scitex-resource mcp list-tools --json
```

## Running the server

```bash
scitex-resource-mcp           # stdio MCP server
```

The server runs `mcp.run()` which uses stdio transport by default.

## Caveats

* `processor_usages_log` blocks for `max_rows * interval_s` seconds; the
  agent will be stalled. Prefer calling the Python API with `background=True`
  for long captures.
* `ram_limit_set` is per-process; child processes do not inherit on Linux.
* `metrics_show` shells out to `nvidia-smi` when `gpu=True` and the binary is
  on `$PATH`.
