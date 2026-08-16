import type { ConnState } from "../hooks/useTwinStream";
import type { TwinTick } from "../types";

const CONN: Record<ConnState, { label: string; color: string }> = {
  connecting: { label: "Connecting…", color: "#eab308" },
  live: { label: "LIVE", color: "#22c55e" },
  polling: { label: "Polling", color: "#eab308" },
  offline: { label: "Offline", color: "#ef4444" },
};

export default function Hud({ tick, conn }: { tick: TwinTick | null; conn: ConnState }) {
  const c = CONN[conn];
  const stat = [
    { label: "Sim time", value: tick?.sim_time ?? "—" },
    { label: "Speed", value: tick ? `${tick.sim_speed}×` : "—" },
    { label: "Trains around Vasai", value: tick?.count ?? "—" },
  ];
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/70 px-5 py-3">
      <div className="flex items-center gap-3">
        <span className="relative flex h-3 w-3">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60"
            style={{ background: c.color }} />
          <span className="relative inline-flex h-3 w-3 rounded-full" style={{ background: c.color }} />
        </span>
        <div>
          <div className="text-sm font-semibold" style={{ color: c.color }}>{c.label}</div>
          <div className="text-xs text-slate-500">RailRadar · Vasai Road (BSR)</div>
        </div>
      </div>
      <div className="flex gap-6">
        {stat.map((s) => (
          <div key={s.label} className="text-right">
            <div className="text-xs uppercase tracking-wide text-slate-500">{s.label}</div>
            <div className="font-mono text-lg font-semibold tabular-nums">{s.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
