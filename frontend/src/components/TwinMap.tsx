import { useMemo } from "react";
import type { GraphNode, Selection, SimTrain, TwinResponse } from "../types";
import { VIEW, computeLayout, TYPE_COLOR } from "../lib/layout";

interface Props {
  twin: TwinResponse;
  trains: SimTrain[];
  selection: Selection;
  onSelect: (sel: Selection) => void;
}

// End-of-branch direction labels (matches the real station signage).
const CORRIDOR_LABEL: Record<string, string> = {
  north: "↑ Virar · Dahanu Rd",
  western: "Mumbai · Churchgate",
  diva: "Diva · Panvel",
};

export default function TwinMap({ twin, trains, selection, onSelect }: Props) {
  const layout = useMemo(
    () => computeLayout(twin.graph.nodes, twin.junction.code),
    [twin]
  );

  const selId =
    selection?.kind === "train"
      ? `train:${selection.train.id}`
      : selection && "node" in selection
      ? `node:${selection.node.id}`
      : null;

  // Farthest station per corridor -> place the direction label there.
  const endpoints = useMemo(() => {
    const far: Record<string, { id: string; x: number; y: number }> = {};
    for (const s of layout.stations.values()) {
      const c = s.corridor;
      if (!c || s.id === twin.junction.code) continue;
      if (!far[c] || (s.km ?? 0) > (layout.stations.get(far[c].id)?.km ?? 0)) {
        far[c] = { id: s.id, x: s.x, y: s.y };
      }
    }
    return far;
  }, [layout, twin.junction.code]);

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 shadow-xl">
      <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="w-full" role="img" aria-label="Vasai Road live twin">
        <defs>
          <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx={layout.center.x} cy={layout.center.y} r={140} fill="url(#glow)" />

        {/* --- Track edges --- */}
        {twin.graph.edges
          .filter((e) => e.kind === "block")
          .map((e, i) => {
            const a = layout.stations.get(e.source);
            const b = layout.stations.get(e.target);
            if (!a || !b) return null;
            return (
              <line key={`e${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                stroke="#334155" strokeWidth={5} strokeLinecap="round" />
            );
          })}

        {/* --- Corridor direction labels --- */}
        {Object.entries(endpoints).map(([corr, p]) => (
          <text key={corr} x={p.x} y={p.y + (corr === "north" ? -22 : 24)}
            textAnchor="middle" fontSize={11} fontWeight={600} fill="#64748b">
            {CORRIDOR_LABEL[corr] ?? corr}
          </text>
        ))}

        {/* --- Yard & Freight --- */}
        {layout.yard && (
          <ResourceBox node={layout.yard} label="North Yard" stroke="#a78bfa"
            selected={selId === `node:${layout.yard.id}`}
            onClick={() => onSelect({ kind: "yard", node: layout.yard! })} />
        )}
        {layout.freight && (
          <ResourceBox node={layout.freight} label="Freight / Goods" stroke="#f59e0b"
            selected={selId === `node:${layout.freight.id}`}
            onClick={() => onSelect({ kind: "freight", node: layout.freight! })} />
        )}

        {/* --- Platforms: P1–P5 slow/fast, P6–P7 MEMU --- */}
        {layout.platforms.map((pf) => {
          const memu = (pf.number ?? 0) >= 6;
          const sel = selId === `node:${pf.id}`;
          return (
            <g key={pf.id} className="cursor-pointer" onClick={() => onSelect({ kind: "platform", node: pf })}>
              <rect x={pf.x - 48} y={pf.y - 10} width={96} height={20} rx={5}
                fill={sel ? "#1d4ed8" : memu ? "#134e4a" : "#1e293b"}
                stroke={memu ? "#14b8a6" : "#475569"} strokeWidth={1.5} />
              <text x={pf.x} y={pf.y + 4} textAnchor="middle" fontSize={10}
                fill={memu ? "#5eead4" : "#cbd5e1"}>
                P{pf.number}{memu ? " · MEMU" : ""}
              </text>
            </g>
          );
        })}

        {/* --- Stations --- */}
        {[...layout.stations.values()].map((st) => {
          const isJn = st.id === twin.junction.code;
          const sel = selId === `node:${st.id}`;
          return (
            <g key={st.id} className="cursor-pointer"
              onClick={() => onSelect({ kind: isJn ? "junction" : "station", node: st as GraphNode })}>
              <circle cx={st.x} cy={st.y} r={isJn ? 13 : 6}
                fill={sel ? "#f8fafc" : isJn ? "#0ea5e9" : "#0f172a"}
                stroke={isJn ? "#38bdf8" : "#64748b"} strokeWidth={2} />
              <text x={st.x} y={st.y - (isJn ? 20 : 12)} textAnchor="middle"
                fontSize={isJn ? 13 : 9.5} fontWeight={isJn ? 700 : 500} fill="#e2e8f0">
                {st.id}
              </text>
            </g>
          );
        })}

        {/* --- Live trains (animated) --- */}
        {trains.map((t) => {
          const p = layout.edgePoint(t.from_station, t.to_station, t.frac);
          const sel = selId === `train:${t.id}`;
          const color = TYPE_COLOR[t.type] ?? "#64748b";
          const atPlat = t.status === "at_platform";
          return (
            <g key={t.id} className="cursor-pointer"
              style={{ transform: `translate(${p.x}px, ${p.y}px)`, transition: "transform 1s linear" }}
              onClick={() => onSelect({ kind: "train", train: t })}>
              {atPlat && <circle r={13} fill={color} opacity={0.25}><animate attributeName="r" values="9;16;9" dur="1.6s" repeatCount="indefinite" /></circle>}
              <rect x={-8} y={-8} width={16} height={16} rx={4} fill={color}
                stroke={sel ? "#f8fafc" : "#0b1220"} strokeWidth={sel ? 3 : 1.5} />
              <title>{t.id} — {t.name} ({t.status})</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function ResourceBox({ node, label, stroke, selected, onClick }: {
  node: { x: number; y: number }; label: string; stroke: string; selected: boolean; onClick: () => void;
}) {
  return (
    <g className="cursor-pointer" onClick={onClick}>
      <rect x={node.x - 62} y={node.y - 16} width={124} height={32} rx={7}
        fill="#0f172a" stroke={stroke} strokeWidth={selected ? 2.5 : 1.5} strokeDasharray="5 3" />
      <text x={node.x} y={node.y + 4} textAnchor="middle" fontSize={11} fontWeight={600} fill={stroke}>
        {label}
      </text>
    </g>
  );
}
