"""Seed builder is a pure transform — testable without a database."""
from __future__ import annotations

from app.seed import build_seed_rows
from app.topology.loader import load_topology


def test_build_seed_rows_shapes(topology_path):
    topo = load_topology(topology_path)
    rows = build_seed_rows(topo)

    assert {"stations", "platforms", "blocks", "junctions", "signals", "trains"} <= set(rows)
    # 7 platforms at BSR (confirmed by dataset).
    assert len(rows["platforms"]) == 7
    # Every station row carries a corridor + km.
    for st in rows["stations"]:
        assert st["code"] and st["corridor"] and "km_from_bsr" in st
    # Blocks reference real stations.
    ids = {b["id"] for b in rows["blocks"]}
    assert "B-BSR-NIG" in ids
    # Trains carry a normalized type + priority.
    assert len(rows["trains"]) >= 5
    for t in rows["trains"]:
        assert t["train_id"] and t["train_type"] and 1 <= t["priority"] <= 10


def test_seed_rows_are_deterministic(topology_path):
    topo = load_topology(topology_path)
    a = build_seed_rows(topo)["trains"]
    b = build_seed_rows(topo)["trains"]
    assert [t["train_id"] for t in a] == [t["train_id"] for t in b]
