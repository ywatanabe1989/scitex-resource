#!/usr/bin/env python3
"""Per-edge integration + degradation tests for the OPTIONAL scitex-sh edge.

The edge under test
-------------------
``scitex_resource._log_processor_usages.sh(cmd, **kwargs)`` is a thin shell
helper. scitex-sh is an OPTIONAL dependency (``scitex-resource[sh]``):

  - PRESENT: ``sh`` delegates to ``scitex_sh.sh``, the hardened,
    list-form-only shell runner shared across the ecosystem.
  - ABSENT: ``sh`` degrades to the stdlib ``subprocess`` fallback. To preserve
    scitex-sh's shell-injection-safe contract, the fallback *still* refuses
    string-form commands (raising ``ValueError``) and only runs list-form
    commands, returning their captured stdout.

The two test kinds every optional edge should have
--------------------------------------------------
1. INTEGRATION (collaborator PRESENT): exercise the real ``scitex_sh`` and
   assert on concrete behaviour. Guarded with
   ``pytest.importorskip("scitex_sh")`` so minimal installs stay green.

2. DEGRADATION (collaborator ABSENT): simulate scitex-sh missing in a
   hermetic, reversible way — snapshot ``sys.modules``, shadow ``scitex_sh``
   with an inert ``None`` so a *fresh* ``import scitex_sh`` raises ImportError,
   reload the edge module so it re-runs its ``try/except ImportError`` guard,
   then restore everything on teardown. Assert the documented graceful
   contract: list-form still runs via subprocess; string-form raises the
   documented ``ValueError`` rather than leaking an opaque traceback.

Conventions honoured (matching the package's existing integration tests):
  - One behaviour per test with explicit Arrange / Act / Assert markers.
  - No ``monkeypatch`` / ``mocker`` (banned): the scitex-sh-absent fixture
    hand-swaps ``sys.modules`` and restores it on teardown.
"""

from __future__ import annotations

import importlib
import sys

import pytest

# ===========================================================================
# 1. INTEGRATION  —  scitex_sh PRESENT
# ===========================================================================
pytest.importorskip("scitex_sh")


@pytest.fixture
def sh_with_scitex_sh():
    """The edge ``sh`` helper with scitex_sh present (its top-level state)."""
    import scitex_resource._log_processor_usages as mod

    # Ensure the module reflects the real (scitex_sh-present) environment in
    # case an earlier degradation test reloaded it; reload is cheap and pure.
    importlib.reload(mod)
    return mod.sh


def test_sh_delegates_to_scitex_sh_returns_stdout(sh_with_scitex_sh):
    """With scitex_sh present, a list-form command returns its stdout string."""
    # Arrange
    sh = sh_with_scitex_sh
    # Act
    out = sh(["echo", "edge_present"], verbose=False, return_as="str")
    # Assert
    assert out.strip() == "edge_present"


def test_sh_uses_scitex_sh_implementation(sh_with_scitex_sh):
    """The PRESENT path really routes through scitex_sh (not the fallback)."""
    # Arrange
    import scitex_sh

    sh = sh_with_scitex_sh
    # Act
    # scitex_sh.sh accepts return_as="dict"; the subprocess fallback does not
    # understand that kwarg. A dict result therefore proves scitex_sh ran.
    result = sh(["echo", "via_scitex_sh"], verbose=False, return_as="dict")
    # Assert
    assert isinstance(result, dict)


def test_sh_scitex_sh_rejects_string_command(sh_with_scitex_sh):
    """scitex_sh enforces list-form commands (shell-injection safety)."""
    # Arrange
    sh = sh_with_scitex_sh
    # Act
    raises = pytest.raises((ValueError, TypeError))
    # Assert
    with raises:
        sh("echo injected", verbose=False)


# ===========================================================================
# 2. DEGRADATION  —  scitex_sh ABSENT
# ===========================================================================
@pytest.fixture
def sh_without_scitex_sh():
    """Make ``import scitex_sh`` fail for the duration of the test.

    Hermetic and reversible:
      1. snapshot the whole ``sys.modules`` so teardown restores it exactly;
      2. evict any cached ``scitex_sh`` modules and shadow ``scitex_sh`` with
         ``None`` so a *fresh* ``import scitex_sh`` raises ImportError;
      3. reload the edge module so its module-level ``sh`` re-runs its
         ``try: from scitex_sh import sh ... except ImportError`` guard under
         the missing dependency.

    Yields the freshly reloaded edge ``sh`` callable.
    """
    import scitex_resource._log_processor_usages as mod

    # 1. Snapshot for an exact restore.
    snapshot = dict(sys.modules)

    # 2. Evict + shadow scitex_sh so a fresh import raises ImportError.
    for name in list(sys.modules):
        if name == "scitex_sh" or name.startswith("scitex_sh."):
            del sys.modules[name]
    sys.modules["scitex_sh"] = None  # type: ignore[assignment]

    # 3. Reload the edge module under the missing dependency.
    importlib.reload(mod)
    try:
        yield mod.sh
    finally:
        # Exact restore, then reload so later tests see the real scitex_sh.
        sys.modules.clear()
        sys.modules.update(snapshot)
        importlib.reload(mod)


def test_sh_falls_back_to_subprocess_for_list_command(sh_without_scitex_sh):
    """Without scitex_sh, a list-form command still runs via subprocess."""
    # Arrange
    sh = sh_without_scitex_sh
    # Act
    out = sh(["echo", "edge_absent"])
    # Assert
    assert out.strip() == "edge_absent"


def test_sh_fallback_returns_str(sh_without_scitex_sh):
    """The subprocess fallback returns captured stdout as a plain str."""
    # Arrange
    sh = sh_without_scitex_sh
    # Act
    out = sh(["echo", "typed"])
    # Assert
    assert isinstance(out, str)


def test_sh_fallback_rejects_string_command(sh_without_scitex_sh):
    """The fallback preserves the list-form-only safety contract."""
    # Arrange
    sh = sh_without_scitex_sh
    # Act
    raises = pytest.raises(ValueError)
    # Assert
    with raises:
        sh("echo injected")


@pytest.fixture
def fallback_string_command_error(sh_without_scitex_sh):
    """Capture the ValueError message raised by the fallback on a str command."""
    with pytest.raises(ValueError) as excinfo:
        sh_without_scitex_sh("echo injected")
    return str(excinfo.value)


def test_sh_fallback_string_command_error_message(fallback_string_command_error):
    """The degraded path raises the documented, caller-readable message."""
    # Arrange
    message = fallback_string_command_error
    # Act
    is_documented = "must be list-form" in message
    # Assert
    assert is_documented


def test_sh_fallback_does_not_leak_importerror(sh_without_scitex_sh):
    """Degradation is graceful: no raw ImportError escapes to the caller."""
    # Arrange
    sh = sh_without_scitex_sh
    # Act
    raised_importerror = False
    try:
        sh(["echo", "graceful"])
    except ImportError:
        raised_importerror = True
    # Assert
    assert raised_importerror is False
