"""Persisted-entity endpoints — read stations/trains from Postgres.

These demonstrate that Phase 1 persistence works. They degrade gracefully
(return an empty list) if the database is unavailable, so the API never 500s
in a DB-less context.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter
from sqlalchemy import select

from app.db import models as m
from app.db.session import session_scope

log = logging.getLogger("vasai.entities")
router = APIRouter(tags=["entities"])


@router.get("/stations")
def list_stations() -> dict:
    rows = _safe_query(
        lambda s: [
            {"code": r.code, "name": r.name, "corridor": r.corridor,
             "km_from_bsr": r.km_from_bsr}
            for r in s.scalars(select(m.Station).order_by(m.Station.km_from_bsr))
        ]
    )
    return {"count": len(rows), "stations": rows}


@router.get("/trains")
def list_trains() -> dict:
    rows = _safe_query(
        lambda s: [
            {"train_id": r.train_id, "name": r.name, "train_type": r.train_type,
             "priority": r.priority}
            for r in s.scalars(select(m.Train).order_by(m.Train.priority))
        ]
    )
    return {"count": len(rows), "trains": rows}


def _safe_query(fn):
    try:
        with session_scope() as session:
            return fn(session)
    except Exception as exc:
        log.warning("Entity query failed (DB unavailable?): %s", exc)
        return []
