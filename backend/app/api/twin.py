"""Twin endpoint — the Vasai graph + current trains."""
from __future__ import annotations

from fastapi import APIRouter

from app.adapters import SyntheticAdapter
from app.topology.graph import graph_summary, to_json
from app.topology.loader import get_topology, graph_of

router = APIRouter(tags=["twin"])


@router.get("/twin")
def get_twin() -> dict:
    topo = get_topology()
    g = graph_of(topo)
    trains = SyntheticAdapter(topo).get_trains()
    return {
        "junction": {"code": topo.junction_code, "name": topo.junction_name},
        "summary": graph_summary(g),
        "graph": to_json(g),
        "trains": [t.model_dump(mode="json") for t in trains],
    }


@router.get("/twin/summary")
def get_twin_summary() -> dict:
    topo = get_topology()
    return {
        "junction": topo.junction_code,
        "platforms": len(topo.platforms),
        "corridors": {k: len(c.stations) for k, c in topo.corridors.items()},
        "blocks": len(topo.blocks),
        "graph": graph_summary(graph_of(topo)),
    }
