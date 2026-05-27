---
description: |
  [TOPIC] scitex-resource Python API
  [DETAILS] Top-level public callables — get_specs, get_metrics, get_processor_usages, log_processor_usages, get_machine_name, get_machine_config, load_config.
tags: [scitex-resource-python-api]
---

# Python API

Top-level public surface re-exported from `scitex_resource`.

## Public symbols

| Name                          | Purpose                                                   |
|-------------------------------|-----------------------------------------------------------|
| `__version__`                 | Installed package version                                 |
| `get_specs()`                 | One-shot dict — cpu / memory / disk / network / gpu / os / python |
| `get_metrics()`               | Live `cpu_percent`, `mem_percent`, `disk_percent` snapshot |
| `get_processor_usages()`      | Per-core CPU% list                                        |
| `log_processor_usages(...)`   | Append CPU/RAM/GPU/VRAM rows to CSV on an interval        |
| `get_host_name()`             | Stable host identifier (survives reboots)                 |
| `get_host_config()`           | Per-host config dict (env → project → user → hostname)   |
| `get_machine_name()`          | Deprecated alias for `get_host_name()`                    |
| `get_machine_config()`        | Deprecated alias for `get_host_config()`                  |
| `load_config(path)`           | Low-level YAML loader for arbitrary config files          |
| `main()`                      | CLI entry point used by `python -m scitex_resource._log_processor_usages` |

## Snapshot shape

```python
specs = res.get_specs()
specs["cpu"]["physical"]      # int
specs["memory"]["total_gb"]   # float
specs["gpu"]["available"]     # bool — True iff nvidia-smi found
specs["os"]["name"]           # 'Linux' | 'Darwin' | 'Windows'
specs["python"]["version"]    # e.g. '3.11.6'
```

## Monitor signature

```python
res.log_processor_usages(
    path: str | None = None,   # default: ~/.scitex/resource/runtime/processor_usages.csv
    limit_min: float = 30,     # stop after this many minutes
    interval_s: float = 1,     # sample period in seconds
)
```

Output is CSV — one row per sample with Timestamp, CPU%, RAM, GPU%, VRAM.

## Config layering

`get_host_config()` honors:

1. `$SCITEX_RESOURCE_HOST` env var (highest)
2. project-local `<repo>/.scitex/resource/config.yaml`
3. user-level `$SCITEX_DIR/resource/config.yaml`
4. short hostname (fallback)

Use this to attach project-specific tags / labels to a host without
touching the global config.

## Not exposed

- Sub-second sampling helpers — out of scope; use `perf` / `py-spy`.
- Process-tree walk — out of scope; call `psutil.process_iter()` directly.
