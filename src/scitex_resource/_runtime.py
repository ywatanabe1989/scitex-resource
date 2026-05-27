"""Runtime path resolution — regenerable state under ``~/.scitex/resource/runtime/``.

Every scitex-* package writes regenerable data (logs, caches, PID files,
workspaces, databases) exclusively under ``<pkg-short>/runtime/``. This
module provides the canonical path for the processor-usages CSV log and
any future runtime files.

The resolved path always contains ``/runtime/`` — see the
``local-state-directories`` skill for the full layout.

Legacy locations (``/tmp/scitex/…``) are NOT migrated automatically;
callers that want to point at an old file must pass an explicit ``--path``.
"""

from __future__ import annotations

import os
from pathlib import Path

_PKG_SHORT = "resource"


def _runtime_root() -> Path:
    """Return the user-scope ``runtime/`` root (``$SCITEX_DIR/resource/runtime/``).

    Project-scope runtime dirs are deliberately *not* resolved here — runtime
    data is per-host, not per-project. Callers that need project-scope paths
    should accept an explicit override.
    """
    base = Path(os.environ.get("SCITEX_DIR") or (Path.home() / ".scitex"))
    return base / _PKG_SHORT / "runtime"


def default_log_path() -> str:
    """Return the canonical path for the processor-usages CSV log.

    The parent directory is **not** created here — lazy creation happens on
    first write (see :func:`scitex_resource._log_processor_usages._ensure_log_file`).
    """
    return str(_runtime_root() / "processor_usages.csv")
