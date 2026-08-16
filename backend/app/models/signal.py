"""SignalState — signal aspect at a junction/throat."""
from __future__ import annotations

from pydantic import BaseModel

from app.models.enums import SignalAspect


class SignalState(BaseModel):
    signal_id: str
    at_node: str
    kind: str = "home"  # home | starter | distant
    aspect: SignalAspect = SignalAspect.RED
