# AGENTS.md — Working Guide for AI Agents

This file tells any AI agent (Claude Code, Cursor, Copilot, etc.) what this project is, how to reason
about it, and the rules it must not break. Read this **before** proposing or writing code.
For the human-facing overview, see **[README.md](README.md)**.

---

## 1. Mission

Build a **predictive, simulation-driven railway Decision Support System** on a **Digital Twin of
Vasai Road Junction (BSR)**. It ingests existing/live train data, predicts near-future conflicts and
delays, evaluates alternative traffic-management strategies via what-if simulation, optimizes train
sequencing and resource allocation subject to **hard safety constraints**, and produces
**explainable** recommendations for a human traffic controller.

**Team:** Code Bandits · **Event:** Smart India Hackathon 2026 · **Deliverable now:** a *working
prototype*, not a production system.

### Non-goals (do NOT build these)
- ❌ A replacement for signalling / interlocking, or **direct AI control of signals**.
- ❌ A photorealistic 3D model of the station (the "Digital Twin" here is *operational*, not visual).
- ❌ A nationwide or full-Mumbai-network simulation.
- ❌ A recreation of Kavach, or an LLM that "drives" trains.
- ❌ Reinforcement Learning as the first MVP (it is a stretch goal).
- ❌ Any design that assumes proprietary RTIS data is available.
- ❌ Full replication of every railway rule — model what the prototype demo needs.

---

## 2. Mental Model (the single most important section)

The system is a **pipeline of specialized components**, not one giant AI model. Keep these responsibilities separate:

| Concern | Owner | Never do this instead |
| --- | --- | --- |
| **Prediction** (ETA, delay, conflict) | ML (XGBoost) | Don't let ML make operational decisions |
| **Decisions** (precedence, routing, holding, platform, sequencing) | Operations Research (OR-Tools / MILP) | Don't hardcode decisions in the UI or ML |
| **Validation** ("what happens if we do X?") | Simulation (SimPy) | Don't trust an optimizer output without simulating it |
| **Hard safety** (headway, track, platform, route, dwell, interlocking) | Deterministic Rule Engine | Don't let ML/OR ever override these |
| **Human decision** | Controller Dashboard | Don't auto-apply; recommend only |

Decision flow with the safety gate:

```
Optimization → Safety & Feasibility Validator → VALID? ─ yes → Explainable Recommendation → Human
                                                  │
                                                  no → back to optimizer
```

**The Digital Twin has three jobs:** (1) represent current state, (2) simulate future state,
(3) run what-if experiments. It is the central state engine — not just the UI.

---

## 3. Domain Glossary

- **Block** — a track segment that only one train may occupy at a time (safety unit of movement).
- **Headway** — minimum time/space separation required between successive trains. A **hard constraint**.
- **Dwell** — time a train must remain stopped at a platform. A constraint on scheduling.
- **Junction** — where corridors meet and compete for crossing slots (e.g. Vasai Road / BSR).
- **Loop / siding** — a parallel track used to hold or overtake trains (e.g. hold freight for an express).
- **Precedence** — the decision of which train goes first through a shared resource.
- **Corridor** — a directional line of stations (Western/Mumbai, Diva/Panvel, North/Surat).
- **Platform contention** — two trains needing the same platform in overlapping windows.
- **Digital Twin** — a **live operational** representation of infrastructure + trains + state +
  constraints. **Not** a 3D render.
- **RTIS / COA / ARS / TMS / NTES / FOIS** — existing Indian Railways systems this project sits *above*.
- **RailRadar** — an external public live-train data source used for the prototype. **Not RTIS.**

---

## 4. Canonical Vasai Topology (do not re-invent this)

The prototype models **Vasai Road Junction (BSR)** with three corridors plus yard and freight resources.

