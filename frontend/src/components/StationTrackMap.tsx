import { useMemo } from "react";
import type { GraphNode, Selection, SimTrain } from "../types";
import { TYPE_COLOR } from "../lib/layout";
import type { Palette } from "../lib/theme";

interface Props {
  trains: SimTrain[];
  palette: Palette;
  selection: Selection;
  onSelect: (sel: Selection) => void;
}

const VIEW = { w: 1160, h: 1000 };
const TOP_Y = 120;
const BOT_Y = 890;
const NORTH_X = TOP_Y + 70;
const SOUTH_X = BOT_Y - 70;

const TRACK_X: Record<number, number> = { 1: 175, 2: 255, 3: 415, 4: 475, 5: 575, 6: 635, 7: 735 };
const ALL_TRACKS = [175, 255, 307, 415, 475, 575, 635, 735]; // 307 = PF2 island 2B face

// Platform bodies with realistic (varied) lengths; PF1 is a set-back side platform.
interface Body { x: number; w: number; y0: number; y1: number; faces: { label: string; x: number; memu?: boolean }[]; }
const BODIES: Body[] = [
  { x: 132, w: 34, y0: 470, y1: 812, faces: [{ label: "1", x: 175 }] },                                   // long, set back
  { x: 263, w: 46, y0: 300, y1: 742, faces: [{ label: "2A", x: 255 }, { label: "2B", x: 307 }] },          // longest island
  { x: 423, w: 44, y0: 320, y1: 720, faces: [{ label: "3", x: 415 }, { label: "4", x: 475 }] },
  { x: 583, w: 44, y0: 320, y1: 720, faces: [{ label: "5", x: 575 }, { label: "6", x: 635, memu: true }] },
  { x: 743, w: 34, y0: 372, y1: 664, faces: [{ label: "7", x: 735, memu: true }] },                        // shorter MEMU bay
];

const DIVA_A = { x: 735, y: 640 };
const DIVA_B = { x: 1092, y: 946 };
const YARD = { x: 858, y: 150, w: 250, h: 150 };

const bodyOf = (pf: number): Body =>
  BODIES.find((b) => b.faces.some((f) => Math.abs(f.x - (TRACK_X[pf] ?? 475)) < 30)) ?? BODIES[2];

const hash = (s: string) => [...s].reduce((a, c) => a + c.charCodeAt(0), 0);

function trainPos(t: SimTrain): { x: number; y: number } {
  if (t.type === "freight") {
    const h = hash(t.id);
    return { x: YARD.x + 46 + (h % 3) * 70, y: YARD.y + 40 + (h % 4) * 28 };
  }
  if (t.corridor === "diva" && !t.at_platform) {
    const p = Math.min(1, (t.km_from_bsr ?? 0) / 22);
    return { x: DIVA_A.x + (DIVA_B.x - DIVA_A.x) * p, y: DIVA_A.y + (DIVA_B.y - DIVA_A.y) * p };
  }
  const pf = t.platform ?? 4;
  const x = TRACK_X[pf] ?? 475;
  const b = bodyOf(pf);
  if (t.at_platform) return { x, y: (b.y0 + b.y1) / 2 };
  const d = Math.min(250, (t.km_from_bsr ?? 0) * 18);
  return t.corridor === "north" ? { x, y: b.y0 - d } : { x, y: b.y1 + d };
}

