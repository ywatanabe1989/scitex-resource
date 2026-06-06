---
description: |
  [TOPIC] Specs vs metrics vs processor-usages
  [DETAILS] How to choose between the three observation tiers and what
  shape each returns.
tags: [scitex-resource-specs-vs-metrics]
---

# Specs vs metrics vs processor-usages

scitex-resource exposes three system-introspection tiers. They look
similar but answer different questions.

| Function | Shape | Cost | Use when |
|---|---|---|---|
| `get_specs(...)` | nested dict (or YAML string) | high (~1 s, includes a 1 s CPU sample) | one-off display; experiment header |
| `get_metrics(gpu=True)` | flat dict of ints / floats / short strings | low (~10 ms, +200 ms for nvidia-smi) | heartbeats; dashboard polling; wire payloads |
| `get_processor_usages()` | 1-row pandas DataFrame | medium (psutil + nvidia-smi shellout) | sampling loops feeding a CSV |

## get_specs

Rich, human-formatted. Includes torch version, pip packages, conda
packages, full CPU-per-core breakdown, partition table. The fields use
human keys (`"Physical cores"`, `"Total Sent"`, etc.) and pre-formatted
byte strings (`"15.4 GiB"`). Section toggles: `system=`, `cpu=`, `gpu=`,
`disk=`, `network=`. Output type switches to YAML string with
`yaml=True`.

## get_metrics

Flat, machine-readable. The schema is a public contract:

```
cpu_count, cpu_model, load_avg_1m/5m/15m,
mem_total_mb, mem_used_mb, mem_free_mb, mem_used_percent,
disk_total_mb, disk_used_mb, disk_used_percent,
gpus: [{name, vram_total_mb, vram_used_mb}, ...]
```

Container-aware: inside Docker / cgroups, `psutil.virtual_memory()`
reports the cgroup limit, not the host kernel. So the numbers reflect
what the process can actually use. Set `gpu=False` to skip the ~200 ms
`nvidia-smi` shellout on hot paths.

## get_processor_usages

Single-sample DataFrame with columns
`Timestamp, CPU [%], RAM [GiB], GPU [%], VRAM [GiB]`. Designed to be
`pd.concat`'d into a longer time series -- see
[12_processor-usages-log.md](12_processor-usages-log.md).

## CLI quick mapping

```bash
$ scitex-resource specs show                # get_specs(...)
$ scitex-resource specs show --no-gpu --json
$ scitex-resource metrics show              # get_metrics(...)
$ scitex-resource metrics show --no-gpu --json
$ scitex-resource processor-usages show     # get_processor_usages()
$ scitex-resource processor-usages show --csv
```
