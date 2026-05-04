---
description: |
  [TOPIC] scitex-resource Quick Start
  [DETAILS] Smallest example — capture a one-shot machine snapshot, then live CPU/mem metrics.
tags: [scitex-resource-quick-start]
---

# Quick Start

## One-shot snapshot

```python
import scitex_resource as res

specs = res.get_specs()
# {'cpu': {...}, 'memory': {...}, 'disk': {...}, 'network': {...},
#  'gpu': {...}, 'os': {...}, 'python': {...}}
```

Save this dict at the top of an analysis script so you can later answer
"what machine produced this result?".

## Live metrics

```python
m = res.get_metrics()                  # {'cpu_percent': ..., 'mem_percent': ..., 'disk_percent': ...}
cores = res.get_processor_usages()     # per-core CPU%
```

## Long-running monitor

```python
res.log_processor_usages(interval_s=10, duration_s=3600)
# Appends JSONL to <scitex_dir>/resource/runtime/usages-*.jsonl
```

Read back with standard tools:

```python
import pandas as pd
df = pd.read_json("<path>.jsonl", lines=True)
```

## Per-host identity

```python
name = res.get_machine_name()          # stable across reboots
cfg  = res.get_machine_config()        # honors $SCITEX_DIR / project scope
```

`get_machine_config()` resolves through `scitex_config._ecosystem.local_state`,
so a project can override the global host config via
`<repo>/.scitex/resource/config.yaml`.
