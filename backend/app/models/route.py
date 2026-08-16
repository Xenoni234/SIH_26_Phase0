"""RouteState — a set path through the junction for a train."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import OccupancyStatus


class RouteState(BaseModel):
    route_id: str
    from_node: str
    to_node: str
    path: list[str] = Field(default_factory=list, description="ordered node ids")
    status: OccupancyStatus = OccupancyStatus.FREE
    set_for: str | None = Field(None, description="train_id the route is set for")
