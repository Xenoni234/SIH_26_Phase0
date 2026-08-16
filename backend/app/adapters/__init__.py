"""Source-agnostic adapters. Each maps an external feed → list[TrainState].

Guardrail: nothing source-specific may leave this package. Downstream code only
ever sees normalized TrainState objects.
"""
from app.adapters.base import SourceAdapter, get_adapter
from app.adapters.railradar import RailRadarAdapter
from app.adapters.synthetic import SyntheticAdapter

__all__ = ["SourceAdapter", "get_adapter", "RailRadarAdapter", "SyntheticAdapter"]
