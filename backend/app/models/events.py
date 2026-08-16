"""StationEvent — a discrete operational event (arrival, departure, etc.)."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventKind(str, Enum):
    ARRIVAL = "arrival"
    DEPARTURE = "departure"
    ENTER_BLOCK = "enter_block"
    EXIT_BLOCK = "exit_block"
    ROUTE_SET = "route_set"
    ROUTE_RELEASE = "route_release"
    PLATFORM_OCCUPY = "platform_occupy"
    PLATFORM_RELEASE = "platform_release"
    RUN_THROUGH = "run_through"


class StationEvent(BaseModel):
    event_id: str | None = None
    kind: EventKind
    train_id: str
    station: str | None = None
    block_id: str | None = None
    platform: int | None = None
    at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "synthetic"