```
                          NORTH / SURAT
                               ↑
                             VIRAR
                               │
                         NALLA SOPARA
                               │
                          VASAI ROAD (BSR)
                              /   \
             WESTERN / MUMBAI     VIRAR–DIVA–BHIWANDI–PANVEL
                corridor              corridor
                   │                     │
                Naigaon               Juchandra
                Bhayandar             Kaman Road
                Mira Road             Kharbav
                Dahisar               Bhiwandi Road
                Borivali              Kopar
                Andheri               Diva
                Bandra                Panvel
                Dadar
                Mumbai Central
                Churchgate
```

- **North / Surat direction:** Vasai → Nalla Sopara → Virar → (Surat / north).
- **Western / Mumbai corridor:** Vasai → Naigaon → Bhayandar → Mira Road → … → Churchgate.
- **Diva corridor:** Vasai → Juchandra → Kaman Road → Kharbav → Bhiwandi Road → Kopar → Diva → Panvel.
- **North Yard / Sidings:** run **parallel to the Vasai–Virar corridor** — an operational resource, *not* a passenger branch.
- **Freight / Goods:** associated with the **Diva-side corridor**.

---

## 5. Unified Data Model

Internal state entities (normalized, source-agnostic):

`TrainState` · `TrackState` · `BlockState` · `PlatformState` · `SignalState` · `RouteState` ·
`JunctionState` · `StationEvent` · `DelayState`

`TrainState` core fields: id, type (express/passenger/local/freight/yard), location, current block,
speed, direction, destination, delay, priority, ETA.

Database tables (PostgreSQL + PostGIS):
`stations · platforms · tracks · blocks · signals · junctions · routes · trains · timetables ·
train_movements · events · predictions · simulation_runs · recommendations · scenarios`

---

## 6. Source-Agnostic Adapter Rule

Never let a source-specific payload (e.g. RailRadar JSON) leak into the core. Every feed goes through
an adapter that emits a normalized `TrainState`:

```
RailRadar Adapter ─┐
RTIS Adapter ──────┤
COA Adapter ───────┼──→ Normalized TrainState ──→ Digital Twin
NTES Adapter ──────┤
Synthetic Adapter ─┘
```

For this prototype: **RailRadar adapter** (live prototype feed) + **Synthetic adapter** (training &
disruption scenarios) are wired early. Others are stubs behind the same interface.

---

## 7. Guardrails (hard rules for agents)

1. **RailRadar ≠ RTIS.** Never describe RailRadar as RTIS/official Indian Railways access.
2. **Never let ML or OR violate hard safety constraints.** The deterministic validator is the final gate.
3. **AI never directly controls signals.** Output is a *recommendation*; a human accepts/modifies/rejects.
4. **Explainable output only.** Every recommendation states *what · why · expected impact · alternatives*.
5. **Use real simulation numbers**, never invented percentages, in evaluation and demos.
6. **Respect the topology above** — don't move the yard, freight, or corridors around.
7. **Keep concerns separated** (Section 2). No single model that predicts *and* decides *and* validates.
8. **Prototype-scoped fidelity** — model what the demo needs; don't try to encode all of Indian Railways.

---

## 8. Repo Conventions

- **Stack (target):** React + TS + Tailwind + MapLibre/SVG (frontend) · FastAPI + Pydantic (backend) ·
  PostgreSQL + PostGIS (db) · Redis + WebSockets (real-time) · SimPy + NetworkX (twin/sim) ·
  scikit-learn / XGBoost (ML) · OR-Tools + Pyomo/MILP (optimization) · Docker Compose (infra).
- **Structure & run instructions:** *to be filled in as code lands (Phase 0+).*
- When adding a component, state which mental-model concern (Section 2) it belongs to.

---

## 9. Phase Roadmap (prototype)

Each phase has a goal, key components, and a concrete **demoable exit criterion**. Build in order;
don't skip ahead to GNN/RL.

