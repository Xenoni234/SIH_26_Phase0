"""Entity endpoints return the right shape and never 500 without a DB."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_stations_endpoint_shape():
    # No DB in unit-test env -> graceful empty list, HTTP 200.
    with TestClient(app) as c:
        r = c.get("/stations")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body and "stations" in body
        assert isinstance(body["stations"], list)


def test_trains_endpoint_shape():
    with TestClient(app) as c:
        r = c.get("/trains")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body and "trains" in body
        assert isinstance(body["trains"], list)
