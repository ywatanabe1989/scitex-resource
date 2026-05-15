"""Machine identity — canonical name and per-host config.

scitex-resource owns the question "what machine am I running on?". Other
scitex-* packages (scitex-orochi, scitex-hpc, scitex-agent-container)
consume :func:`get_machine_name` so every package agrees on the same
canonical name regardless of how the OS reports it (FQDN drift,
``Yusukes-MacBook-Air`` vs ``mba``, login-node vs compute-node, etc.).

Resolution cascade (highest precedence first):

    1. ``$SCITEX_RESOURCE_MACHINE`` env var
    2. ``<project>/.scitex/resource/config.yaml`` ``machine.canonical_name``
    3. ``~/.scitex/resource/config.yaml`` ``machine.canonical_name``
    4. Short hostname (``socket.gethostname().split(".", 1)[0]``)

The same chain applies to :func:`get_machine_config` which returns the
full ``machine:`` block including ``aliases``, ``role``, ``hpc.*``.

Config schema (``~/.scitex/resource/config.yaml`` — example for a SLURM
login node):

    machine:
      canonical_name: spartan
      aliases:
        - spartan-login1.hpc.example.edu
        - spartan-login1
      role: hpc-login
      hpc:
        cluster: spartan
        login_only: true        # don't surface login-node CPU as available
        partitions: [physical, sapphire]

This file is part of the scitex local-state convention — see the
``arch-local-state-directories`` skill in scitex-python for the full
``.scitex/<pkg-short>/`` layout (config tracked, ``runtime/`` ignored).
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from typing import Any

_PKG_SHORT = "resource"
_ENV_VAR = "SCITEX_RESOURCE_MACHINE"


def _config_paths() -> list[Path]:
    """Search order for ``config.yaml`` — project scope first, user fallback.

    The project search walks from cwd up to (but stops AT) ``$HOME`` so
    the user's ``~/.scitex/<pkg>/config.yaml`` is not mistaken for a
    project hit when cwd happens to live under home (which it almost
    always does on a workstation).
    """
    paths: list[Path] = []
    cwd_root = Path.cwd()
    home = Path.home().resolve()
    for parent in (cwd_root, *cwd_root.parents):
        try:
            resolved = parent.resolve()
        except OSError:
            resolved = parent
        if resolved == home:
            break
        candidate = parent / ".scitex" / _PKG_SHORT / "config.yaml"
        if candidate.is_file():
            paths.append(candidate)
            break
    user_root = Path(os.environ.get("SCITEX_DIR") or (Path.home() / ".scitex"))
    user = user_root / _PKG_SHORT / "config.yaml"
    if user.is_file():
        paths.append(user)
    return paths


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError):
        return {}


def load_config() -> dict[str, Any]:
    """Return the merged config dict — project file overrides user file.

    Empty dict if no config files exist or PyYAML isn't installed.
    """
    merged: dict[str, Any] = {}
    for path in reversed(_config_paths()):
        data = _load_yaml(path)
        merged.update(data)
    return merged


def get_machine_config() -> dict[str, Any]:
    """Return the ``machine:`` block from config, or ``{}``."""
    cfg = load_config()
    return cfg.get("machine") or {}


def get_machine_name() -> str:
    """Return the canonical machine name.

    See module docstring for the resolution cascade. Always returns a
    non-empty string — the short hostname is the last-resort fallback.
    """
    env = os.environ.get(_ENV_VAR, "").strip()
    if env:
        return env
    cfg = get_machine_config()
    canonical = (cfg.get("canonical_name") or "").strip()
    if canonical:
        return canonical
    return _short_hostname()


def _short_hostname() -> str:
    try:
        return socket.gethostname().split(".", 1)[0] or "unknown"
    except OSError:
        return "unknown"
