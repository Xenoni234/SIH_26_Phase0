# AI-Powered Precise Train Traffic Control
### Predictive Digital Twin & Decision Support System for Vasai Road Junction (BSR)

> **Smart India Hackathon 2026 · Team Code Bandits**
>
> A predictive, simulation-driven railway **Decision Support System** built on a **Digital Twin of
> Vasai Road Junction**. It ingests existing/live train data, predicts near-future conflicts and
> delays, evaluates alternative traffic-management strategies, optimizes train sequencing under hard
> safety constraints, and gives **explainable** recommendations to a human controller.
>
> **AI recommends — the human decides. Safety always first.**

---

## The Problem

**Maximize railway section throughput using AI-powered precise train traffic control.**

Railway infrastructure is *finite* — tracks, blocks, platforms, junctions, routes, loops, and
yard/sidings. Trains are *heterogeneous* — express, passenger, local, freight, and shunting moves —
each with a different speed, priority, destination, delay, and dwell requirement. A single decision
ripples through the network:

```
Train A delayed → junction slot missed → Train B held → platform occupied → Train C delayed → congestion
```

So the real question is **not** "which train goes first?" It is:

> *Given the current railway state, what decision produces the best overall network outcome while
> satisfying every hard safety constraint?*

**Minimize:** total delay · passenger delay · conflicts · platform contention · unnecessary holding · disruption.
**Maximize:** section throughput · infrastructure utilization · on-time performance · flow efficiency.

---

## What This Is — and Is NOT

This system sits **above** the existing railway ecosystem (RTIS, COA, ARS/TMS, signalling &
interlocking, NTES, FOIS, Data Logger, Kavach). Those systems observe, monitor, control, protect,
route, and report **what is happening**. This system predicts **what is likely to happen next** and
recommends **what should happen** — a decision-support layer, not a replacement.

| Existing systems | This system |
| --- | --- |
| Observe · Monitor · Control · Protect · Route · Report | Observe → Understand → Predict → Simulate → Optimize → Validate → **Recommend** → Human decides |

**We are explicitly NOT building:** a replacement for signalling/interlocking · direct AI control of
signals · a photorealistic 3D station · a nationwide/full-Mumbai simulation · a recreation of Kavach ·
an LLM that "drives" trains · RL as the first MVP · a system that assumes proprietary RTIS access.

---

## Core Loop

```
Observe → Understand → Predict → Simulate → Optimize → Validate → Recommend → Human Decision → Re-evaluate
```

This is a **closed loop**: the controller's Accept / Modify / Reject decision becomes the operating
plan, the Digital Twin updates with actual state, and the system continuously re-optimizes.

---

## Prototype Scope — Vasai Road Junction (BSR)

Vasai Road is chosen because it has enough operational complexity (multiple corridors, priorities,
yard and freight activity, junction competition) while staying tractable.

```
                          NORTH / SURAT
                               ↑
                             VIRAR
                               │
                         NALLA SOPARA
                               │
                          VASAI ROAD (BSR)  ── North Yard / Sidings (parallel to Vasai–Virar)
                              /   \
             WESTERN / MUMBAI     VIRAR–DIVA–BHIWANDI–PANVEL
                corridor              corridor  ── Freight / Goods (Diva-side)
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

- **North Yard / Sidings** run *parallel to the Vasai–Virar corridor* — an operational resource, not a passenger branch.
- **Freight / Goods** operations are associated with the *Diva-side corridor*.

---

## Architecture

Nine operational stages, mapped onto six technical layers.

```
1. EXISTING RAILWAY SYSTEMS & LIVE DATA   (RTIS · COA · ARS/TMS · Signalling · NTES · RailRadar · Data Logger)
                 │
2. DATA INGESTION & NORMALIZATION         (validate → normalize → timestamp sync → unified state)
                 │
3. VASAI ROAD DIGITAL TWIN                (infra + train + operational state; NetworkX graph + SimPy sim)
                 │
4. PREDICT FUTURE STATE                   (ETA · delay propagation · conflict probability · 5/10/20-min look-ahead)
                 │
5. CONFLICT / BOTTLENECK DETECTION        (junction · platform · route · headway conflicts)
                 │
6. WHAT-IF SIMULATION + OPTIMIZATION      (scenarios A/B/C/D → simulate → compare → best feasible action)
                 │
7. SAFETY & FEASIBILITY CHECK             (headway · track · platform · route · operational — AI CANNOT override)
                 │
8. TRAFFIC CONTROLLER DASHBOARD           (live twin · prediction alert · recommended action · expected impact)
                 │                         → [ ACCEPT ] [ MODIFY ] [ REJECT ]
