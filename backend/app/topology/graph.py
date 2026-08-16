"""Build the Vasai railway graph G=(V,E) with NetworkX.

Nodes: stations, junctions, platforms, yard, freight.
Edges: track/movement connections (station-station blocks, platform links,
junction throats, yard/freight attachments).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from app.topology.loader import Topology


def build_graph(topo: "Topology") -> nx.Graph:
    g = nx.Graph()

    # --- Station nodes ---
    for code, st in topo.stations().items():
        g.add_node(
            code,
            kind="station",
            name=st.name,
            corridor=st.corridor.value,
            km=st.km,
        )

    # --- Block edges (station <-> station) ---
    for blk in topo.blocks:
        g.add_edge(
            blk.from_station,
            blk.to_station,
            kind="block",
            block_id=blk.block_id,
            corridor=blk.corridor.value,
            length_km=blk.length_km,
        )

    # --- Platform nodes, linked to the junction station ---
    for pf in topo.platforms:
        g.add_node(
            pf.id,
            kind="platform",
            number=pf.number,
            station=topo.junction_code,
            serves=pf.serves,
        )
        g.add_edge(topo.junction_code, pf.id, kind="platform_link")

    # --- Junction (throat) nodes ---
    for j in topo.junctions:
        g.add_node(j.id, kind="junction", name=j.name, connects=j.connects)
        g.add_edge(topo.junction_code, j.id, kind="throat")

    # --- Yard + freight as operational-resource nodes ---
    if topo.yard:
        g.add_node(
            topo.yard["id"],
            kind="yard",
            name=topo.yard.get("name"),
            parallel_to=topo.yard.get("parallel_to"),
        )
        g.add_edge(topo.junction_code, topo.yard["id"], kind="yard_link")
    if topo.freight:
        g.add_node(
            topo.freight["id"],
            kind="freight",
            name=topo.freight.get("name"),
            corridor=topo.freight.get("associated_corridor"),
        )
        g.add_edge(topo.junction_code, topo.freight["id"], kind="freight_link")

    return g


def graph_summary(g: nx.Graph) -> dict:
    """Compact counts for /twin and tests."""
    kinds: dict[str, int] = {}
    for _, data in g.nodes(data=True):
        kinds[data.get("kind", "?")] = kinds.get(data.get("kind", "?"), 0) + 1
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "node_kinds": kinds,
    }


def to_json(g: nx.Graph) -> dict:
    """Serialize the graph for the API (nodes + edges)."""
    return {
        "nodes": [{"id": n, **d} for n, d in g.nodes(data=True)],
        "edges": [{"source": u, "target": v, **d} for u, v, d in g.edges(data=True)],
    }
