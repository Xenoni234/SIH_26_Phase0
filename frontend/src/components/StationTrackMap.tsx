import { useMemo } from "react";
import type { GraphNode, Selection, SimTrain } from "../types";
import { TYPE_COLOR } from "../lib/layout";

interface Props {
  trains: SimTrain[];
  selection: Selection;
  onSelect: (sel: Selection) => void;
}

/**
 * Realistic top-view of Vasai Road (BSR): island platforms with two faces,
 * PF1 set back (side platform), scissors crossovers at both throats, the Diva
 * line diverging east, and the freight/goods yard. North (Virar/Dahanu) is up,
 * Churchgate/Mumbai is down.
 */
const VIEW = { w: 1160, h: 1000 };
const THROAT_TOP = 150;
const THROAT_BOT = 860;
const NORTH_X = THROAT_TOP + 40; // crossover band (north)
const SOUTH_X = THROAT_BOT - 40; // crossover band (south)

// Track x per platform number the engine emits (1..7).
const TRACK_X: Record<number, number> = { 1: 175, 2: 255, 3: 415, 4: 475, 5: 575, 6: 635, 7: 735 };
const ALL_TRACKS = [175, 255, 307, 415, 475, 575, 635, 735]; // 307 = PF2 island 2B face

// Platform bodies (islands / side platforms).
interface Body { x: number; w: number; y0: number; y1: number; faces: { label: string; x: number; memu?: boolean }[]; }
const BODIES: Body[] = [
  // PF1 — side platform, set BACK to the south
  { x: 132, w: 34, y0: 520, y1: 780, faces: [{ label: "1", x: 175 }] },
  // Island: 2A | 2B
  { x: 263, w: 46, y0: 330, y1: 720, faces: [{ label: "2A", x: 255 }, { label: "2B", x: 307 }] },
  // Island: 3 | 4
  { x: 423, w: 44, y0: 330, y1: 720, faces: [{ label: "3", x: 415 }, { label: "4", x: 475 }] },
  // Island: 5 | 6  (6 is MEMU)
  { x: 583, w: 44, y0: 330, y1: 720, faces: [{ label: "5", x: 575 }, { label: "6", x: 635, memu: true }] },
  // PF7 — MEMU side platform (east)
  { x: 743, w: 34, y0: 330, y1: 720, faces: [{ label: "7", x: 735, memu: true }] },
];

const DIVA_A = { x: 735, y: 620 };
const DIVA_B = { x: 1090, y: 940 };
const YARD = { x: 850, y: 150, w: 250, h: 150 };

const bodyOf = (pf: number): Body =>
  BODIES.find((b) => b.faces.some((f) => Math.abs(f.x - (TRACK_X[pf] ?? 475)) < 30)) ?? BODIES[2];

function trainPos(t: SimTrain, idx: number): { x: number; y: number } {
  if (t.type === "freight") {
    const row = idx % 4;
    return { x: YARD.x + 40 + (idx % 3) * 60, y: YARD.y + 34 + row * 30 };
  }
  if (t.corridor === "diva" && !t.at_platform) {
    const p = Math.min(1, (t.km_from_bsr ?? 0) / 22);
    return { x: DIVA_A.x + (DIVA_B.x - DIVA_A.x) * p, y: DIVA_A.y + (DIVA_B.y - DIVA_A.y) * p };
  }
  const pf = t.platform ?? 4;
  const x = TRACK_X[pf] ?? 475;
  const body = bodyOf(pf);
  if (t.at_platform) return { x, y: (body.y0 + body.y1) / 2 };
  const d = Math.min(THROAT_TOP > 0 ? 250 : 250, (t.km_from_bsr ?? 0) * 18);
  if (t.corridor === "north") return { x, y: body.y0 - d };
  return { x, y: body.y1 + d };
}

