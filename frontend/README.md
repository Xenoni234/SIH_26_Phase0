# Frontend — Vasai Road Digital Twin (Phase 1)

React + TypeScript + Vite + Tailwind. Renders the Vasai junction as a static SVG
schematic (BSR + 7 platforms, 3 corridors, yard & freight, a static train snapshot)
with a click-to-inspect detail panel and a train table.

## Prerequisites
- Node.js 18+ and npm
- The backend running (see repo root `run.md`): `docker compose up` → API on `http://localhost:8000`

## Run
```bash
cd frontend
cp .env.example .env      # VITE_API_URL=http://localhost:8000
npm install
npm run dev               # http://localhost:5173
```

## Build (type-check + bundle)
```bash
npm run build
npm run preview
```

## Config
- `VITE_API_URL` — backend base URL (default `http://localhost:8000`).

## Layout
- `src/api/twin.ts` — typed fetch of `/twin`, `/twin/summary`, `/stations`
- `src/types.ts` — response types mirroring the backend
- `src/lib/layout.ts` — schematic SVG positioning (BSR centre; North up, Western
  lower-left, Diva lower-right)
- `src/components/TwinMap.tsx` — the SVG schematic (stations, platforms, yard,
  freight, trains; click to select)
- `src/components/DetailPanel.tsx` · `TrainTable.tsx` · `SummaryBar.tsx`

Phase 1 shows a **static** snapshot — trains do not move yet (that's Phase 2).
