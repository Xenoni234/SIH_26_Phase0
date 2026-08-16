// SVG color palettes for the two maps. Chrome (cards/text) uses Tailwind
// light-first classes with `dark:` variants; the SVGs read these tokens.

export interface Palette {
  glow: string;
  track: string;
  tie: string; // sleeper ticks
  crossover: string;
  edge: string; // corridor blocks
  platformFill: string;
  platformStroke: string;
  platformText: string;
  memuFill: string;
  memuStroke: string;
  memuText: string;
  stationFill: string;
  stationStroke: string;
  junctionFill: string;
  junctionStroke: string;
  stationText: string;
  labelMuted: string;
  resourceFill: string;
  yardFill: string;
  yardStroke: string;
  yardSiding: string;
  yardText: string;
  trainStroke: string; // outline around a train marker
  trainLabel: string; // text on a train marker
  occStroke: string; // occupied-platform highlight
}

export const LIGHT: Palette = {
  glow: "#0ea5e9",
  track: "#94a3b8",
  tie: "#cbd5e1",
  crossover: "#64748b",
  edge: "#94a3b8",
  platformFill: "#e2e8f0",
  platformStroke: "#94a3b8",
  platformText: "#334155",
  memuFill: "#cffafe",
  memuStroke: "#0d9488",
  memuText: "#0f766e",
  stationFill: "#ffffff",
  stationStroke: "#64748b",
  junctionFill: "#0ea5e9",
  junctionStroke: "#0369a1",
  stationText: "#1e293b",
  labelMuted: "#64748b",
  resourceFill: "#ffffff",
  yardFill: "#fff7ed",
  yardStroke: "#d97706",
  yardSiding: "#fdba74",
  yardText: "#c2410c",
  trainStroke: "#ffffff",
  trainLabel: "#0b1220",
  occStroke: "#0284c7",
};

export const DARK: Palette = {
  glow: "#0ea5e9",
  track: "#475569",
  tie: "#334155",
  crossover: "#5b7ba0",
  edge: "#334155",
  platformFill: "#0f1a2b",
  platformStroke: "#334155",
  platformText: "#e2e8f0",
  memuFill: "#0f2e2b",
  memuStroke: "#14b8a6",
  memuText: "#5eead4",
  stationFill: "#0f172a",
  stationStroke: "#64748b",
  junctionFill: "#0ea5e9",
  junctionStroke: "#38bdf8",
  stationText: "#e2e8f0",
  labelMuted: "#64748b",
  resourceFill: "#0f172a",
  yardFill: "#1a1206",
  yardStroke: "#d97706",
  yardSiding: "#3f2d10",
  yardText: "#f59e0b",
  trainStroke: "#0b1220",
  trainLabel: "#0b1220",
  occStroke: "#38bdf8",
};

export type ThemeMode = "light" | "dark";
export const paletteFor = (m: ThemeMode): Palette => (m === "dark" ? DARK : LIGHT);
