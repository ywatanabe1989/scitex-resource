# scitex-resource

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>System resource info, processor usage logging, RAM limiting + machine-identity config.</b></p>

<p align="center">
  <a href="https://scitex-resource.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-resource</code>
</p>

<!-- scitex-badges:start -->
<p align="center">
  <a href="https://pypi.org/project/scitex-resource/"><img src="https://img.shields.io/pypi/v/scitex-resource.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/scitex-resource/"><img src="https://img.shields.io/pypi/pyversions/scitex-resource.svg" alt="Python"></a>
  <a href="https://github.com/ywatanabe1989/scitex-resource/actions/workflows/test.yml"><img src="https://github.com/ywatanabe1989/scitex-resource/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/ywatanabe1989/scitex-resource/actions/workflows/install-test.yml"><img src="https://github.com/ywatanabe1989/scitex-resource/actions/workflows/install-test.yml/badge.svg" alt="Install Test"></a>
  <a href="https://codecov.io/gh/ywatanabe1989/scitex-resource"><img src="https://codecov.io/gh/ywatanabe1989/scitex-resource/graph/badge.svg" alt="Coverage"></a>
  <a href="https://scitex-resource.readthedocs.io/en/latest/"><img src="https://readthedocs.org/projects/scitex-resource/badge/?version=latest" alt="Docs"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/license-AGPL_v3-blue.svg" alt="License: AGPL v3"></a>
</p>
<!-- scitex-badges:end -->

---

## Installation

```bash
pip install scitex-resource
```

## Quick Start

```python
import scitex_resource as r

print(r.get_machine_name())          # canonical machine identity
metrics = r.get_metrics()            # cpu / mem / disk / gpu / load
specs = r.get_specs()                # rich human-readable snapshot
```

## 1 Interfaces

<details open>
<summary><strong>Python API</strong></summary>

<br>

```python
import scitex_resource as r

# Hub-friendly metrics (cross-platform via psutil)
metrics = r.get_metrics()

# Canonical machine identity
name = r.get_machine_name()
cfg = r.get_machine_config()        # {"canonical_name", "aliases", "role", "hpc": {...}}

# Rich snapshot
specs = r.get_specs()

# CPU/RAM samples + continuous CSV logging
usage = r.get_processor_usages()
r.log_processor_usages("/tmp/usage.csv", limit_min=30, interval_s=1)

# Cap process RAM
r.limit_ram(0.5)
```

</details>

## Machine identity config — `~/.scitex/resource/config.yaml`

```yaml
machine:
  canonical_name: mba                  # what every scitex-* package uses to refer to this host
  aliases:                              # optional; cross-package discovery / drift detection
    - Yusukes-MacBook-Air
    - Yusukes-MacBook-Air.local
  role: head                            # generic role tag (head, worker, hpc-login, ...)
  hpc:                                  # optional; HPC-only
    cluster: spartan
    login_only: true
    partitions: [physical, sapphire]
```

Resolution cascade (highest precedence first):

1. `$SCITEX_RESOURCE_MACHINE`
2. `<project>/.scitex/resource/config.yaml` `machine.canonical_name`
3. `~/.scitex/resource/config.yaml` `machine.canonical_name`
4. `socket.gethostname().split(".", 1)[0]`

## Status

Standalone fork of `scitex.resource`. Deps: pandas, psutil, PyYAML, matplotlib.

Decoupling notes:
- `scitex.str.readable_bytes` / `scitex.gen.fmt_size` / `scitex.str.printc` →
  vendored as 3 small helpers in `_compat.py`.
- `scitex.io._load.load` / `scitex.io._save.save` → use `pandas.read_csv` /
  `to_csv` directly for the CSV log files.
- `scitex.sh.sh` → prefer `scitex_sh` if installed, fall back to plain
  `subprocess.run` (list-only).

The umbrella package's `scitex.resource` import path is preserved via a
`sys.modules`-alias bridge.

## Part of SciTeX

`scitex-resource` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[resource]` to use as
`scitex.resource` (Python) or `scitex resource ...` (CLI).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>
