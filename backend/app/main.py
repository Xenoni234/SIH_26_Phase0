"""FastAPI application entrypoint.

Lifespan:
  * load + validate the Vasai topology (fail fast if broken),
  * connect Redis (optional; health reports status),
  * expose /health, /twin, /adapters/{source}/trains.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI

from app import __version__
from app.api import adapters as adapters_api
from app.api import health as health_api
from app.api import twin as twin_api
from app.config import get_settings
from app.topology.loader import get_topology, graph_of

logging.basicConfig(level=get_settings().log_level)
log = logging.getLogger("vasai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # 1) Load the Digital Twin (single source of truth). Fail fast if invalid.
    topo = get_topology()
    n_nodes = graph_of(topo).number_of_nodes()
    log.info("Loaded Vasai twin: %s (%d graph nodes)", topo.junction_code, n_nodes)

    # 2) Connect Redis (optional).
    try:
        app.state.redis = redis.from_url(settings.redis_url, decode_responses=True)
        app.state.redis.ping()
        log.info("Redis connected: %s", settings.redis_url)
    except Exception as exc:  # degrade gracefully
        app.state.redis = None
        log.warning("Redis unavailable (%s) — caching disabled.", exc)

    log.info(
        "RailRadar source: %s",
        "LIVE" if settings.railradar_enabled else "fixtures (no key)",
    )
    yield

    if getattr(app.state, "redis", None) is not None:
        app.state.redis.close()


app = FastAPI(
    title="Vasai Road Digital Twin — Decision Support (Phase 0)",
    version=__version__,
    lifespan=lifespan,
)

app.include_router(health_api.router)
app.include_router(twin_api.router)
app.include_router(adapters_api.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": "Vasai Road Digital Twin — Decision Support",
        "phase": 0,
        "version": __version__,
        "endpoints": ["/health", "/twin", "/twin/summary", "/adapters/{source}/trains"],
        "note": "AI recommends — human decides. RailRadar is an external prototype source, not RTIS.",
    }
