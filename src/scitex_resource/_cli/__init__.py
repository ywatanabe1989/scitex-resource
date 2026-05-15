"""scitex-resource CLI package.

Re-exports ``main`` and the click ``cli`` group so existing imports
``from scitex_resource._cli import main`` work.
"""

from ._root import cli, main

__all__ = ["cli", "main"]
