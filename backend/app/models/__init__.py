"""Normalized domain contracts (Pydantic v2).

These are the source-agnostic types every adapter emits and the Digital Twin
consumes. Nothing source-specific (RailRadar JSON, RTIS payloads) may leak past
the adapter layer — it must be mapped into these types first.
"""
from app.models.enums import (
    Corridor,
    Direction,
    OccupancyStatus,
    SignalAspect,
    TrainType,
)
from app.models.train import TrainState
from app.models.track import TrackState
from app.models.block import BlockState
from app.models.platform import PlatformState
from app.models.signal import SignalState
from app.models.route import RouteState
from app.models.junction import JunctionState
from app.models.events import StationEvent
from app.models.delay import DelayState

__all__ = [
    "Corridor",
    "Direction",
    "OccupancyStatus",
    "SignalAspect",
    "TrainType",
    "TrainState",
    "TrackState",
    "BlockState",
    "PlatformState",
    "SignalState",
    "RouteState",
    "JunctionState",
    "StationEvent",
    "DelayState",
]
