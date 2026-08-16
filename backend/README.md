# Backend — Vasai Road Digital Twin (Phase 0)

FastAPI + PostgreSQL/PostGIS + Redis. Loads the canonical Vasai topology
(`data/topology/vasai.yaml`) into a NetworkX graph and exposes it, plus
source-agnostic adapters (synthetic + RailRadar) that emit normalized `TrainState`.

## Run the full stack (recommended)
From the repo root:

```bash
cp .env.example .env    # then paste your RAILRADAR_API_KEY into .env
docker compose up --build
```

Services: `db` (PostGIS), `redis`, `backend` (runs `alembic upgrade head` then uvicorn).

### Verify
```bash
curl localhost:8000/health
curl localhost:8000/twin/summary
curl localhost:8000/adapters/synthetic/trains
curl localhost:8000/adapters/railradar/trains
```

Open API docs: http://localhost:8000/docs

## Local dev (tests without Docker)
Topology/adapter/API tests need no database:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

## RailRadar
- Live only when `RAILRADAR_API_KEY` is set; otherwise recorded fixtures in
  `app/adapters/fixtures/` are used (offline).
- Set `RAILRADAR_TRAIN_NUMBERS` (comma-separated) to a small set of Vasai-relevant
  trains — responses are Redis-cached (`RAILRADAR_CACHE_TTL`) to respect the free
  tier (50 req/day). **RailRadar is an external prototype source, not RTIS.**

## Layout
- `app/models/` — normalized Pydantic contracts (TrainState, BlockState, …)
- `app/topology/` — YAML loader + NetworkX graph
- `app/adapters/` — SourceAdapter ABC, synthetic, RailRadar (+ fixtures)
- `app/db/` — SQLAlchemy models + session; `alembic/` migrations
- `app/api/` — `/health`, `/twin`, `/adapters/{source}/trains`
