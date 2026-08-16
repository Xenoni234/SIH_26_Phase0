"""initial schema — create all Phase 0 tables

Revision ID: 0001
Revises:
Create Date: 2026-08-16

Phase 0 creates the entire schema from the SQLAlchemy metadata in one shot.
Later phases add incremental migrations on top.
"""
from __future__ import annotations

from alembic import op

from app.db.base import Base
import app.db.models  # noqa: F401  (populate Base.metadata)

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # PostGIS is enabled by infra/postgres/init.sql; ensure it here too for
    # non-container databases used in local runs.
    bind.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis")
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
