"""RailRadarAdapter — external prototype live-data source (NOT RTIS).

Rules baked in:
  * Bearer auth with the key from settings (never logged/committed).
  * Responses cached in Redis (TTL) to respect the free tier (50 req/day, 10/min)
    — we never hot-poll.
  * Falls back to recorded JSON fixtures when no API key is configured, so the
    demo and tests run fully offline.

The live response schema is not fully documented, so `_normalize` maps
defensively across the likely field names and always produces a TrainState.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from app.adapters.base import SourceAdapter
from app.config import get_settings
from app.models import TrainState
from app.models.enums import Corridor, TrainType

log = logging.getLogger(__name__)
_FIXTURE_DIR = Path(__file__).parent / "fixtures"


class RailRadarAdapter(SourceAdapter):
    source_name = "railradar"

    def __init__(self, redis_client=None, http_client: httpx.Client | None = None):
        self.settings = get_settings()
        self._redis = redis_client  # optional; injected in app lifespan
        self._http = http_client

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def get_trains(self) -> list[TrainState]:
        if not self.settings.railradar_enabled:
            log.info("RailRadar key absent — using recorded fixtures.")
            return self._from_fixtures()

        trains: list[TrainState] = []
        for number in self.settings.railradar_train_list:
            payload = self._fetch_live(number)
            if payload:
                trains.append(self._normalize(number, payload))
        if not trains:
            log.warning("RailRadar returned nothing — falling back to fixtures.")
            return self._from_fixtures()
        return trains

    # ------------------------------------------------------------------ #
    # Station board — ALL trains serving Vasai (one request, cached)      #
    # ------------------------------------------------------------------ #
    def get_station_board(self, code: str | None = None) -> list[dict]:
        """Return every train serving the station as normalized board entries.

        Uses GET /stations/{code}/trains. Cached in Redis for `board_ttl` so we
        never exceed the 50/day free tier. Falls back to the board fixture when
        no key is set. Real response shape:
            {success, data:{station, trains:[{train:{number,name,type,source,
             destination,runDays}, stop:{sequence,arrival,departure,arrivalDay,
             departureDay,distance,stopType}}]}}
        """
        code = code or self.settings.railradar_station_code
        payload = self._fetch_station_board(code)
        if not payload:
            payload = self._board_fixture()
        return self._normalize_board(payload)

    def _fetch_station_board(self, code: str) -> dict | None:
        if not self.settings.railradar_enabled:
            return None
        cache_key = f"railradar:board:{code}"
        if self._redis is not None:
            cached = self._redis.get(cache_key)
            if cached:
                return json.loads(cached)

        url = f"{self.settings.railradar_base_url}/stations/{code}/trains"
        headers = {"Authorization": f"Bearer {self.settings.railradar_api_key}"}
        try:
            client = self._http or httpx.Client(timeout=15.0)
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            log.warning("RailRadar station board fetch failed for %s: %s", code, exc)
            return None

        if self._redis is not None:
            self._redis.setex(cache_key, self.settings.railradar_board_ttl, json.dumps(data))
        return data

    def _board_fixture(self) -> dict:
        fp = _FIXTURE_DIR / "railradar_board_BSR.json"
        if fp.exists():
            return json.loads(fp.read_text())
        return {"data": {"trains": []}}

    @classmethod
    def _normalize_board(cls, payload: dict) -> list[dict]:
        data = payload.get("data", payload)
        entries = data.get("trains", []) if isinstance(data, dict) else []
        out: list[dict] = []
        for item in entries:
            tr = item.get("train", {})
            stop = item.get("stop", {})
            number = str(tr.get("number", "")).strip()
            if not number:
                continue
            src = (tr.get("source") or {})
            dst = (tr.get("destination") or {})
            out.append(
                {
                    "number": number,
                    "name": tr.get("name"),
                    "type": _map_board_type(tr.get("type"), tr.get("name") or "", number),
                    "source_code": (src.get("code") or "").upper(),
                    "dest_code": (dst.get("code") or "").upper(),
                    "arrival": stop.get("arrival"),
                    "departure": stop.get("departure"),
                    "arrival_day": stop.get("arrivalDay"),
                    "departure_day": stop.get("departureDay"),
                    "distance": stop.get("distance"),
                    "stop_type": stop.get("stopType"),
                    "run_days": tr.get("runDays") or [],
                }
            )
        return out

    # ------------------------------------------------------------------ #
    # Live fetch (cached)                                                #
    # ------------------------------------------------------------------ #
    def _fetch_live(self, number: str) -> dict | None:
        cache_key = f"railradar:live:{number}"
        if self._redis is not None:
            cached = self._redis.get(cache_key)
            if cached:
                return json.loads(cached)

        url = f"{self.settings.railradar_base_url}/trains/{number}/live"
        headers = {"Authorization": f"Bearer {self.settings.railradar_api_key}"}
        try:
            client = self._http or httpx.Client(timeout=10.0)
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # network/quota/parse — degrade gracefully
            log.warning("RailRadar fetch failed for %s: %s", number, exc)
            return None

        if self._redis is not None:
            self._redis.setex(
                cache_key, self.settings.railradar_cache_ttl, json.dumps(data)
            )
        return data

    # ------------------------------------------------------------------ #
    # Fixtures (offline)                                                 #
    # ------------------------------------------------------------------ #
    def _from_fixtures(self) -> list[TrainState]:
        out: list[TrainState] = []
        for fp in sorted(_FIXTURE_DIR.glob("railradar_*.json")):
            raw = json.loads(fp.read_text())
            number = raw.get("trainNumber") or fp.stem.replace("railradar_", "")
            out.append(self._normalize(str(number), raw))
        return out

    # ------------------------------------------------------------------ #
    # Normalization (defensive across likely schemas)                    #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _pick(d: dict, *keys, default=None):
        for k in keys:
            if k in d and d[k] is not None:
                return d[k]
        # also check a nested "data" envelope
        data = d.get("data") if isinstance(d.get("data"), dict) else {}
        for k in keys:
            if k in data and data[k] is not None:
                return data[k]
        return default

    @classmethod
    def _normalize(cls, number: str, raw: dict) -> TrainState:
        name = cls._pick(raw, "trainName", "name")
        ttype = _guess_type(name or "", number)
        corridor = _guess_corridor(cls._pick(raw, "toStationCode", "destination", default=""))

        eta_raw = cls._pick(raw, "eta", "expectedArrival")
        eta = _parse_dt(eta_raw)

        ts = TrainState(
            train_id=str(number),
            name=name,
            train_type=ttype,
            corridor=corridor,
            current_station=cls._pick(raw, "currentStationCode", "currentStation", "lastStation"),
            next_station=cls._pick(raw, "nextStationCode", "nextStation"),
            platform=_as_int(cls._pick(raw, "platform", "pf")),
            lat=_as_float(cls._pick(raw, "latitude", "lat")),
            lon=_as_float(cls._pick(raw, "longitude", "lng", "lon")),
            speed_kmph=_as_float(cls._pick(raw, "speed", "currentSpeed")),
            delay_minutes=_as_float(cls._pick(raw, "delay", "delayMinutes", default=0)) or 0.0,
            destination=cls._pick(raw, "toStationCode", "destination"),
            eta=eta,
            source=cls.source_name,
            observed_at=datetime.utcnow(),
        )
        ts.priority = ts.default_priority_for_type()
        return ts


# --------------------------------------------------------------------------- #
# small helpers                                                               #
# --------------------------------------------------------------------------- #
def _as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _as_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _parse_dt(v):
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def _map_board_type(api_type: str | None, name: str, number: str) -> str:
    """Map RailRadar board `type` (EMU/MEMU/Exp/SF/...) to our TrainType value."""
    t = (api_type or "").upper()
    if t == "MEMU" or number.startswith(("61", "69")):
        return TrainType.MEMU.value
    if t in {"EMU", "LOCAL"} or number.startswith(("90", "91", "92", "93", "94")):
        return TrainType.LOCAL.value
    if t in {"EXP", "SF", "SUF", "MAIL", "EXPRESS", "DRNT", "DURONTO", "HUMSAFAR",
             "RAJDHANI", "GARIBRATH", "SKR"}:
        return TrainType.EXPRESS.value
    if "GOODS" in name.upper() or "FREIGHT" in name.upper():
        return TrainType.FREIGHT.value
    return _guess_type(name, number).value


def _guess_type(name: str, number: str) -> TrainType:
    n = name.lower()
    if number.startswith(("90", "91", "92", "93", "94")):
        return TrainType.LOCAL
    if number.startswith(("61", "69")) or "memu" in n:
        return TrainType.MEMU
    if any(k in n for k in ("duronto", "express", "superfast", "humsafar", "sf", "exp")):
        return TrainType.EXPRESS
    if "goods" in n or "freight" in n:
        return TrainType.FREIGHT
    return TrainType.PASSENGER


def _guess_corridor(dest_code: str) -> Corridor | None:
    dest = (dest_code or "").upper()
    if dest in {"VR", "NSP", "VTN", "DRD"}:
        return Corridor.NORTH
    if dest in {"CCG", "ADH", "BA", "DDR", "BVI", "MIRA", "BYR", "NIG", "BDTS", "MMCT"}:
        return Corridor.WESTERN
    if dest in {"DIVA", "PNVL", "KOPR"}:
        return Corridor.DIVA
    return None
