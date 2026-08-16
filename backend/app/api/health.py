"""Health endpoint — pings DB and Redis."""
from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.db.session import get_engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request) -> dict:
    db_ok = _check_db()
    redis_ok = _check_redis(request)
    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {
        "status": status,
        "db": "ok" if db_ok else "down",
        "redis": "ok" if redis_ok else "down",
    }


def _check_db() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def _check_redis(request: Request) -> bool:
    client = getattr(request.app.state, "redis", None)
    if client is None:
        return False
    try:
        return bool(client.ping())
    except Exception:
        return False
