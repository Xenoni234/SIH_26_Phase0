import { useMemo } from "react";
import type { GraphNode, Selection, SimTrain, TwinResponse } from "../types";
import { VIEW, computeLayout, TYPE_COLOR } from "../lib/layout";
import type { Palette } from "../lib/theme";

interface Props {
  twin: TwinResponse;
  trains: SimTrain[];
  palette: Palette;
  selection: Selection;
  onSelect: (sel: Selection) => void;
}

const CORRIDOR_LABEL: Record<string, string> = {
  north: "↑ Virar · Dahanu Rd",
  western: "Mumbai · Churchgate",
  diva: "Diva · Panvel",
};

export default function TwinMap({ twin, trains, palette, selection, onSelect }: Props) {
  const layout = useMemo(() => computeLayout(twin.graph.nodes, twin.junction.code), [twin]);

  const selId =
    selection?.kind === "train" ? `train:${selection.train.id}`
    : selection && "node" in selection ? `node:${selection.node.id}` : null;

  const endpoints = useMemo(() => {
    const far: Record<string, { id: string; x: number; y: number }> = {};
    for (const s of layout.stations.values()) {
      const c = s.corridor;
      if (!c || s.id === twin.junction.code) continue;
      if (!far[c] || (s.km ?? 0) > (layout.stations.get(far[c].id)?.km ?? 0)) far[c] = { id: s.id, x: s.x, y: s.y };
    }
    return far;
  }, [layout, twin.junction.code]);

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="w-full" role="img" aria-label="Vasai Road live twin">
        <defs>
          <radialGradient id="glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={palette.glow} stopOpacity="0.18" />
            <stop offset="100%" stopColor={palette.glow} stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx={layout.center.x} cy={layout.center.y} r={150} fill="url(#glow)" />

        {twin.graph.edges.filter((e) => e.kind === "block").map((e, i) => {
          const a = layout.stations.get(e.source);
          const b = layout.stations.get(e.target);
          if (!a || !b) return null;
          return <line key={`e${i}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={palette.edge} strokeWidth={5} strokeLinecap="round" />;
        })}

        {Object.entries(endpoints).map(([corr, p]) => (
          <text key={corr} x={p.x} y={p.y + (corr === "north" ? -22 : 24)} textAnchor="middle" fontSize={11} fontWeight={600} fill={palette.labelMuted}>
            {CORRIDOR_LABEL[corr] ?? corr}
          </text>
        ))}

        {layout.yard && (
          <ResourceBox p={palette} node={layout.yard} label="North Yard" stroke="#a78bfa"
            selected={selId === `node:${layout.yard.id}`} onClick={() => onSelect({ kind: "yard", node: layout.yard! })} />
        )}
        {layout.freight && (
          <ResourceBox p={palette} node={layout.freight} label="Freight / Goods" stroke={palette.yardStroke}
            selected={selId === `node:${layout.freight.id}`} onClick={() => onSelect({ kind: "freight", node: layout.freight! })} />
        )}

        {layout.platforms.map((pf) => {
          const memu = (pf.number ?? 0) >= 6;
          const sel = selId === `node:${pf.id}`;
          return (
            <g key={pf.id} className="cursor-pointer" onClick={() => onSelect({ kind: "platform", node: pf })}>
              <rect x={pf.x - 48} y={pf.y - 10} width={96} height={20} rx={5}
                fill={sel ? "#2563eb" : memu ? palette.memuFill : palette.platformFill}
                stroke={memu ? palette.memuStroke : palette.platformStroke} strokeWidth={1.5} />
              <text x={pf.x} y={pf.y + 4} textAnchor="middle" fontSize={10} fill={memu ? palette.memuText : palette.platformText}>
                P{pf.number}{memu ? " · MEMU" : ""}
              </text>
            </g>
          );
        })}

        {[...layout.stations.values()].map((st) => {
          const isJn = st.id === twin.junction.code;
          const sel = selId === `node:${st.id}`;
          return (
            <g key={st.id} className="cursor-pointer" onClick={() => onSelect({ kind: isJn ? "junction" : "station", node: st as GraphNode })}>
              <circle cx={st.x} cy={st.y} r={isJn ? 13 : 6}
                fill={sel ? palette.occStroke : isJn ? palette.junctionFill : palette.stationFill}
                stroke={isJn ? palette.junctionStroke : palette.stationStroke} strokeWidth={2} />
              <text x={st.x} y={st.y - (isJn ? 20 : 12)} textAnchor="middle" fontSize={isJn ? 13 : 9.5} fontWeight={isJn ? 700 : 500} fill={palette.stationText}>
                {st.id}
              </text>
            </g>
          );
        })}

        {trains.map((t) => {
          const p = layout.edgePoint(t.from_station, t.to_station, t.frac);
          const sel = selId === `train:${t.id}`;
          const color = TYPE_COLOR[t.type] ?? "#64748b";
          return (
            <g key={t.id} className="cursor-pointer"
              style={{ transform: `translate(${p.x}px, ${p.y}px)`, transition: "transform 1s linear" }}
              onClick={() => onSelect({ kind: "train", train: t })}>
              {t.at_platform && <circle r={13} fill={color} opacity={0.25}><animate attributeName="r" values="9;16;9" dur="1.6s" repeatCount="indefinite" /></circle>}
              <rect x={-8} y={-8} width={16} height={16} rx={4} fill={color} stroke={sel ? palette.occStroke : palette.trainStroke} strokeWidth={sel ? 3 : 1.5} />
              <title>{t.id} — {t.name} ({t.status})</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function ResourceBox({ p, node, label, stroke, selected, onClick }: {
  p: Palette; node: { x: number; y: number }; label: string; stroke: string; selected: boolean; onClick: () => void;
}) {
  return (
    <g className="cursor-pointer" onClick={onClick}>
      <rect x={node.x - 62} y={node.y - 16} width={124} height={32} rx={7} fill={p.resourceFill} stroke={stroke} strokeWidth={selected ? 2.5 : 1.5} strokeDasharray="5 3" />
      <text x={node.x} y={node.y + 4} textAnchor="middle" fontSize={11} fontWeight={600} fill={stroke}>{label}</text>
    </g>
  );
}
