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
| `log_processor_usages(...)`   | Append per-core CPU% to JSONL on an interval              |
| `get_machine_name()`          | Stable host identifier (survives reboots)                 |
| `get_machine_config()`        | Per-host config dict (layered via `scitex_config`)        |
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
    interval_s: float = 10,    # sample period
    duration_s: float = 3600,  # stop after this many seconds
    out_path: str | None = None,  # default: <scitex_dir>/resource/runtime/
)
```

Output is JSONL — one line per sample with timestamp + per-core values.

## Config layering

`get_machine_config()` honors:

1. project-local `<repo>/.scitex/resource/config.yaml`
2. user-level `$SCITEX_DIR/resource/config.yaml`
3. package defaults

Use this to attach project-specific tags / labels to a host without
touching the global config.

## Not exposed

- Sub-second sampling helpers — out of scope; use `perf` / `py-spy`.
- Process-tree walk — out of scope; call `psutil.process_iter()` directly.
