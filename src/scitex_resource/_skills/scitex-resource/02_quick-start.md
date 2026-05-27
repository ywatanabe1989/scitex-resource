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
res.log_processor_usages(limit_min=30, interval_s=1)
# Appends CSV rows to ~/.scitex/resource/runtime/processor_usages.csv
```

Read back with standard tools:

```python
import pandas as pd
df = pd.read_csv("~/.scitex/resource/runtime/processor_usages.csv")
```

## Per-host identity

```python
name = res.get_host_name()           # stable across reboots
cfg  = res.get_host_config()         # honors $SCITEX_DIR / project scope
```

`get_host_config()` resolves through the config cascade (env → project →
user → hostname), so a project can override the global host config via
`<repo>/.scitex/resource/config.yaml`.
