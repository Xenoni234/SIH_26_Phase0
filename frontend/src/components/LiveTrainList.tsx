import type { Selection, SimTrain } from "../types";
import { TYPE_COLOR } from "../lib/layout";

const STATUS_STYLE: Record<string, string> = {
  approaching: "text-sky-600 dark:text-sky-400",
  at_platform: "text-emerald-600 dark:text-emerald-400",
  departed: "text-slate-500",
  stabled: "text-amber-600 dark:text-amber-400",
};

function eta(min: number): string {
  if (Math.abs(min) < 1) return "now";
  return min > 0 ? `in ${Math.round(min)}m` : `${Math.round(-min)}m ago`;
}

export default function LiveTrainList({ trains, selection, onSelect }: {
  trains: SimTrain[];
  selection: Selection;
  onSelect: (s: Selection) => void;
}) {
  const selId = selection?.kind === "train" ? selection.train.id : null;
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900/70">
      <div className="max-h-[520px] divide-y divide-slate-100 overflow-y-auto dark:divide-slate-800">
        {trains.map((t) => {
          const sel = t.id === selId;
          return (
            <button key={t.id} onClick={() => onSelect({ kind: "train", train: t })}
              className={`flex w-full items-center gap-2 px-3 py-2 text-left transition ${
                sel ? "bg-sky-50 dark:bg-sky-950/60" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"}`}>
              <span className="mt-0.5 h-2.5 w-2.5 shrink-0 rounded-sm" style={{ background: TYPE_COLOR[t.type] ?? "#64748b" }} />
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="font-semibold">{t.id}</span>
                  <span className="shrink-0 font-mono text-[11px] tabular-nums text-slate-500">{eta(t.minutes_to_departure)}</span>
                </div>
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-xs text-slate-500">{t.name}</span>
                  <span className={`shrink-0 text-[11px] ${STATUS_STYLE[t.status] ?? "text-slate-500"}`}>
                    {t.status.replace("_", " ")}
                  </span>
                </div>
                <div className="mt-0.5 flex items-center gap-2 font-mono text-[11px] text-slate-400">
                  <span>{t.source} → {t.destination}</span>
                  {t.platform != null && <span className="rounded bg-slate-100 px-1 text-slate-500 dark:bg-slate-800">PF{t.platform}</span>}
                </div>
              </div>
            </button>
          );
        })}
        {trains.length === 0 && (
          <div className="px-3 py-6 text-center text-sm text-slate-500">Waiting for live data…</div>
        )}
      </div>
    </div>
  );
}
