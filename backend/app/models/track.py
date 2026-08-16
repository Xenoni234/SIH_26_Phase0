"""TrackState — a running line between two points on a corridor."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import Corridor, OccupancyStatus


class TrackState(BaseModel):
    track_id: str
    corridor: Corridor
    from_node: str
    to_node: str
    length_km: float | None = None
    status: OccupancyStatus = OccupancyStatus.FREE
    occupied_by: str | None = Field(None, description="train_id if occupied")
