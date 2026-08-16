"""SourceAdapter ABC + a small registry/factory."""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import TrainState


class SourceAdapter(ABC):
    """Base class for all data sources.

    Implementations translate a specific external feed into normalized
    TrainState objects. They must never expose source-specific payloads.
    """

    #: unique key used in the API path /adapters/{source}/trains
    source_name: str = "base"

    @abstractmethod
    def get_trains(self) -> list[TrainState]:
        """Return the current set of trains as normalized TrainState."""
        raise NotImplementedError


def get_adapter(source: str):
    """Factory: resolve an adapter by name. Imports locally to avoid cycles."""
    from app.adapters.railradar import RailRadarAdapter
    from app.adapters.synthetic import SyntheticAdapter

    source = source.lower()
    if source == SyntheticAdapter.source_name:
        return SyntheticAdapter()
    if source == RailRadarAdapter.source_name:
        return RailRadarAdapter()
    raise KeyError(f"Unknown adapter source: {source!r}")
