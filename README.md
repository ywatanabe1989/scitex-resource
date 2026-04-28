# scitex-resource

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-resource.svg)](https://pypi.org/project/scitex-resource/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-resource.svg)](https://pypi.org/project/scitex-resource/)
[![Tests](https://github.com/ywatanabe1989/scitex-resource/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-resource/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-resource/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-resource/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-resource/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-resource)
[![Docs](https://readthedocs.org/projects/scitex-resource/badge/?version=latest)](https://scitex-resource.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->


System resource info, processor usage logging, and RAM limiting helpers, extracted from the [SciTeX](https://github.com/ywatanabe1989/scitex-python) ecosystem as a standalone package.

## Install

```bash
pip install scitex-resource
```

## API

```python
import scitex_resource as r

# Flat hub-friendly metrics (cpu/mem/disk/gpu/load) — cross-platform via psutil
metrics = r.get_metrics()

# Canonical machine identity — every scitex-* package consumes this so they
# all agree on "what host am I". Resolves env > project config > user config
# > short hostname. See ~/.scitex/resource/config.yaml below.
name = r.get_machine_name()
cfg = r.get_machine_config()        # {"canonical_name", "aliases", "role", "hpc": {...}}

# Rich human-readable snapshot (system info, GPU, network, disk partitions)
specs = r.get_specs()

# CPU/RAM samples + continuous CSV logging
usage = r.get_processor_usages()
r.log_processor_usages("/tmp/usage.csv", limit_min=30, interval_s=1)

# Cap process RAM
r.limit_ram(0.5)
```

### Machine identity config — `~/.scitex/resource/config.yaml`

```yaml
machine:
  canonical_name: mba                  # what every scitex-* package uses to refer to this host
  aliases:                              # optional; cross-package discovery / drift detection
    - Yusukes-MacBook-Air
    - Yusukes-MacBook-Air.local
  role: head                            # generic role tag (head, worker, hpc-login, ...)
  hpc:                                  # optional; HPC-only
    cluster: spartan
    login_only: true                    # don't surface login-node CPU as available
    partitions: [physical, sapphire]
```

Resolution cascade (highest precedence first):

1. `$SCITEX_RESOURCE_MACHINE`
2. `<project>/.scitex/resource/config.yaml` `machine.canonical_name`
3. `~/.scitex/resource/config.yaml` `machine.canonical_name`
4. `socket.gethostname().split(".", 1)[0]`

This is the **ecosystem convention** — see scitex-python `_skills/general/01_arch_06_local-state-directories.md` for the full `.scitex/<pkg-short>/` layout (config tracked, `runtime/` ignored).

## Status

Standalone fork of `scitex.resource`. Deps: pandas, psutil, PyYAML, matplotlib.

Decoupling notes:
- `scitex.str.readable_bytes` / `scitex.gen.fmt_size` / `scitex.str.printc` →
  vendored as 3 small helpers in `_compat.py`.
- `scitex.io._load.load` / `scitex.io._save.save` → use `pandas.read_csv` /
  `to_csv` directly for the CSV log files; defer to scitex.io only if a
  non-CSV path is requested (raises ImportError without scitex installed).
- `scitex.sh.sh` → prefer `scitex_sh` if installed, fall back to plain
  `subprocess.run` (list-only).
- `scitex.session.start/close` `__main__` block → simplified to plain `main()`.

The umbrella package's `scitex.resource` import path is preserved via a
`sys.modules`-alias bridge. 65/65 tests pass.

## License

AGPL-3.0-only (see [LICENSE](./LICENSE)).
