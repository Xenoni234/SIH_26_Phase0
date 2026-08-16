import { useMemo } from "react";
import type { GraphNode, Selection, SimTrain } from "../types";
import { TYPE_COLOR } from "../lib/layout";

interface Props {
  trains: SimTrain[];
  selection: Selection;
  onSelect: (sel: Selection) => void;
}

// Track-wise station schematic: North (Virar/Dahanu) at top, Churchgate/Mumbai
// at bottom, 7 parallel platforms (PF1–5 slow/fast, PF6–7 MEMU), Diva branch east.
const VIEW = { w: 980, h: 900 };
const TOP_Y = 96;
const BOT_Y = 812;
const PLAT_Y0 = 384;
const PLAT_Y1 = 524;
const MID_Y = (PLAT_Y0 + PLAT_Y1) / 2;

const colX = (n: number) => 150 + (n - 1) * 92; // PF1..PF7 -> 150..702
const DIVA_START = { x: colX(7) + 30, y: MID_Y };
const DIVA_END = { x: 948, y: 868 };

function trainPos(t: SimTrain): { x: number; y: number } {
  const pf = t.platform ?? 4;
  const x = colX(pf);
  if (t.at_platform) return { x, y: MID_Y };
  const d = Math.min(300, (t.km_from_bsr ?? 0) * 20);
  if (t.corridor === "diva") {
    const p = Math.min(1, d / 300);
    return { x: DIVA_START.x + (DIVA_END.x - DIVA_START.x) * p, y: DIVA_START.y + (DIVA_END.y - DIVA_START.y) * p };
  }
  if (t.corridor === "north") return { x, y: PLAT_Y0 - d }; // top approach
  return { x, y: PLAT_Y1 + d }; // Mumbai/south approach
}

export default function StationTrackMap({ trains, selection, onSelect }: Props) {
  const occupied = useMemo(() => {
    const m: Record<number, SimTrain> = {};
    for (const t of trains) if (t.at_platform && t.platform) m[t.platform] = t;
    return m;
  }, [trains]);

  const selId = selection?.kind === "train" ? `train:${selection.train.id}` : null;

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 shadow-xl">
      <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="w-full" role="img" aria-label="Vasai Road station track diagram">
        {/* direction labels */}
        <text x={VIEW.w / 2} y={40} textAnchor="middle" fontSize={15} fontWeight={700} fill="#cbd5e1">↑ Virar · Dahanu Road (North)</text>
        <text x={VIEW.w / 2} y={870} textAnchor="middle" fontSize={15} fontWeight={700} fill="#cbd5e1">↓ Andheri · Churchgate (Mumbai)</text>
        <text x={26} y={MID_Y} textAnchor="middle" fontSize={12} fontWeight={600} fill="#475569" transform={`rotate(-90 26 ${MID_Y})`}>WEST</text>
        <text x={958} y={MID_Y - 120} textAnchor="middle" fontSize={12} fontWeight={600} fill="#475569" transform={`rotate(-90 958 ${MID_Y - 120})`}>EAST</text>

        {/* Diva branch track */}
        <line x1={DIVA_START.x} y1={DIVA_START.y} x2={DIVA_END.x} y2={DIVA_END.y} stroke="#334155" strokeWidth={5} strokeLinecap="round" />
        <text x={DIVA_END.x - 6} y={DIVA_END.y + 20} textAnchor="end" fontSize={12} fontWeight={600} fill="#64748b">Diva · Panvel →</text>

        {/* platforms + their running tracks */}
        {Array.from({ length: 7 }, (_, i) => i + 1).map((n) => {
          const x = colX(n);
          const memu = n >= 6;
          const occ = occupied[n];
          const sel = selection?.kind === "platform" && selection.node.id === `BSR-P${n}`;
          return (
            <g key={n}>
              {/* running line through the platform */}
              <line x1={x} y1={TOP_Y} x2={x} y2={BOT_Y} stroke="#273449" strokeWidth={4} strokeLinecap="round" />
              {/* platform body */}
              <g className="cursor-pointer" onClick={() => onSelect({ kind: "platform", node: platformNode(n) })}>
                <rect x={x - 24} y={PLAT_Y0} width={48} height={PLAT_Y1 - PLAT_Y0} rx={8}
                  fill={occ ? "#1e3a5f" : memu ? "#0f2e2b" : "#111c2e"}
                  stroke={sel ? "#f8fafc" : occ ? "#38bdf8" : memu ? "#14b8a6" : "#334155"}
                  strokeWidth={sel || occ ? 2.5 : 1.5} />
                <text x={x} y={PLAT_Y0 - 12} textAnchor="middle" fontSize={13} fontWeight={700} fill={memu ? "#5eead4" : "#e2e8f0"}>PF{n}</text>
                <text x={x} y={PLAT_Y1 + 20} textAnchor="middle" fontSize={9} fill="#64748b">{memu ? "MEMU" : "slow/fast"}</text>
                {/* vertical PF label inside bar */}
                <text x={x} y={MID_Y} textAnchor="middle" fontSize={10} fill="#334155" transform={`rotate(-90 ${x} ${MID_Y})`}>PLATFORM {n}</text>
              </g>
            </g>
          );
        })}

        {/* trains */}
        {trains.map((t) => {
          const p = trainPos(t);
          const sel = selId === `train:${t.id}`;
          const color = TYPE_COLOR[t.type] ?? "#64748b";
          return (
            <g key={t.id} className="cursor-pointer"
              style={{ transform: `translate(${p.x}px, ${p.y}px)`, transition: "transform 1s linear" }}
              onClick={() => onSelect({ kind: "train", train: t })}>
              {t.at_platform && <circle r={13} fill={color} opacity={0.25}><animate attributeName="r" values="10;17;10" dur="1.6s" repeatCount="indefinite" /></circle>}
              <rect x={-14} y={-7} width={28} height={14} rx={4} fill={color}
                stroke={sel ? "#f8fafc" : "#0b1220"} strokeWidth={sel ? 3 : 1.5} />
              <text x={0} y={3.5} textAnchor="middle" fontSize={8} fontWeight={700} fill="#0b1220">{t.id.slice(-4)}</text>
              <title>{t.id} — {t.name} · PF{t.platform ?? "?"} · {t.status}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function platformNode(n: number): GraphNode {
  return {
    id: `BSR-P${n}`, kind: "platform", number: n, station: "BSR",
    serves: n >= 6 ? ["memu", "diva"] : ["western", "north"],
  };
}
