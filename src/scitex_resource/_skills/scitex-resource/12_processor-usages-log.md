---
description: |
  [TOPIC] Long-running CSV usage logger
  [DETAILS] `log_processor_usages()` pattern -- CSV layout, append-mode
  writes, background process option, and the `--max-rows` CLI ergonomics.
tags: [scitex-resource-processor-usages-log]
---

# Long-running CSV usage logger

`log_processor_usages(path, limit_min, interval_s, init, verbose,
background)` samples `get_processor_usages()` once per `interval_s` and
appends one row to the CSV at `path`. After `limit_min * 60 // interval_s`
samples the loop exits.

## CSV layout

```
Timestamp,CPU [%],RAM [GiB],GPU [%],VRAM [GiB]
2026-05-15 09:00:01,12.4,8.1,0.0,0.0
2026-05-15 09:00:02,13.7,8.2,0.0,0.0
...
```

Headers are written by `_ensure_log_file()` when the file is absent or
when `init=True`. Each sample appends with `pandas.to_csv(..., mode="a",
header=False)`, so no full-file rewrite even for hour-long runs.

## Background mode

```python
proc = log_processor_usages(
    limit_min=60,
    interval_s=5,
    background=True,    # returns multiprocessing.Process
)
# ... do work ...
proc.join()
```

`background=True` returns the live `multiprocessing.Process`. The
default (`background=False`) blocks until done.

## CLI ergonomics

The CLI uses `--max-rows` rather than `--limit-min` because "log N samples
at interval I" is the natural specification for a heartbeat:

```bash
$ scitex-resource processor-usages log \
    --interval 5 --max-rows 12
# wrote 12 rows to ~/.scitex/resource/runtime/processor_usages.csv
```

`limit_min` is computed under the hood as `(max_rows * interval) / 60`.

The default output path is ``~/.scitex/resource/runtime/processor_usages.csv``.
Override with ``--path``.

## Reading back

```python
import pandas as pd
from pathlib import Path
path = Path.home() / ".scitex" / "resource" / "runtime" / "processor_usages.csv"
df = pd.read_csv(path, parse_dates=["Timestamp"])
df.set_index("Timestamp")["CPU [%]"].plot()
```

## Stopping early

Send `SIGINT` (Ctrl-C) -- the loop exits cleanly between samples and
the CSV is left in a valid state thanks to the row-at-a-time append
write.
