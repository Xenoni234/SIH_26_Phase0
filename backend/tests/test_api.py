"""API smoke tests using FastAPI's TestClient (no DB/Redis needed for /twin)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _client() -> TestClient:
    # Use context manager so lifespan runs (loads topology, tries Redis).
    return TestClient(app)


def test_root():
    with _client() as c:
        r = c.get("/")
        assert r.status_code == 200
        assert r.json()["phase"] == 0


def test_twin_summary():
    with _client() as c:
        r = c.get("/twin/summary")
        assert r.status_code == 200
        body = r.json()
        assert body["platforms"] == 7
        assert set(body["corridors"]) == {"north", "western", "diva"}


def test_twin_graph_and_trains():
    with _client() as c:
        r = c.get("/twin")
        assert r.status_code == 200
        body = r.json()
        assert body["junction"]["code"] == "BSR"
        assert body["summary"]["nodes"] > 0
        assert len(body["trains"]) >= 5


def test_adapters_synthetic():
    with _client() as c:
        r = c.get("/adapters/synthetic/trains")
        assert r.status_code == 200
        assert r.json()["count"] >= 5


def test_adapters_railradar_fixture():
    with _client() as c:
        r = c.get("/adapters/railradar/trains")
        assert r.status_code == 200
        body = r.json()
        assert body["source"] == "railradar"
        assert body["count"] >= 1


def test_unknown_adapter_404():
    with _client() as c:
        r = c.get("/adapters/nope/trains")
        assert r.status_code == 404
