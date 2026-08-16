"""Adapters produce well-formed, normalized TrainState objects."""
from __future__ import annotations

from app.adapters.railradar import RailRadarAdapter
from app.adapters.synthetic import SyntheticAdapter
from app.models import TrainState
from app.models.enums import TrainType
from app.topology.loader import load_topology


def test_synthetic_adapter_normalizes(topology_path):
    topo = load_topology(topology_path)
    trains = SyntheticAdapter(topo, seed=42).get_trains()
    assert len(trains) >= 5
    for t in trains:
        assert isinstance(t, TrainState)
        assert t.source == "synthetic"
        assert t.train_id
        assert 1 <= t.priority <= 10


def test_synthetic_is_deterministic_with_seed(topology_path):
    topo = load_topology(topology_path)
    a = SyntheticAdapter(topo, seed=7).get_trains()
    b = SyntheticAdapter(topo, seed=7).get_trains()
    assert [t.platform for t in a] == [t.platform for t in b]


def test_railradar_fixture_fallback(monkeypatch):
    # No API key -> fixture mode. Normalization must yield valid TrainState.
    monkeypatch.setenv("RAILRADAR_API_KEY", "")
    adapter = RailRadarAdapter()
    trains = adapter.get_trains()
    assert len(trains) >= 1
    ids = {t.train_id for t in trains}
    assert "12283" in ids  # from railradar_12283.json
    express = next(t for t in trains if t.train_id == "12283")
    assert express.train_type == TrainType.EXPRESS
    assert express.source == "railradar"
    assert express.current_station == "BSR"


def test_railradar_type_and_corridor_inference():
    ts = RailRadarAdapter._normalize(
        "93005",
        {"trainName": "Churchgate - Dahanu Road Fast Local", "toStationCode": "DRD"},
    )
    assert ts.train_type == TrainType.LOCAL
    # DRD is on the North/Virar up-line in our corridor mapping.
    assert ts.corridor is not None
