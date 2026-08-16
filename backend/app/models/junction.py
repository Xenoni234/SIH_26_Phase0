"""JunctionState — a crossing point where corridors compete."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import Corridor


class JunctionState(BaseModel):
    junction_id: str
    name: str
    connects: list[Corridor] = Field(default_factory=list)
    occupied_by: str | None = Field(None, description="train_id crossing, if any")
