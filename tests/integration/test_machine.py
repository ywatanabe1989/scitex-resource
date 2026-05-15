"""Integration tests for ``scitex_resource._machine`` — resolution cascade.

Other scitex-* packages depend on env > project > user > hostname.
Uses real env-var mutation + tmp_path; no ``monkeypatch`` fixture.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path

import pytest

from scitex_resource import get_machine_config, get_machine_name

ENV_KEY = "SCITEX_RESOURCE_MACHINE"
HOME_KEY = "HOME"


def _set_env(key: str, value: str | None):
    prior = os.environ.get(key)
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value
    return prior


def _restore(key: str, prior: str | None):
    if prior is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = prior


@pytest.fixture
def isolated_home(tmp_path):
    """Pin $HOME / $SCITEX_DIR to tmp_path and clear $SCITEX_RESOURCE_MACHINE."""
    # Arrange
    prior_env = _set_env(ENV_KEY, None)
    prior_home = _set_env(HOME_KEY, str(tmp_path))
    prior_scitex_dir = _set_env("SCITEX_DIR", str(tmp_path / ".scitex"))
    prior_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(prior_cwd)
        _restore("SCITEX_DIR", prior_scitex_dir)
        _restore(HOME_KEY, prior_home)
        _restore(ENV_KEY, prior_env)


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def test_falls_back_to_short_hostname_when_nothing_set(isolated_home):
    # Arrange
    expected = socket.gethostname().split(".", 1)[0]
    # Act
    name = get_machine_name()
    # Assert
    assert name == expected


def test_env_var_overrides_user_config(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: userfile\n",
    )
    prior = _set_env(ENV_KEY, "envname")
    try:
        # Act
        name = get_machine_name()
    finally:
        _restore(ENV_KEY, prior)
    # Assert
    assert name == "envname"


def test_user_config_returns_canonical_name_when_no_env(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-user\n",
    )
    # Act
    name = get_machine_name()
    # Assert
    assert name == "from-user"


def test_project_config_overrides_user_config(tmp_path):
    # Arrange
    home = tmp_path / "home"
    home.mkdir()
    project = tmp_path / "proj"
    _write_yaml(
        home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-user\n",
    )
    _write_yaml(
        project / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-project\n",
    )
    prior_env = _set_env(ENV_KEY, None)
    prior_home = _set_env(HOME_KEY, str(home))
    prior_cwd = os.getcwd()
    os.chdir(project)
    try:
        # Act
        name = get_machine_name()
    finally:
        os.chdir(prior_cwd)
        _restore(HOME_KEY, prior_home)
        _restore(ENV_KEY, prior_env)
    # Assert
    assert name == "from-project"


def test_get_machine_config_returns_canonical_name(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        """\
machine:
  canonical_name: spartan
  aliases:
    - spartan-login1.hpc.example.edu
  role: hpc-login
  hpc:
    cluster: spartan
    login_only: true
""",
    )
    # Act
    cfg = get_machine_config()
    # Assert
    assert cfg["canonical_name"] == "spartan"


def test_get_machine_config_returns_aliases_list(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        """\
machine:
  canonical_name: spartan
  aliases:
    - spartan-login1.hpc.example.edu
""",
    )
    # Act
    cfg = get_machine_config()
    # Assert
    assert "spartan-login1.hpc.example.edu" in cfg["aliases"]


def test_get_machine_config_returns_role(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: spartan\n  role: hpc-login\n",
    )
    # Act
    cfg = get_machine_config()
    # Assert
    assert cfg["role"] == "hpc-login"


def test_get_machine_config_returns_nested_hpc_block(isolated_home):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: spartan\n  hpc:\n    login_only: true\n",
    )
    # Act
    cfg = get_machine_config()
    # Assert
    assert cfg["hpc"]["login_only"] is True


def test_empty_config_returns_empty_dict(isolated_home):
    # Arrange
    # Act
    cfg = get_machine_config()
    # Assert
    assert cfg == {}


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_canonical_falls_through_to_hostname(isolated_home, value):
    # Arrange
    _write_yaml(
        isolated_home / ".scitex" / "resource" / "config.yaml",
        f"machine:\n  canonical_name: '{value}'\n",
    )
    expected = socket.gethostname().split(".", 1)[0]
    # Act
    name = get_machine_name()
    # Assert
    assert name == expected
