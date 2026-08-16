"""BlockState — the safety unit of movement (one train at a time)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import Corridor, OccupancyStatus


class BlockState(BaseModel):
    block_id: str
    corridor: Corridor
    from_station: str
    to_station: str
    length_km: float | None = None
    status: OccupancyStatus = OccupancyStatus.FREE
    occupied_by: str | None = Field(None, description="train_id if occupied")
    headway_seconds: int = 120