export default function StationTrackMap({ trains, selection, onSelect }: Props) {
  const occupied = useMemo(() => {
    const s = new Set<number>();
    for (const t of trains) if (t.at_platform && t.platform) s.add(t.platform);
    return s;
  }, [trains]);
  const selId = selection?.kind === "train" ? `train:${selection.train.id}` : null;

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950 shadow-xl">
      <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="w-full" role="img" aria-label="Vasai Road station top view">
        {/* direction + side labels */}
        <text x={VIEW.w / 2} y={38} textAnchor="middle" fontSize={15} fontWeight={700} fill="#cbd5e1">↑ Virar · Dahanu Road (North)</text>
        <text x={VIEW.w / 2} y={968} textAnchor="middle" fontSize={15} fontWeight={700} fill="#cbd5e1">↓ Andheri · Churchgate (Mumbai)</text>
        <text x={24} y={500} textAnchor="middle" fontSize={12} fontWeight={600} fill="#475569" transform="rotate(-90 24 500)">WEST</text>
        <text x={1146} y={520} textAnchor="middle" fontSize={12} fontWeight={600} fill="#475569" transform="rotate(-90 1146 520)">EAST</text>

        {/* running tracks */}
        {ALL_TRACKS.map((x) => (
          <line key={x} x1={x} y1={THROAT_TOP} x2={x} y2={THROAT_BOT} stroke="#273449" strokeWidth={4} strokeLinecap="round" />
        ))}

        {/* scissors crossovers (north + south throats) — incl. the 4/5 & 6/7 area */}
        {([[175, 255], [307, 415], [475, 575], [635, 735]] as const).map(([a, b], i) => (
          <g key={i} stroke="#3b5573" strokeWidth={2.5}>
            <Scissors xa={a} xb={b} y0={NORTH_X - 26} y1={NORTH_X + 26} />
            <Scissors xa={a} xb={b} y0={SOUTH_X - 26} y1={SOUTH_X + 26} />
          </g>
        ))}

        {/* Diva branch (east) + connector from PF7 */}
        <path d={`M735 640 C 820 720, 960 820, ${DIVA_B.x} ${DIVA_B.y}`} fill="none" stroke="#334155" strokeWidth={5} strokeLinecap="round" />
        <text x={DIVA_B.x - 8} y={DIVA_B.y - 8} textAnchor="end" fontSize={12} fontWeight={600} fill="#64748b">Diva · Panvel →</text>

        {/* Freight / Goods yard */}
        <g>
          <path d={`M735 ${THROAT_TOP} C 780 200, 830 210, ${YARD.x + 20} ${YARD.y + YARD.h / 2}`} fill="none" stroke="#334155" strokeWidth={3} />
          <rect x={YARD.x} y={YARD.y} width={YARD.w} height={YARD.h} rx={10} fill="#1a1206" stroke="#d97706" strokeWidth={1.5} strokeDasharray="6 4" />
          {[0, 1, 2, 3].map((i) => (
            <line key={i} x1={YARD.x + 18} y1={YARD.y + 34 + i * 30} x2={YARD.x + YARD.w - 18} y2={YARD.y + 34 + i * 30} stroke="#3f2d10" strokeWidth={3} />
          ))}
          <text x={YARD.x + YARD.w / 2} y={YARD.y + 18} textAnchor="middle" fontSize={12} fontWeight={700} fill="#f59e0b">Freight / Goods Yard</text>
        </g>

        {/* platform bodies + face labels */}
        {BODIES.map((b, i) => (
          <g key={i}>
            <rect x={b.x} y={b.y0} width={b.w} height={b.y1 - b.y0} rx={7} fill="#0f1a2b" stroke="#243247" strokeWidth={1.5} />
            <text x={b.x + b.w / 2} y={(b.y0 + b.y1) / 2} textAnchor="middle" fontSize={10} fill="#33465e"
              transform={`rotate(-90 ${b.x + b.w / 2} ${(b.y0 + b.y1) / 2})`}>PLATFORM</text>
            {b.faces.map((f) => {
              const occ = occupied.has(labelToPf(f.label));
              return (
                <g key={f.label} className="cursor-pointer" onClick={() => onSelect({ kind: "platform", node: platformNode(f.label, !!f.memu) })}>
                  <circle cx={f.x} cy={b.y0 - 16} r={12} fill={f.memu ? "#0f2e2b" : "#111c2e"} stroke={occ ? "#38bdf8" : f.memu ? "#14b8a6" : "#334155"} strokeWidth={occ ? 2.5 : 1.5} />
                  <text x={f.x} y={b.y0 - 12} textAnchor="middle" fontSize={9} fontWeight={700} fill={f.memu ? "#5eead4" : "#e2e8f0"}>{f.label}</text>
                  <text x={f.x} y={b.y1 + 16} textAnchor="middle" fontSize={8} fill="#5b6b82">{f.memu ? "MEMU" : "slow/fast"}</text>
                </g>
              );
            })}
          </g>
        ))}

        {/* trains */}
        {trains.map((t, i) => {
          const p = trainPos(t, i);
          const sel = selId === `train:${t.id}`;
          const color = TYPE_COLOR[t.type] ?? "#64748b";
          return (
            <g key={t.id} className="cursor-pointer"
              style={{ transform: `translate(${p.x}px, ${p.y}px)`, transition: "transform 1s linear" }}
              onClick={() => onSelect({ kind: "train", train: t })}>
              {t.at_platform && <circle r={13} fill={color} opacity={0.25}><animate attributeName="r" values="10;17;10" dur="1.6s" repeatCount="indefinite" /></circle>}
              <rect x={-15} y={-7} width={30} height={14} rx={4} fill={color} stroke={sel ? "#f8fafc" : "#0b1220"} strokeWidth={sel ? 3 : 1.5} />
              <text x={0} y={3.5} textAnchor="middle" fontSize={8} fontWeight={700} fill="#0b1220">{t.id.slice(-4)}</text>
              <title>{t.id} — {t.name} · PF{t.platform ?? "?"} · {t.status}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function Scissors({ xa, xb, y0, y1 }: { xa: number; xb: number; y0: number; y1: number }) {
  return (
    <>
      <line x1={xa} y1={y0} x2={xb} y2={y1} />
      <line x1={xa} y1={y1} x2={xb} y2={y0} />
    </>
  );
}

function labelToPf(label: string): number {
  const n = parseInt(label.replace(/[^0-9]/g, ""), 10);
  return Number.isNaN(n) ? 0 : n;
}

function platformNode(label: string, memu: boolean): GraphNode {
  return {
    id: `BSR-P${label}`, kind: "platform", number: labelToPf(label), station: "BSR",
    serves: memu ? ["memu", "diva"] : ["western", "north"],
  };
}
