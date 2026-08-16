"""FastAPI application entrypoint.

Lifespan:
  * load + validate the Vasai topology (fail fast if broken),
  * connect Redis (optional; health reports status),
  * expose /health, /twin, /adapters/{source}/trains.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import asyncio

import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import adapters as adapters_api
from app.api import entities as entities_api
from app.api import health as health_api
from app.api import stream as stream_api
from app.api import twin as twin_api
from app.config import get_settings
from app.seed import seed_on_startup
from app.simulation.engine import SimulationEngine
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

    # 3) Persist the twin into Postgres (idempotent; safe if DB is down).
    if settings.seed_on_startup:
        seed_on_startup()

    # 4) Live simulation: seed from the real RailRadar board + start the loop.
    app.state.broadcaster = stream_api.Broadcaster()
    engine = SimulationEngine(topo=topo)
    engine.attach_redis(app.state.redis)
    engine.seed()
    app.state.engine = engine
    app.state.sim_task = asyncio.create_task(stream_api.run_simulation_loop(app))

    log.info(
        "RailRadar source: %s",
        "LIVE" if settings.railradar_enabled else "fixtures (no key)",
    )
    yield

    task = getattr(app.state, "sim_task", None)
    if task is not None:
        task.cancel()
    if getattr(app.state, "redis", None) is not None:
        app.state.redis.close()


app = FastAPI(
    title="Vasai Road Digital Twin — Decision Support",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_origin_regex=get_settings().cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_api.router)
app.include_router(twin_api.router)
app.include_router(entities_api.router)
app.include_router(adapters_api.router)
app.include_router(stream_api.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": "Vasai Road Digital Twin — Decision Support",
        "phase": 2,
        "version": __version__,
        "endpoints": [
            "/health", "/twin", "/twin/summary", "/stations", "/trains",
            "/adapters/{source}/trains", "/sim/snapshot", "/ws/twin (WebSocket)",
        ],
        "note": "AI recommends — human decides. RailRadar is an external prototype source, not RTIS.",
    }
