"""TrainState — the central normalized train entity every adapter emits."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import Corridor, Direction, TrainType


class TrainState(BaseModel):
    """A single train's operational state at a point in time.

    Source-agnostic: RailRadar, synthetic, RTIS (future) all map into this.
    """

    train_id: str = Field(..., description="Train number, e.g. '12283'")
    name: str | None = None
    train_type: TrainType

    # Location
    corridor: Corridor | None = None
    direction: Direction | None = None
    current_station: str | None = Field(None, description="Station code, e.g. 'BSR'")
    next_station: str | None = None
    current_block: str | None = None
    platform: int | None = None
    lat: float | None = None
    lon: float | None = None

    # Kinematics / schedule
    speed_kmph: float | None = None
    delay_minutes: float = 0.0
    priority: int = Field(5, ge=1, le=10, description="1=highest, 10=lowest")
    destination: str | None = None
    eta: datetime | None = None

    # Provenance
    source: str = Field(..., description="Adapter that produced this state")
    observed_at: datetime = Field(default_factory=datetime.utcnow)

    def default_priority_for_type(self) -> int:
        return {
            TrainType.EXPRESS: 2,
            TrainType.MEMU: 5,
            TrainType.PASSENGER: 5,
            TrainType.LOCAL: 6,
            TrainType.FREIGHT: 8,
            TrainType.YARD: 9,
        }.get(self.train_type, 5)
