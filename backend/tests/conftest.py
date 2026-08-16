"""Shared test fixtures. Resolves the topology YAML across local + container layouts."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve()

# Candidate locations, first existing wins:
#  1) explicit env var (set in Docker), 2) repo-root/data (local checkout),
#  3) container mount at /app/data.
_CANDIDATES = [
    os.environ.get("TOPOLOGY_PATH"),
    str(_HERE.parents[2] / "data" / "topology" / "vasai.yaml"),  # repo root
    "/app/data/topology/vasai.yaml",                              # container
]


def _resolve() -> str:
    for c in _CANDIDATES:
        if c and Path(c).exists():
            return c
    raise FileNotFoundError(f"vasai.yaml not found in any of: {_CANDIDATES}")


_TOPOLOGY = _resolve()
os.environ["TOPOLOGY_PATH"] = _TOPOLOGY  # make app + fixture agree


@pytest.fixture(scope="session")
def topology_path() -> str:
    return _TOPOLOGY