export default function StationTrackMap({ trains, palette, selection, onSelect }: Props) {
  const occupied = useMemo(() => {
    const s = new Set<number>();
    for (const t of trains) if (t.at_platform && t.platform) s.add(t.platform);
    return s;
  }, [trains]);
  const selId = selection?.kind === "train" ? `train:${selection.train.id}` : null;

  // sleeper ties along every track (minute detailing)
  const ties = useMemo(() => {
    const rows: number[] = [];
    for (let y = TOP_Y + 12; y < BOT_Y; y += 30) rows.push(y);
    return rows;
  }, []);

  return (
    <div className="relative w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <svg viewBox={`0 0 ${VIEW.w} ${VIEW.h}`} className="w-full" role="img" aria-label="Vasai Road station top view">
        <text x={VIEW.w / 2} y={40} textAnchor="middle" fontSize={15} fontWeight={700} fill={palette.stationText}>↑ Virar · Dahanu Road (North)</text>
        <text x={VIEW.w / 2} y={978} textAnchor="middle" fontSize={15} fontWeight={700} fill={palette.stationText}>↓ Andheri · Churchgate (Mumbai)</text>
        <text x={24} y={500} textAnchor="middle" fontSize={12} fontWeight={600} fill={palette.labelMuted} transform="rotate(-90 24 500)">WEST</text>
        <text x={1146} y={520} textAnchor="middle" fontSize={12} fontWeight={600} fill={palette.labelMuted} transform="rotate(-90 1146 520)">EAST</text>

        {/* tracks + sleeper ties */}
        {ALL_TRACKS.map((x) => (
          <g key={x}>
            {ties.map((y) => (
              <line key={y} x1={x - 6} y1={y} x2={x + 6} y2={y} stroke={palette.tie} strokeWidth={2} />
            ))}
            <line x1={x} y1={TOP_Y} x2={x} y2={BOT_Y} stroke={palette.track} strokeWidth={4} strokeLinecap="round" />
          </g>
        ))}

        {/* scissors crossovers (both throats) */}
        {([[175, 255], [307, 415], [475, 575], [635, 735]] as const).map(([a, b], i) => (
          <g key={i} stroke={palette.crossover} strokeWidth={2.5}>
            <line x1={a} y1={NORTH_X - 26} x2={b} y2={NORTH_X + 26} />
            <line x1={a} y1={NORTH_X + 26} x2={b} y2={NORTH_X - 26} />
            <line x1={a} y1={SOUTH_X - 26} x2={b} y2={SOUTH_X + 26} />
            <line x1={a} y1={SOUTH_X + 26} x2={b} y2={SOUTH_X - 26} />
          </g>
        ))}

        {/* Diva branch */}
        <path d={`M735 660 C 820 740, 960 840, ${DIVA_B.x} ${DIVA_B.y}`} fill="none" stroke={palette.track} strokeWidth={5} strokeLinecap="round" />
        <text x={DIVA_B.x - 8} y={DIVA_B.y - 8} textAnchor="end" fontSize={12} fontWeight={600} fill={palette.labelMuted}>Diva · Panvel →</text>

        {/* Freight / Goods yard */}
        <g>
          <path d={`M735 ${TOP_Y} C 780 170, 830 180, ${YARD.x + 20} ${YARD.y + YARD.h / 2}`} fill="none" stroke={palette.track} strokeWidth={3} />
          <rect x={YARD.x} y={YARD.y} width={YARD.w} height={YARD.h} rx={10} fill={palette.yardFill} stroke={palette.yardStroke} strokeWidth={1.5} strokeDasharray="6 4" />
          {[0, 1, 2, 3].map((i) => (
            <line key={i} x1={YARD.x + 18} y1={YARD.y + 40 + i * 28} x2={YARD.x + YARD.w - 18} y2={YARD.y + 40 + i * 28} stroke={palette.yardSiding} strokeWidth={3} />
          ))}
          <text x={YARD.x + YARD.w / 2} y={YARD.y + 20} textAnchor="middle" fontSize={12} fontWeight={700} fill={palette.yardText}>Freight / Goods Yard</text>
        </g>

        {/* platform bodies + faces */}
        {BODIES.map((b, i) => (
          <g key={i}>
            <rect x={b.x} y={b.y0} width={b.w} height={b.y1 - b.y0} rx={7} fill={palette.platformFill} stroke={palette.platformStroke} strokeWidth={1.5} />
            <text x={b.x + b.w / 2} y={(b.y0 + b.y1) / 2} textAnchor="middle" fontSize={10} fill={palette.labelMuted}
              transform={`rotate(-90 ${b.x + b.w / 2} ${(b.y0 + b.y1) / 2})`} opacity={0.7}>PLATFORM</text>
            {b.faces.map((f) => {
              const occ = occupied.has(labelToPf(f.label));
              return (
                <g key={f.label} className="cursor-pointer" onClick={() => onSelect({ kind: "platform", node: platformNode(f.label, !!f.memu) })}>
                  <circle cx={f.x} cy={b.y0 - 16} r={12} fill={f.memu ? palette.memuFill : palette.platformFill}
                    stroke={occ ? palette.occStroke : f.memu ? palette.memuStroke : palette.platformStroke} strokeWidth={occ ? 2.5 : 1.5} />
                  <text x={f.x} y={b.y0 - 12} textAnchor="middle" fontSize={9} fontWeight={700} fill={f.memu ? palette.memuText : palette.platformText}>{f.label}</text>
                  <text x={f.x} y={b.y1 + 16} textAnchor="middle" fontSize={8} fill={palette.labelMuted}>{f.memu ? "MEMU" : "slow/fast"}</text>
                </g>
              );
            })}
          </g>
        ))}

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
              <rect x={-15} y={-7} width={30} height={14} rx={4} fill={color} stroke={sel ? palette.occStroke : palette.trainStroke} strokeWidth={sel ? 3 : 1.5} />
              <text x={0} y={3.5} textAnchor="middle" fontSize={8} fontWeight={700} fill={palette.trainLabel}>{t.id.slice(-4)}</text>
              <title>{t.id} — {t.name} · {t.platform ? `PF${t.platform} · ` : ""}{t.status}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function labelToPf(label: string): number {
  const n = parseInt(label.replace(/[^0-9]/g, ""), 10);
  return Number.isNaN(n) ? 0 : n;
}
function platformNode(label: string, memu: boolean): GraphNode {
  return { id: `BSR-P${label}`, kind: "platform", number: labelToPf(label), station: "BSR", serves: memu ? ["memu", "diva"] : ["western", "north"] };
}