### Phase 0 — Foundations & Scaffolding
- **Goal:** a runnable skeleton and the data backbone.
- **Components:** repo structure; Docker Compose (FastAPI + Postgres/PostGIS + Redis); env & deps;
  data schemas/contracts (Section 5); Vasai topology encoded as a **NetworkX graph + config**;
  **source-agnostic adapter interface + RailRadar adapter + synthetic adapter** → normalized `TrainState`.
- **Tech:** FastAPI, Pydantic, Postgres/PostGIS, Redis, NetworkX, Docker Compose.
- **Exit:** a valid twin loads from config; the RailRadar adapter returns normalized `TrainState`.

### Phase 1 — Digital Twin State + Static Map
- **Goal:** represent and display current state.
- **Components:** unified state model; infrastructure + train entities persisted; backend serves twin
  state; frontend renders the static Vasai map (stations, corridors, platforms, yard, freight).
- **Tech:** FastAPI, PostGIS, React + TS + MapLibre/SVG.
- **Exit:** you can see the twin on screen (no motion yet).

### Phase 2 — Simulation Engine (trains move)
- **Goal:** trains move through the twin over time.
- **Components:** SimPy discrete-event sim (enter/exit block, arrival, departure, dwell, route set/
  release, platform occupy/release, junction/yard/freight moves); state streamed to the UI.
- **Tech:** SimPy, Redis, WebSockets.
- **Exit:** watch simulated trains move on the live map.

### Phase 3 — Prediction Layer
- **Goal:** forecast the near future.
- **Components:** ETA prediction, delay-propagation prediction (XGBoost regression), conflict
  prediction (XGBoost classifier); training data generated from the simulator + synthetic scenarios.
- **Tech:** scikit-learn, XGBoost, Pandas.
- **Exit:** the system raises alerts like *"conflict likely in 7 min at J2."*

### Phase 4 — What-If + Optimization + Safety Validator
- **Goal:** propose feasible, safe candidate actions.
- **Components:** what-if engine (generate alternatives A/B/C/D, simulate each); optimization
  (OR-Tools / MILP) minimizing delay + conflicts + contention + unnecessary holding, maximizing
  throughput; **deterministic safety/feasibility validator** as the final gate.
- **Tech:** SimPy, OR-Tools, (Pyomo/MILP later).
- **Exit:** a ranked list of *feasible* candidate actions with simulated outcomes.

### Phase 5 — Explainable Recommendation + Controller Dashboard
- **Goal:** close the human-in-the-loop.
- **Components:** recommendation with *what · why · expected impact · alternatives*; dashboard with
  live twin, prediction alert, recommended action, expected impact; **Accept / Modify / Reject**;
  twin updates on the controller's decision.
- **Tech:** FastAPI, React + TS, WebSockets.
- **Exit:** the full closed loop runs — recommend → decide → twin updates → re-optimize.

### Phase 6 — Evaluation & Disruption Scenarios
- **Goal:** prove it with numbers.
- **Components:** disruption injection (breakdown, signal failure, track/platform block, freight delay,
  peak traffic, yard congestion, multi-delay); baseline-vs-AI KPI comparison (delay, throughput,
  conflicts, utilization, recovery time).
- **Tech:** SimPy, Pandas; reporting/export.
- **Exit:** a quantified demo story — baseline vs AI-optimized, from real simulation runs.

### Stretch (after the prototype works)
GNN (PyTorch, nodes = network entities / edges = movement links) · Reinforcement Learning
(state = railway state, action = hold/route/prioritize, reward = less delay / more throughput /
fewer conflicts) · Pyomo/MILP advanced formulations · richer infrastructure fidelity ·
Prometheus / Grafana / MLflow / Kubernetes / CI-CD.

---

## 10. The One-Line Summary

> Observe → Understand → Predict → Simulate → Optimize → Validate → Recommend → **Human Decision** → Re-evaluate.
>
> ML predicts · OR decides · Simulation validates · Rules keep it safe · the human stays in control.
