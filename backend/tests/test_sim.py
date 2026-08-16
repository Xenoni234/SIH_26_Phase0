"""Simulation engine: seeds from a board and produces interpolatable positions."""
from __future__ import annotations

from datetime import datetime

from app.simulation.engine import IST, SimulationEngine, _wrap_delta
from app.topology.loader import load_topology


def _engine(topology_path) -> SimulationEngine:
    return SimulationEngine(topo=load_topology(topology_path))


def test_seed_from_fixture_board(topology_path):
    eng = _engine(topology_path)
    n = eng.seed()  # no key in tests -> fixture board
    assert n >= 3
    numbers = {st.number for st in eng._board}
    assert {"91018", "93005", "61003"} <= numbers


def test_snapshot_positions_are_on_the_graph(topology_path):
    eng = _engine(topology_path)
    eng.seed()
    # Fixture departures cluster around 00:0x — put the sim clock there.
    eng.sim_now = datetime(2026, 8, 16, 0, 5, 0, tzinfo=IST)
    snap = eng.snapshot()

    assert snap["type"] == "twin_tick"
    assert snap["count"] >= 1
    for t in snap["trains"]:
        assert t["from_station"] and t["to_station"]
        assert 0.0 <= t["frac"] <= 1.0
        assert t["corridor"] in {"north", "western", "diva"}
        assert t["status"] in {"approaching", "departed", "at_platform"}


def test_memu_uses_diva_corridor(topology_path):
    eng = _engine(topology_path)
    eng.seed()
    eng.sim_now = datetime(2026, 8, 16, 0, 10, 0, tzinfo=IST)
    snap = eng.snapshot()
    memu = [t for t in snap["trains"] if t["id"] == "61003"]
    assert memu and memu[0]["corridor"] == "diva"


def test_wrap_delta():
    assert _wrap_delta(1430) == -10   # ~23:50 next-day wraps to -10 min
    assert _wrap_delta(-1430) == 10
