// Computes schematic SVG positions for the Vasai twin from the graph.
// Not geographic — a stylized junction diagram: BSR centre, North up,
// Western lower-left, Diva lower-right; stations spaced evenly by order.

import type { GraphNode, TrainState } from "../types";

export interface Pt {
  x: number;
  y: number;
}

export const VIEW = { w: 1000, h: 720 };
const CENTER: Pt = { x: 500, y: 360 };
const MAX_STEP = 72; // px between consecutive stations (short branches)

// Unit-ish direction per corridor (SVG y grows downward) + how far the branch
// may reach from centre, so long corridors stay on-canvas.
const DIR: Record<string, Pt & { reach: number }> = {
  north: { x: 0, y: -1, reach: 300 },
  western: { x: -0.82, y: 0.57, reach: 340 },
  diva: { x: 0.82, y: 0.57, reach: 330 },
};

export interface Layout {
  center: Pt;
  stations: Map<string, GraphNode & Pt>;
  platforms: (GraphNode & Pt)[];
  yard?: GraphNode & Pt;
  freight?: GraphNode & Pt;
  trainAt: (t: TrainState) => Pt;
  /** Interpolate a live train position between two station nodes. */
  edgePoint: (from: string, to: string, frac: number) => Pt;
}

export function computeLayout(nodes: GraphNode[], junctionCode: string): Layout {
  const stations = new Map<string, GraphNode & Pt>();

  // Group station nodes by corridor, drop the junction itself.
  const byCorridor: Record<string, GraphNode[]> = {};
  for (const n of nodes) {
    if (n.kind !== "station") continue;
    if (n.id === junctionCode) continue;
    const c = n.corridor ?? "western";
    (byCorridor[c] ??= []).push(n);
  }

  // Junction at centre.
  const jn = nodes.find((n) => n.id === junctionCode);
  if (jn) stations.set(junctionCode, { ...jn, ...CENTER });

  for (const [corridor, list] of Object.entries(byCorridor)) {
    const dir = DIR[corridor] ?? DIR.western;
    const sorted = list.slice().sort((a, b) => (a.km ?? 0) - (b.km ?? 0));
    // Adaptive spacing: long branches shrink to stay within `reach`.
    const step = Math.min(MAX_STEP, dir.reach / Math.max(sorted.length, 1));
    sorted.forEach((node, i) => {
      const d = (i + 1) * step;
      stations.set(node.id, {
        ...node,
        x: CENTER.x + dir.x * d,
        y: CENTER.y + dir.y * d,
      });
    });
  }

  // Platforms: stacked vertically just left of the junction.
  const pfNodes = nodes
    .filter((n) => n.kind === "platform")
    .sort((a, b) => (a.number ?? 0) - (b.number ?? 0));
  const pfTop = CENTER.y - ((pfNodes.length - 1) * 26) / 2;
  const platforms = pfNodes.map((n, i) => ({
    ...n,
    x: CENTER.x - 150,
    y: pfTop + i * 26,
  }));

  // Yard (up-left, parallel to North) and Freight (down-right, Diva side).
  const yardNode = nodes.find((n) => n.kind === "yard");
  const freightNode = nodes.find((n) => n.kind === "freight");
  const yard = yardNode ? { ...yardNode, x: CENTER.x - 120, y: CENTER.y - 210 } : undefined;
  const freight = freightNode
    ? { ...freightNode, x: CENTER.x + 250, y: CENTER.y + 230 }
    : undefined;

  const trainAt = (t: TrainState): Pt => {
    const key = t.current_station ?? "";
    const at = stations.get(key);
    const base = at ?? CENTER;
    // deterministic jitter by train id so co-located markers don't fully overlap
    const h = [...t.train_id].reduce((a, c) => a + c.charCodeAt(0), 0);
    return { x: base.x + ((h % 5) - 2) * 7, y: base.y - 14 - ((h % 3) * 7) };
  };

  const edgePoint = (from: string, to: string, frac: number): Pt => {
    const a = stations.get(from) ?? { ...CENTER };
    const b = stations.get(to) ?? { ...CENTER };
    const f = Math.max(0, Math.min(1, frac));
    return { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f };
  };

  return { center: CENTER, stations, platforms, yard, freight, trainAt, edgePoint };
}

export const TYPE_COLOR: Record<string, string> = {
  express: "#dc2626",
  local: "#2563eb",
  memu: "#0d9488",
  freight: "#d97706",
  passenger: "#64748b",
  yard: "#7c3aed",
};
