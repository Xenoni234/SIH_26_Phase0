"""Live simulation of the real trains around Vasai.

Seed: the real RailRadar station board for BSR (all trains serving Vasai).
Motion: each train's position is derived from its real scheduled departure at
BSR and its direction (source -> destination through Vasai). An internal sim
clock (accelerated by `sim_speed`) advances so motion is visible; the active
set is re-selected every tick as the clock moves. Near-zero API usage — the
board is fetched once and cached (respecting the 50/day free tier).

Output per active train is a small dict the frontend interpolates:
  {id, name, type, corridor, from_station, to_station, frac, status, ...}
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.adapters.railradar import RailRadarAdapter
from app.adapters.synthetic import SyntheticAdapter
from app.config import get_settings
from app.models.enums import TrainType
from app.topology.loader import Topology, get_topology

log = logging.getLogger("vasai.sim")

IST = timezone(timedelta(hours=5, minutes=30))

# Realistic cruising speeds by type (km/h) — used to map schedule offset -> km.
_SPEED_KMPH = {
    TrainType.EXPRESS.value: 65,
    TrainType.MEMU.value: 40,
    TrainType.LOCAL.value: 45,
    TrainType.PASSENGER.value: 40,
    TrainType.FREIGHT.value: 30,
    TrainType.YARD.value: 15,
}

# Station codes -> corridor for source/destination that sit off our modelled map
# (long-distance origins/terminals). Modelled stations are resolved from topology.
_FAR_CORRIDOR = {
    # North / Gujarat / North India (up line beyond Virar)
    "DRD": "north", "VR": "north", "VTN": "north", "BL": "north", "UDN": "north",
    "ST": "north", "ADI": "north", "BRC": "north", "NZM": "north", "ASR": "north",
    "JAM": "north", "OKHA": "north", "BME": "north", "RJT": "north", "PBR": "north",
    "BKN": "north", "HW": "north", "INDB": "north", "GIMB": "north", "SGNR": "north",
    # Mumbai / South / Konkan (Western/Mumbai side)
    "CCG": "western", "MMCT": "western", "BDTS": "western", "BA": "western",
    "DDR": "western", "ADH": "western", "BVI": "western", "PUNE": "western",
    "KOP": "western", "MAO": "western", "MRJ": "western", "ERS": "western",
    "TVCN": "western", "TVC": "western", "MAS": "western", "YPR": "western",
    "CBE": "western", "TEN": "western", "SWV": "western", "RN": "western",
    # Diva / Panvel / SE
    "DIVA": "diva", "PNVL": "diva", "BIRD": "diva", "KOPR": "diva", "DD": "diva",
    "PANVEL": "diva",
}


@dataclass
class _Corridor:
    key: str
    # stations sorted by km ascending (BSR at km 0 first)
    stations: list[tuple[str, float]]

    def max_km(self) -> float:
        return self.stations[-1][1] if self.stations else 0.0

    def locate(self, km: float) -> tuple[str, str, float]:
        """Return (from_station, to_station, frac) for a signed km along branch."""
        km = max(0.0, min(km, self.max_km()))
        for (a, ka), (b, kb) in zip(self.stations, self.stations[1:]):
            if ka <= km <= kb:
                span = (kb - ka) or 1.0
                return a, b, (km - ka) / span
        # beyond last station
        last = self.stations[-1][0]
        prev = self.stations[-2][0] if len(self.stations) > 1 else last
        return prev, last, 1.0


@dataclass
class SimTrain:
    number: str
    name: str
    ttype: str
    source_code: str
    dest_code: str
    dep_minute_of_day: int | None
    approach_corridor: str
    leave_corridor: str
    platform: int


@dataclass
class SimulationEngine:
    topo: Topology = field(default_factory=get_topology)

    def __post_init__(self) -> None:
        self.settings = get_settings()
        self.corridors: dict[str, _Corridor] = {}
        self._station_corridor: dict[str, str] = {}
        for key, cdef in self.topo.corridors.items():
            stations = sorted(
                [(s.code, float(s.km)) for s in cdef.stations], key=lambda x: x[1]
            )
            self.corridors[key] = _Corridor(key, stations)
            for code, _ in stations:
                self._station_corridor.setdefault(code, key)

        self._board: list[SimTrain] = []
        self._redis = None
        self.sim_now = datetime.now(IST)
        self._last_board_fetch = 0.0
        self.speed = float(self.settings.sim_speed)  # mutable at runtime

    def set_speed(self, value: float) -> float:
        self.speed = max(1.0, min(200.0, float(value)))
        return self.speed

    # ------------------------------------------------------------------ #
    def attach_redis(self, redis_client) -> None:
        self._redis = redis_client

    def seed(self) -> int:
        """Load (or reload) the real station board into SimTrains."""
        adapter = RailRadarAdapter(redis_client=self._redis)
        entries = adapter.get_station_board()
        if not entries:
            entries = self._synthetic_board()
        self._board = [self._to_sim_train(e) for e in entries if e.get("number")]
        log.info("Simulation seeded with %d trains from station board.", len(self._board))
        return len(self._board)

    def _synthetic_board(self) -> list[dict]:
        """Fallback board from the synthetic adapter when RailRadar is unavailable."""
        out = []
        for t in SyntheticAdapter(self.topo, seed=0).get_trains():
            out.append(
                {
                    "number": t.train_id,
                    "name": t.name,
                    "type": t.train_type.value,
                    "source_code": "VR",
                    "dest_code": t.destination or "CCG",
                    "departure": None,
                }
            )
        return out

    def _corridor_of(self, code: str) -> str:
        if code in self._station_corridor:
            return self._station_corridor[code]
        return _FAR_CORRIDOR.get(code, "western")

    def _to_sim_train(self, e: dict) -> SimTrain:
        ttype = e.get("type") or TrainType.PASSENGER.value
        src = e.get("source_code", "")
        dst = e.get("dest_code", "")
        return SimTrain(
            number=e["number"],
            name=e.get("name") or e["number"],
            ttype=ttype,
            source_code=src,
            dest_code=dst,
            dep_minute_of_day=_hhmm_to_min(e.get("departure")),
            approach_corridor=self._corridor_of(src),
            leave_corridor=self._corridor_of(dst),
            platform=_platform_for(ttype, e["number"]),
        )

    # ------------------------------------------------------------------ #
    def tick(self) -> None:
        self.sim_now += timedelta(seconds=self.settings.sim_tick_seconds * self.speed)

    def snapshot(self) -> dict:
        now = self.sim_now
        now_min = now.hour * 60 + now.minute + now.second / 60.0
        window = self.settings.sim_window_minutes

        active = []
        for st in self._board:
            if st.dep_minute_of_day is None:
                continue
            delta = _wrap_delta(st.dep_minute_of_day - now_min)  # +ve => before departure
            if abs(delta) > window:
                continue
            active.append((abs(delta), delta, st))

        active.sort(key=lambda x: x[0])
        active = active[: self.settings.sim_max_trains]

        trains = [self._position(delta, st) for _, delta, st in active]
        return {
            "type": "twin_tick",
            "sim_time": now.strftime("%H:%M:%S"),
            "sim_speed": self.speed,
            "count": len(trains),
            "trains": trains,
        }

    def _position(self, delta_min: float, st: SimTrain) -> dict:
        speed = _SPEED_KMPH.get(st.ttype, 40)
        km_out = abs(delta_min) * speed / 60.0

        at_platform = abs(delta_min) <= 1.0
        if delta_min > 0:
            corridor_key = st.approach_corridor      # still approaching from source side
            status = "approaching"
        else:
            corridor_key = st.leave_corridor         # departed towards destination
            status = "departed"
        if at_platform:
            status = "at_platform"

        corridor = self.corridors.get(corridor_key) or next(iter(self.corridors.values()))
        frm, to, frac = corridor.locate(0.0 if at_platform else km_out)

        return {
            "id": st.number,
            "name": st.name,
            "type": st.ttype,
            "corridor": corridor_key,
            "from_station": frm,
            "to_station": to,
            "frac": round(frac, 4),
            "km_from_bsr": round(km_out, 2),
            "status": status,
            "source": st.source_code,
            "destination": st.dest_code,
            "platform": st.platform,          # target platform (also while approaching)
            "at_platform": at_platform,
            "minutes_to_departure": round(delta_min, 1),
        }


# --------------------------------------------------------------------------- #
def _hhmm_to_min(hhmm: str | None) -> int | None:
    if not hhmm or ":" not in str(hhmm):
        return None
    try:
        h, m = str(hhmm).split(":")[:2]
        return int(h) * 60 + int(m)
    except ValueError:
        return None


def _wrap_delta(delta: float) -> float:
    """Wrap a minute delta into [-720, 720] so day-boundary trains behave."""
    while delta > 720:
        delta -= 1440
    while delta < -720:
        delta += 1440
    return delta


def _platform_for(ttype: str, number: str) -> int:
    if ttype == TrainType.MEMU.value:
        return 7 if int(number[-1] or 0) % 2 else 6      # PF6/PF7 are MEMU
    if ttype == TrainType.EXPRESS.value:
        return 6 if int(number[-1] or 0) % 2 else 7
    # locals on PF1–PF5 (slow/fast)
    return 1 + (sum(ord(c) for c in number) % 5)
