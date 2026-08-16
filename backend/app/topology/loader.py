"""Load and validate the canonical Vasai topology YAML.

The YAML in data/topology/vasai.yaml is the single source of truth. This module
parses it into validated Pydantic structures and derives blocks between
consecutive stations, then hands off to graph.build_graph().
"""
from __future__ import annotations

import functools
from pathlib import Path

import networkx as nx
import yaml
from pydantic import BaseModel, Field

from app.config import get_settings
from app.models.enums import Corridor


# --------------------------------------------------------------------------- #
# Validated views of the YAML                                                 #
# --------------------------------------------------------------------------- #
class StationNode(BaseModel):
    code: str
    name: str
    km: float
    corridor: Corridor


class PlatformDef(BaseModel):
    id: str
    number: int
    length_m: int | None = None
    serves: list[str] = Field(default_factory=list)


class CorridorDef(BaseModel):
    key: Corridor
    name: str
    direction: str
    tracks: int = 2
    stations: list[StationNode]


class BlockDef(BaseModel):
    block_id: str
    corridor: Corridor
    from_station: str
    to_station: str
    length_km: float


class JunctionDef(BaseModel):
    id: str
    name: str
    connects: list[str] = Field(default_factory=list)


class Topology(BaseModel):
    """Fully validated topology plus a derived NetworkX graph."""

    junction_code: str
    junction_name: str
    platforms: list[PlatformDef]
    corridors: dict[str, CorridorDef]
    blocks: list[BlockDef]
    junctions: list[JunctionDef]
    yard: dict
    freight: dict
    signals: list[dict]
    defaults: dict

    # networkx graph is attached after construction (not a pydantic field)
    model_config = {"arbitrary_types_allowed": True}

    def stations(self) -> dict[str, StationNode]:
        out: dict[str, StationNode] = {}
        for corr in self.corridors.values():
            for st in corr.stations:
                out.setdefault(st.code, st)
        return out


def _derive_blocks(corridors: dict[str, CorridorDef]) -> list[BlockDef]:
    """One block between each pair of consecutive stations on a corridor."""
    blocks: list[BlockDef] = []
    for key, corr in corridors.items():
        stations = corr.stations
        for a, b in zip(stations, stations[1:]):
            length = abs(b.km - a.km)
            blocks.append(
                BlockDef(
                    block_id=f"B-{a.code}-{b.code}",
                    corridor=corr.key,
                    from_station=a.code,
                    to_station=b.code,
                    length_km=length,
                )
            )
    return blocks


def _parse(raw: dict) -> Topology:
    meta = raw["meta"]["junction"]

    corridors: dict[str, CorridorDef] = {}
    for key, cdef in raw["corridors"].items():
        corr_enum = Corridor(key)
        stations = [
            StationNode(code=s["code"], name=s["name"], km=s["km"], corridor=corr_enum)
            for s in cdef["stations"]
        ]
        corridors[key] = CorridorDef(
            key=corr_enum,
            name=cdef["name"],
            direction=cdef["direction"],
            tracks=cdef.get("tracks", 2),
            stations=stations,
        )

    platforms = [PlatformDef(**p) for p in raw["platforms"]]
    junctions = [JunctionDef(**j) for j in raw["junctions"]]
    blocks = _derive_blocks(corridors)

    return Topology(
        junction_code=meta["code"],
        junction_name=meta["name"],
        platforms=platforms,
        corridors=corridors,
        blocks=blocks,
        junctions=junctions,
        yard=raw.get("yard", {}),
        freight=raw.get("freight", {}),
        signals=raw.get("signals", []),
        defaults=raw.get("defaults", {}),
    )


def load_topology(path: str | Path | None = None) -> Topology:
    """Parse + validate the topology YAML and attach its NetworkX graph."""
    from app.topology.graph import build_graph  # local import avoids cycle

    path = Path(path or get_settings().topology_path)
    if not path.exists():
        raise FileNotFoundError(f"Topology file not found: {path}")

    raw = yaml.safe_load(path.read_text())
    topo = _parse(raw)
    topo_graph = build_graph(topo)
    # Attach as a plain attribute (excluded from serialization).
    object.__setattr__(topo, "_graph", topo_graph)
    return topo


@functools.lru_cache
def get_topology() -> Topology:
    """Cached singleton used by the app + API layer."""
    return load_topology()


def graph_of(topo: Topology) -> nx.Graph:
    return getattr(topo, "_graph")
