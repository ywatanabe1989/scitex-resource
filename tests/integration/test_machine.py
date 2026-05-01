"""Tests for ``scitex_resource._machine`` — canonical machine identity.

Resolution cascade contract — verify env > project > user > hostname.
Other scitex-* packages depend on this ordering staying stable.
"""

from __future__ import annotations

import socket
from pathlib import Path

import pytest

from scitex_resource import get_machine_config, get_machine_name


def _write_yaml(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def test_falls_back_to_short_hostname(monkeypatch, tmp_path):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    name = get_machine_name()
    assert name == socket.gethostname().split(".", 1)[0]
    assert name


def test_env_var_overrides_everything(monkeypatch, tmp_path):
    monkeypatch.setenv("SCITEX_RESOURCE_MACHINE", "envname")
    monkeypatch.setenv("HOME", str(tmp_path))
    _write_yaml(
        tmp_path / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: userfile\n",
    )
    assert get_machine_name() == "envname"


def test_user_config_used_when_no_env(monkeypatch, tmp_path):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    _write_yaml(
        tmp_path / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-user\n",
    )
    assert get_machine_name() == "from-user"


def test_project_config_overrides_user(monkeypatch, tmp_path):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    project = tmp_path / "proj"
    _write_yaml(
        home / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-user\n",
    )
    _write_yaml(
        project / ".scitex" / "resource" / "config.yaml",
        "machine:\n  canonical_name: from-project\n",
    )
    monkeypatch.chdir(project)
    assert get_machine_name() == "from-project"


def test_get_machine_config_returns_full_block(monkeypatch, tmp_path):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    _write_yaml(
        tmp_path / ".scitex" / "resource" / "config.yaml",
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
    cfg = get_machine_config()
    assert cfg["canonical_name"] == "spartan"
    assert "spartan-login1.hpc.example.edu" in cfg["aliases"]
    assert cfg["role"] == "hpc-login"
    assert cfg["hpc"]["login_only"] is True


def test_empty_config_returns_empty_dict(monkeypatch, tmp_path):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    assert get_machine_config() == {}


@pytest.mark.parametrize("value", ["", "   "])
def test_blank_canonical_falls_through_to_hostname(monkeypatch, tmp_path, value):
    monkeypatch.delenv("SCITEX_RESOURCE_MACHINE", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    _write_yaml(
        tmp_path / ".scitex" / "resource" / "config.yaml",
        f"machine:\n  canonical_name: '{value}'\n",
    )
    assert get_machine_name() == socket.gethostname().split(".", 1)[0]
