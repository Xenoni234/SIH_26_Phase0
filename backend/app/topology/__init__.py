"""Topology: load the canonical Vasai YAML into a validated NetworkX graph."""
from app.topology.loader import Topology, load_topology
from app.topology.graph import build_graph

__all__ = ["Topology", "load_topology", "build_graph"]
