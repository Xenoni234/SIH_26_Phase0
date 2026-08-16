"""ORM tables for the Vasai twin.

Phase 0 creates the full schema so later phases can persist state, movements,
predictions, simulation runs, and recommendations without further migrations.
Spatial columns use PostGIS geometry (nullable in Phase 0).
"""
from __future__ import annotations

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Station(Base):
    __tablename__ = "stations"
    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    corridor: Mapped[str] = mapped_column(String(20))
    km_from_bsr: Mapped[float] = mapped_column(Float, default=0.0)
    geom: Mapped[object | None] = mapped_column(
        Geometry("POINT", srid=4326), nullable=True
    )


class Platform(Base):
    __tablename__ = "platforms"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    station: Mapped[str] = mapped_column(ForeignKey("stations.code"))
    number: Mapped[int] = mapped_column(Integer)
    length_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serves: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Track(Base):
    __tablename__ = "tracks"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    corridor: Mapped[str] = mapped_column(String(20))
    from_node: Mapped[str] = mapped_column(String(20))
    to_node: Mapped[str] = mapped_column(String(20))
    length_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    geom: Mapped[object | None] = mapped_column(
        Geometry("LINESTRING", srid=4326), nullable=True
    )


class Block(Base):
    __tablename__ = "blocks"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    corridor: Mapped[str] = mapped_column(String(20))
    from_station: Mapped[str] = mapped_column(String(10))
    to_station: Mapped[str] = mapped_column(String(10))
    length_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    headway_seconds: Mapped[int] = mapped_column(Integer, default=120)


class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    at_node: Mapped[str] = mapped_column(String(20))
    kind: Mapped[str] = mapped_column(String(20), default="home")


class Junction(Base):
    __tablename__ = "junctions"
    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    connects: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    from_node: Mapped[str] = mapped_column(String(20))
    to_node: Mapped[str] = mapped_column(String(20))
    path: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class Train(Base):
    __tablename__ = "trains"
    train_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    train_type: Mapped[str] = mapped_column(String(20))
    priority: Mapped[int] = mapped_column(Integer, default=5)


class Timetable(Base):
    __tablename__ = "timetables"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_id: Mapped[str] = mapped_column(String(20))
    station: Mapped[str] = mapped_column(String(10))
    arrival: Mapped[str | None] = mapped_column(String(8), nullable=True)
    departure: Mapped[str | None] = mapped_column(String(8), nullable=True)
    platform: Mapped[int | None] = mapped_column(Integer, nullable=True)


class TrainMovement(Base):
    __tablename__ = "train_movements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_id: Mapped[str] = mapped_column(String(20))
    block_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    station: Mapped[str | None] = mapped_column(String(10), nullable=True)
    speed_kmph: Mapped[float | None] = mapped_column(Float, nullable=True)
    delay_min: Mapped[float] = mapped_column(Float, default=0.0)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(20), default="synthetic")


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(30))
    train_id: Mapped[str] = mapped_column(String(20))
    station: Mapped[str | None] = mapped_column(String(10), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(30))  # eta | delay | conflict
    train_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    scenario: Mapped[str | None] = mapped_column(String(120), nullable=True)
    kpis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_impact: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    alternatives: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="proposed")  # accept/modify/reject
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Scenario(Base):
    __tablename__ = "scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
