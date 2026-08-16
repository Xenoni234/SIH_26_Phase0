"""Seed Postgres from the canonical topology (idempotent).

Two layers:
  * build_seed_rows(topo) — pure transform (topology -> plain dicts). Testable
    without a database.
  * seed(session) / seed_on_startup() — upsert those rows via SQLAlchemy.

Reuses the Phase 0 loader and synthetic adapter; never re-implements topology.
Run manually:  python -m app.seed
"""
from __future__ import annotations

import logging

from app.adapters import SyntheticAdapter
from app.db import models as m
from app.db.session import session_scope
from app.topology.loader import Topology, get_topology

log = logging.getLogger("vasai.seed")


def build_seed_rows(topo: Topology) -> dict[str, list[dict]]:
    """Topology (+ a synthetic train snapshot) -> plain row dicts."""
    stations = [
        {"code": st.code, "name": st.name, "corridor": st.corridor.value,
         "km_from_bsr": st.km}
        for st in topo.stations().values()
    ]
    platforms = [
        {"id": pf.id, "station": topo.junction_code, "number": pf.number,
         "length_m": pf.length_m, "serves": pf.serves}
        for pf in topo.platforms
    ]
    blocks = [
        {"id": b.block_id, "corridor": b.corridor.value, "from_station": b.from_station,
         "to_station": b.to_station, "length_km": b.length_km,
         "headway_seconds": topo.defaults.get("headway_seconds", 120)}
        for b in topo.blocks
    ]
    junctions = [
        {"id": j.id, "name": j.name, "connects": j.connects} for j in topo.junctions
    ]
    signals = [
        {"id": s["id"], "at_node": s.get("at"), "kind": s.get("kind", "home")}
        for s in topo.signals
    ]
    trains = [
        {"train_id": t.train_id, "name": t.name, "train_type": t.train_type.value,
         "priority": t.priority}
        for t in SyntheticAdapter(topo, seed=0).get_trains()
    ]
    return {
        "stations": stations,
        "platforms": platforms,
        "blocks": blocks,
        "junctions": junctions,
        "signals": signals,
        "trains": trains,
    }


def _upsert(session, model, rows: list[dict], pk: str) -> int:
    """Insert-or-update rows by primary key (small tables — simple get/merge)."""
    for row in rows:
        obj = session.get(model, row[pk])
        if obj is None:
            session.add(model(**row))
        else:
            for k, v in row.items():
                setattr(obj, k, v)
    return len(rows)


def seed(session, topo: Topology | None = None) -> dict[str, int]:
    topo = topo or get_topology()
    rows = build_seed_rows(topo)

    # Parents first, flushed so FK targets exist before dependents are inserted.
    counts = {"stations": _upsert(session, m.Station, rows["stations"], "code")}
    counts["junctions"] = _upsert(session, m.Junction, rows["junctions"], "id")
    session.flush()

    # Dependents (platforms -> stations, signals -> junction nodes).
    counts["platforms"] = _upsert(session, m.Platform, rows["platforms"], "id")
    counts["blocks"] = _upsert(session, m.Block, rows["blocks"], "id")
    counts["signals"] = _upsert(session, m.Signal, rows["signals"], "id")
    counts["trains"] = _upsert(session, m.Train, rows["trains"], "train_id")
    return counts


def seed_on_startup() -> None:
    """Called from the app lifespan. Never crashes the app if the DB is down."""
    try:
        with session_scope() as session:
            counts = seed(session)
        log.info("Seeded twin into Postgres: %s", counts)
    except Exception as exc:  # DB not ready / not configured
        log.warning("Seed skipped (DB unavailable): %s", exc)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    with session_scope() as s:
        print("Seeded:", seed(s))
