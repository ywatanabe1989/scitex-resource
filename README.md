# scitex-resource

System resource info, processor usage logging, and RAM limiting helpers, extracted from the [SciTeX](https://github.com/ywatanabe1989/scitex-python) ecosystem as a standalone package.

## Install

```bash
pip install scitex-resource
```

## API

```python
import scitex_resource as r

# Snapshot of CPU / RAM / disk / GPU / monitor info
specs = r.get_specs()

# CPU/RAM samples (one-shot)
usage = r.get_processor_usages()

# Continuous logging (CSV)
r.log_processor_usages("/tmp/usage.csv", limit_min=30, interval_s=1)

# Cap process RAM
r.limit_ram(0.5)
```

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
