"""Topology loads into a valid NetworkX graph matching the canonical map."""
from __future__ import annotations

import networkx as nx

from app.topology.graph import graph_summary
from app.topology.loader import graph_of, load_topology


def test_topology_loads(topology_path):
    topo = load_topology(topology_path)
    assert topo.junction_code == "BSR"
    # Confirmed by the real dataset: 7 platforms.
    assert len(topo.platforms) == 7


def test_corridors_present(topology_path):
    topo = load_topology(topology_path)
    assert set(topo.corridors) == {"north", "western", "diva"}
    # Western corridor starts at BSR and ends at Churchgate.
    western = topo.corridors["western"].stations
    assert western[0].code == "BSR"
    assert western[-1].code == "CCG"


def test_blocks_derived(topology_path):
    topo = load_topology(topology_path)
    # One block per consecutive station pair across all corridors.
    assert len(topo.blocks) > 0
    ids = {b.block_id for b in topo.blocks}
    assert "B-BSR-NIG" in ids  # Vasai -> Naigaon (western)


def test_graph_is_connected_and_typed(topology_path):
    topo = load_topology(topology_path)
    g = graph_of(topo)
    assert isinstance(g, nx.Graph)
    summary = graph_summary(g)
    kinds = summary["node_kinds"]
    assert kinds["station"] >= 10
    assert kinds["platform"] == 7
    assert kinds.get("yard") == 1
    assert kinds.get("freight") == 1
    # BSR must connect to its platforms + throats + yard + freight.
    assert g.degree["BSR"] >= 7


def test_yard_parallel_to_north_and_freight_on_diva(topology_path):
    topo = load_topology(topology_path)
    assert topo.yard["parallel_to"] == "north"
    assert topo.freight["associated_corridor"] == "diva"
