"""DelayState — a train's delay and (later) predicted propagation."""
from __future__ import annotations

from pydantic import BaseModel, Field


class DelayState(BaseModel):
    train_id: str
    current_delay_min: float = 0.0
    at_station: str | None = None
    predicted_delay_min: float | None = Field(
        None, description="Filled by the prediction layer (Phase 3)"
    )