9. UPDATED OPERATING PLAN → UPDATED TWIN → CONTINUOUS MONITORING & RE-OPTIMIZATION ↺
```

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | React · TypeScript · Tailwind CSS · MapLibre / SVG · WebSockets |
| **Backend** | Python · FastAPI · Pydantic |
| **Database** | PostgreSQL · PostGIS |
| **Real-time** | Redis · WebSockets |
| **Data processing** | Pandas · Python |
| **Digital Twin / Simulation** | SimPy (discrete-event) · NetworkX (railway graph) |
| **ML (prediction)** | scikit-learn · XGBoost · PyTorch *(later)* |
| **Optimization (decisions)** | Google OR-Tools · Pyomo / MILP |
| **Advanced AI (stretch)** | Graph Neural Network · Reinforcement Learning |
| **Infrastructure** | Docker · Docker Compose · Git / GitHub |
| **Optional later** | Prometheus · Grafana · Kubernetes · CI/CD · MLflow |

---

## Design Principles

1. **Separation of concerns** — *ML predicts, OR decides, Simulation validates, Rules enforce safety,
   the Dashboard supports the human.* No single "do-everything" AI model.
2. **Hard-constraint safety validator** — a deterministic gate the optimizer can never bypass
   (headway, track/platform availability, route feasibility, dwell, ordering, signal/interlocking rules).
3. **Human-in-the-loop** — the AI never controls signalling; it recommends, the controller decides.
4. **Explainability** — every recommendation carries *what · why · expected impact · alternatives*.
5. **Source-agnostic data** — every feed is normalized behind an adapter into a unified `TrainState`,
   so the prototype can evolve into real integration without rewriting the core.

---

## Data Strategy

- **Public / official** (timetable, infrastructure, topology): Indian Railways, CRIS, Western/Central
  Railway, MRVC, NTES, RDSO documents.
- **Authorized operational** (if access is granted): RTIS, COA, Data Logger feeds.
- **Synthetic** (always available): generated scenarios for normal/peak traffic, express/freight
  delays, platform/track blockage, signal failure, multi-delay, yard conflict — used for ML training
  and disruption testing.

> **RailRadar** is used as an *external prototype live-data source* for train position / delay /
> schedule / route. **RailRadar ≠ RTIS.** It does not expose signal state, track-circuit status,
> interlocking, ARS decisions, or internal COA state — and must never be described as RTIS access.

**Source-agnostic adapters:**

```
RailRadar Adapter ─┐
RTIS Adapter ──────┤
COA Adapter ───────┼──→ Normalized TrainState ──→ Digital Twin
NTES Adapter ──────┤
Synthetic Adapter ─┘
```

---

## MVP Levels

- **MVP 1 — Digital Twin + Simulation:** operational Vasai topology with trains that move.
- **MVP 2 — Predictive Control (core intelligence):** ETA, delay propagation, and conflict prediction
  — *"Express and freight are likely to conflict in 7 minutes at Junction J2."*
- **MVP 3 — Optimization + Decision Support:** what-if, optimization, safety-validated explainable
  recommendation — *"Hold Freight F1 for 4 minutes because it minimizes expected network delay."*

---

## Phase Roadmap

The prototype is built in demo-driven phases (each with a concrete, showable exit criterion). See
**[AGENTS.md](AGENTS.md)** for the full breakdown, guardrails, and canonical domain reference.

| Phase | Milestone | Demoable exit |
| --- | --- | --- |
| **0** | Foundations & scaffolding + adapters (RailRadar + synthetic) | A valid twin loads; RailRadar adapter returns normalized state |
| **1** | Digital Twin state + static Vasai map | See the twin (no motion) |
| **2** | Simulation engine — trains move (SimPy + WebSockets) | Watch trains move on the map |
| **3** | Prediction layer (ETA · delay propagation · conflict) | "Conflict likely in 7 min at J2" alerts |
| **4** | What-if + optimization + safety validator | Ranked, feasible candidate actions |
| **5** | Explainable recommendation + controller dashboard | Full closed loop (Accept/Modify/Reject) |
| **6** | Evaluation & disruption scenarios | Baseline-vs-AI KPIs; quantified demo story |
| **⁺** | *Stretch:* GNN · RL · PyTorch · Pyomo/MILP · richer fidelity | — |

---

## Key Metrics

Evaluated as **baseline strategy vs AI-optimized strategy**, using real simulation results (never
invented percentages): total / average / passenger / freight delay · number of conflicts · section
throughput · platform & route utilization · on-time percentage · recovery time after disruption.

---

## Status

🚧 **Phase 0 — documentation & scaffolding.** Getting-started / setup instructions will be added here
as the stack lands.

---

*Team Code Bandits · Smart India Hackathon 2026*
