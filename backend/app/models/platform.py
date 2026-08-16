"""PlatformState — a platform at a station (P1–P7 at BSR)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import Corridor, OccupancyStatus


class PlatformState(BaseModel):
    platform_id: str
    station: str
    number: int
    length_m: int | None = None
    serves: list[Corridor] = Field(default_factory=list)
    status: OccupancyStatus = OccupancyStatus.FREE
    occupied_by: str | None = Field(None, description="train_id if occupied")
