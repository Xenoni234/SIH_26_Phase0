import { useEffect, useState } from "react";
import type { Selection, TwinResponse } from "./types";
import { getTwin } from "./api/twin";
import { useTwinStream } from "./hooks/useTwinStream";
import { paletteFor, type ThemeMode } from "./lib/theme";
import TwinMap from "./components/TwinMap";
import StationTrackMap from "./components/StationTrackMap";
import Hud from "./components/Hud";
import LiveTrainList from "./components/LiveTrainList";
import DetailPanel from "./components/DetailPanel";

type ViewMode = "corridor" | "station";

export default function App() {
  const [twin, setTwin] = useState<TwinResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selection, setSelection] = useState<Selection>(null);
  const [view, setView] = useState<ViewMode>("station");
  const [theme, setTheme] = useState<ThemeMode>(
    () => (localStorage.getItem("theme") as ThemeMode) || "light"
  );
  const { tick, conn } = useTwinStream();

  useEffect(() => {
    getTwin().then(setTwin).catch((e) => setError(String(e)));
  }, []);
  useEffect(() => {
    localStorage.setItem("theme", theme);
  }, [theme]);

  const trains = tick?.trains ?? [];
  const palette = paletteFor(theme);

  return (
    <div className={theme === "dark" ? "dark" : ""}>
      <div className="min-h-full bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <header className="mb-4 flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Vasai Road Junction — Live Digital Twin</h1>
              <p className="text-sm text-slate-500">
                Phase 2 · real trains from RailRadar, simulated live · AI recommends — human decides
              </p>
            </div>
            <ThemeToggle theme={theme} onToggle={() => setTheme(theme === "dark" ? "light" : "dark")} />
          </header>

          {error && (
            <div className="mb-4 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300">
              Could not load the twin backdrop ({error}). Is the backend running on{" "}
              <code>{import.meta.env.VITE_API_URL ?? "http://localhost:8000"}</code>?
            </div>
          )}

          <div className="mb-4">
            <Hud tick={tick} conn={conn} />
          </div>

          {!twin && !error && <p className="text-slate-500">Loading twin…</p>}

          {twin && (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <ViewToggle view={view} onChange={setView} />
                  <span className="text-xs text-slate-500">
                    {view === "corridor"
                      ? "Corridors around Vasai — how trains approach & leave"
                      : "Realistic station top-view — platforms, crossovers, yard, Diva line"}
                  </span>
                </div>
                {view === "corridor" ? (
                  <TwinMap twin={twin} trains={trains} palette={palette} selection={selection} onSelect={setSelection} />
                ) : (
                  <StationTrackMap trains={trains} palette={palette} selection={selection} onSelect={setSelection} />
                )}
                <Legend />
              </div>

              <div className="flex flex-col gap-4">
                <DetailPanel selection={selection} />
                <div>
                  <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Live around Vasai ({trains.length})
                  </h2>
                  <LiveTrainList trains={trains} selection={selection} onSelect={setSelection} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ThemeToggle({ theme, onToggle }: { theme: ThemeMode; onToggle: () => void }) {
  return (
    <button onClick={onToggle}
      className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800">
      <span>{theme === "dark" ? "☀️" : "🌙"}</span>
      {theme === "dark" ? "Light" : "Dark"}
    </button>
  );
}

function ViewToggle({ view, onChange }: { view: ViewMode; onChange: (v: ViewMode) => void }) {
  const opts: { key: ViewMode; label: string }[] = [
    { key: "corridor", label: "Corridor view" },
    { key: "station", label: "Station tracks" },
  ];
  return (
    <div className="inline-flex rounded-lg border border-slate-300 bg-white p-0.5 dark:border-slate-700 dark:bg-slate-900">
      {opts.map((o) => (
        <button key={o.key} onClick={() => onChange(o.key)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
            view === o.key
              ? "bg-sky-600 text-white"
              : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
          }`}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

function Legend() {
  const items = [
    ["Express", "#dc2626"],
    ["Local", "#2563eb"],
    ["MEMU", "#0d9488"],
    ["Freight", "#d97706"],
  ] as const;
  return (
    <div className="mt-3 flex flex-wrap items-center gap-4 text-xs text-slate-500">
      {items.map(([label, color]) => (
        <div key={label} className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm" style={{ background: color }} />
          {label}
        </div>
      ))}
      <span className="ml-auto">Trains animate along real corridors · click to inspect</span>
    </div>
  );
}
