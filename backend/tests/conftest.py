"""Shared test fixtures. Points settings at the repo's real topology YAML."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# Resolve the topology file relative to the repo (works outside Docker too).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOPOLOGY = _REPO_ROOT / "data" / "topology" / "vasai.yaml"
os.environ.setdefault("TOPOLOGY_PATH", str(_TOPOLOGY))


@pytest.fixture(scope="session")
def topology_path() -> str:
    return str(_TOPOLOGY)
