import type { Selection, SimTrain } from "../types";
import { TYPE_COLOR } from "../lib/layout";

const STATUS_STYLE: Record<string, string> = {
  approaching: "text-sky-400",
  at_platform: "text-emerald-400",
  departed: "text-slate-400",
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
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70">
      <div className="max-h-[420px] overflow-y-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2">Train</th>
              <th className="px-3 py-2">Route</th>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2 text-right">Dep</th>
            </tr>
          </thead>
          <tbody>
            {trains.map((t) => {
              const sel = t.id === selId;
              return (
                <tr key={t.id} onClick={() => onSelect({ kind: "train", train: t })}
                  className={`cursor-pointer border-t border-slate-800/70 ${
                    sel ? "bg-sky-950/60" : "hover:bg-slate-800/50"}`}>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-sm" style={{ background: TYPE_COLOR[t.type] ?? "#64748b" }} />
                      <span className="font-medium">{t.id}</span>
                    </div>
                    <div className="truncate text-xs text-slate-500" style={{ maxWidth: 150 }}>{t.name}</div>
                  </td>
                  <td className="px-3 py-2 font-mono text-xs text-slate-400">{t.source}→{t.destination}</td>
                  <td className={`px-3 py-2 text-xs ${STATUS_STYLE[t.status] ?? "text-slate-400"}`}>
                    {t.status.replace("_", " ")}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-xs tabular-nums text-slate-300">
                    {eta(t.minutes_to_departure)}
                  </td>
                </tr>
              );
            })}
            {trains.length === 0 && (
              <tr><td colSpan={4} className="px-3 py-6 text-center text-slate-500">Waiting for live data…</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
