"""Adapters endpoint — demonstrates source-agnostic normalization."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.adapters.base import get_adapter
from app.adapters.railradar import RailRadarAdapter

router = APIRouter(tags=["adapters"], prefix="/adapters")


@router.get("/{source}/trains")
def adapter_trains(source: str, request: Request) -> dict:
    try:
        adapter = get_adapter(source)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Inject the shared Redis client into the RailRadar adapter for caching.
    if isinstance(adapter, RailRadarAdapter):
        adapter._redis = getattr(request.app.state, "redis", None)

    trains = adapter.get_trains()
    return {
        "source": source,
        "count": len(trains),
        "live": _is_live(source),
        "trains": [t.model_dump(mode="json") for t in trains],
    }


def _is_live(source: str) -> bool:
    if source.lower() != "railradar":
        return False
    from app.config import get_settings

    return get_settings().railradar_enabled
