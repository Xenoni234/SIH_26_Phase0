"""WebSocket streaming of the live simulation + the broadcast loop."""
from __future__ import annotations

import asyncio
import logging
import time

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from app.config import get_settings
from app.simulation.engine import SimulationEngine

log = logging.getLogger("vasai.stream")
router = APIRouter(tags=["stream"])


class Broadcaster:
    """Tracks connected clients and fans out snapshots."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._clients):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    @property
    def count(self) -> int:
        return len(self._clients)


@router.get("/sim/snapshot", tags=["stream"])
def sim_snapshot(request: Request) -> dict:
    """Current simulation snapshot (REST fallback for the WebSocket stream)."""
    engine: SimulationEngine = request.app.state.engine
    return engine.snapshot()


@router.websocket("/ws/twin")
async def ws_twin(ws: WebSocket) -> None:
    broadcaster: Broadcaster = ws.app.state.broadcaster
    engine: SimulationEngine = ws.app.state.engine
    await broadcaster.connect(ws)
    try:
        # Send an immediate snapshot so the client renders without waiting a tick.
        await ws.send_json(engine.snapshot())
        while True:
            # We don't expect client messages; this keeps the socket open.
            await ws.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect(ws)
    except Exception as exc:  # noqa: BLE001
        log.warning("WS error: %s", exc)
        broadcaster.disconnect(ws)


async def run_simulation_loop(app) -> None:
    """Background task: advance the sim clock and broadcast every tick."""
    settings = get_settings()
    engine: SimulationEngine = app.state.engine
    broadcaster: Broadcaster = app.state.broadcaster
    last_seed = time.monotonic()

    while True:
        try:
            engine.tick()
            # Periodically reload the real board (cached; usually no API call).
            if time.monotonic() - last_seed > settings.railradar_board_ttl:
                engine.seed()
                last_seed = time.monotonic()
            if broadcaster.count:
                await broadcaster.broadcast(engine.snapshot())
        except Exception as exc:  # keep the loop alive
            log.warning("sim loop tick failed: %s", exc)
        await asyncio.sleep(settings.sim_tick_seconds)
