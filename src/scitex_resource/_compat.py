"""Tiny compat shims for symbols that used to come from scitex.str / scitex.gen.

Vendored here so scitex-resource has no scitex.* runtime deps.
"""

from __future__ import annotations

import os
import sys


def readable_bytes(num_bytes: float | int, suffix: str = "B") -> str:
    """Human-readable byte size (e.g. 1024 → '1.0KiB'). Vendored from scitex.str."""
    n = float(num_bytes)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(n) < 1024.0:
            return f"{n:3.1f}{unit}{suffix}"
        n /= 1024.0
    return f"{n:.1f}Yi{suffix}"


# Alias used by limit_ram.py
fmt_size = readable_bytes


def printc(text: str, c: str = "white") -> None:
    """Colored print — vendored from scitex.str.printc. Respects NO_COLOR + TTY."""
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        print(text)
        return
    codes = {
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }
    print(f"{codes.get(c, '')}{text}\033[0m")
