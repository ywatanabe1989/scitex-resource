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
| `get_machine_name` | `get_machine_name()` | env > config > short hostname |
| `get_machine_config` | `get_machine_config()` | per-host `machine:` block |
| `get_specs` | `get_specs(system,cpu,gpu,disk,network)` | nested dict |
| `get_metrics` | `get_metrics(gpu=True)` | flat dict for heartbeats |
| `get_processor_usages` | `get_processor_usages()` | list-of-records (1 row) |
| `log_processor_usages` | `log_processor_usages(...)` | blocks; bg=False |
| `limit_ram` | `limit_ram(factor)` | 0 < factor <= 1 |
| `get_ram` | `get_ram()` | KiB free |
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
