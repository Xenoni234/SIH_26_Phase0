"""SyntheticAdapter — the moving workhorse for the sim & ML training.

Spawns plausible trains on the Vasai corridors with realistic types, priorities
and delays. Deterministic when a seed is supplied (useful for tests/demos).
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.adapters.base import SourceAdapter
from app.models import TrainState
from app.models.enums import Corridor, Direction, TrainType
from app.topology.loader import Topology, get_topology

# A few real Vasai-relevant seeds (from the datasets) to make output recognizable.
_SEED_TRAINS = [
    ("12283", "Ernakulam - Nizamuddin Duronto", TrainType.EXPRESS, Corridor.NORTH),
    ("19019", "Bandra - Haridwar Express", TrainType.EXPRESS, Corridor.NORTH),
    ("93005", "Churchgate - Dahanu Road Fast Local", TrainType.LOCAL, Corridor.WESTERN),
    ("93002", "Dahanu Road - Churchgate Fast Local", TrainType.LOCAL, Corridor.WESTERN),
    ("94135", "Churchgate - Virar AC Fast Local", TrainType.LOCAL, Corridor.NORTH),
    ("61003", "Vasai Road - Diva MEMU", TrainType.MEMU, Corridor.DIVA),
    ("69168", "Vasai Road - Panvel MEMU", TrainType.MEMU, Corridor.DIVA),
    ("GOODS1", "BSR Goods", TrainType.FREIGHT, Corridor.DIVA),
]


class SyntheticAdapter(SourceAdapter):
    source_name = "synthetic"

    def __init__(self, topo: Topology | None = None, seed: int | None = None,
                 count: int | None = None):
        self.topo = topo or get_topology()
        self.rng = random.Random(seed)
        self.count = count

    def get_trains(self) -> list[TrainState]:
        now = datetime.utcnow()
        seeds = _SEED_TRAINS[: self.count] if self.count else _SEED_TRAINS
        trains: list[TrainState] = []

        for train_id, name, ttype, corridor in seeds:
            stations = self.topo.corridors[corridor.value].stations
            # place the train somewhere along its corridor
            idx = self.rng.randint(0, max(0, len(stations) - 2))
            cur, nxt = stations[idx], stations[idx + 1]
            direction = Direction.UP if self.rng.random() > 0.5 else Direction.DOWN

            ts = TrainState(
                train_id=train_id,
                name=name,
                train_type=ttype,
                corridor=corridor,
                direction=direction,
                current_station=cur.code,
                next_station=nxt.code,
                current_block=f"B-{cur.code}-{nxt.code}",
                platform=self.rng.choice([1, 2, 3, 4, 5, 6, 7]),
                speed_kmph=round(self.rng.uniform(0, 90), 1),
                delay_minutes=round(self.rng.choice([0, 0, 0, 3, 5, 8, 12]), 1),
                destination=stations[-1].code,
                eta=now + timedelta(minutes=self.rng.randint(5, 90)),
                source=self.source_name,
                observed_at=now,
            )
            ts.priority = ts.default_priority_for_type()
            trains.append(ts)

        return trains
