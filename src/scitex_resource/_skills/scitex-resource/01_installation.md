---
description: |
  [TOPIC] scitex-resource Installation
  [DETAILS] pip install scitex-resource (psutil-backed); smoke verify with get_specs().
tags: [scitex-resource-installation]
---

# Installation

## Standard

```bash
pip install scitex-resource
```

Pulls `psutil` (system stats) and `scitex-config` (per-host config
layering) as runtime dependencies.

## Umbrella

```bash
pip install scitex            # also exposes the same module as scitex.resource
```

`pip install scitex-resource` alone does NOT make `import scitex.resource`
work — install the umbrella for that form. See
`../../general/02_interface-python-api.md`.

## Verify

```bash
python -c "import scitex_resource as r; print(r.__version__); print(r.get_specs()['os']['name'])"
```

Expected: a version string followed by your OS name (e.g. `Linux`).

## Optional: GPU specs

`get_specs()['gpu']` is best-effort — populated when `nvidia-smi` is
available on PATH. Otherwise it returns `{'available': False, ...}`.
No extra Python dependency is required.

## When NOT to install

- Sub-second profiling — use `perf` / `py-spy` instead, `psutil` is
  rate-limited.
- Container-internal CPU limits — `psutil` reports the host view; pair
  with `scitex-container` for container-aware measurement.
