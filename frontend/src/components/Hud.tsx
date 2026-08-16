import { useState } from "react";
import type { ReactNode } from "react";
import type { ConnState } from "../hooks/useTwinStream";
import type { TwinTick } from "../types";
import { setSpeed } from "../api/twin";

const CONN: Record<ConnState, { label: string; color: string }> = {
  connecting: { label: "Connecting…", color: "#eab308" },
  live: { label: "LIVE", color: "#22c55e" },
  polling: { label: "Polling", color: "#eab308" },
  offline: { label: "Offline", color: "#ef4444" },
};

const STEPS = [1, 5, 10, 20, 50, 100];

export default function Hud({ tick, conn }: { tick: TwinTick | null; conn: ConnState }) {
  const c = CONN[conn];
  const [busy, setBusy] = useState(false);
  const speed = tick?.sim_speed ?? 20;

  const change = async (dir: -1 | 1) => {
    const idx = nearestStep(speed);
    const next = STEPS[Math.max(0, Math.min(STEPS.length - 1, idx + dir))];
    setBusy(true);
    try {
      await setSpeed(next);
    } catch {
      /* ignore; the next tick reflects reality */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 px-5 py-3">
      <div className="flex items-center gap-3">
        <span className="relative flex h-3 w-3">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60" style={{ background: c.color }} />
          <span className="relative inline-flex h-3 w-3 rounded-full" style={{ background: c.color }} />
        </span>
        <div>
          <div className="text-sm font-semibold" style={{ color: c.color }}>{c.label}</div>
          <div className="text-xs text-slate-500">RailRadar · Vasai Road (BSR)</div>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <Stat label="Sim time" value={tick?.sim_time ?? "—"} />
        <Trains value={tick?.count ?? "—"} />
        {/* speed control */}
        <div className="text-right">
          <div className="text-xs uppercase tracking-wide text-slate-500">Speed</div>
          <div className="mt-0.5 flex items-center gap-1">
            <SpeedBtn label="−" disabled={busy || speed <= STEPS[0]} onClick={() => change(-1)} />
            <span className="w-14 text-center font-mono text-lg font-semibold tabular-nums">{Math.round(speed)}×</span>
            <SpeedBtn label="+" disabled={busy || speed >= STEPS[STEPS.length - 1]} onClick={() => change(1)} />
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="text-right">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

function Trains({ value }: { value: ReactNode }) {
  return (
    <div className="text-right">
      <div className="text-xs uppercase tracking-wide text-slate-500">Around Vasai</div>
      <div className="font-mono text-lg font-semibold tabular-nums">{value}</div>
    </div>
  );
}

function SpeedBtn({ label, onClick, disabled }: { label: string; onClick: () => void; disabled: boolean }) {
  return (
    <button onClick={onClick} disabled={disabled}
      className="h-7 w-7 rounded-md border border-slate-700 bg-slate-800 text-slate-200 transition hover:bg-slate-700 disabled:opacity-40">
      {label}
    </button>
  );
}

function nearestStep(v: number): number {
  let best = 0, bestD = Infinity;
  STEPS.forEach((s, i) => {
    const d = Math.abs(s - v);
    if (d < bestD) { bestD = d; best = i; }
  });
  return best;
}
