import type { ReactNode } from "react";
import type { Selection } from "../types";
import { TYPE_COLOR } from "../lib/layout";

function Row({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex justify-between gap-4 py-1 text-sm">
      <span className="text-slate-500">{label}</span>
      <span className="text-right font-medium">{value ?? "—"}</span>
    </div>
  );
}

export default function DetailPanel({ selection }: { selection: Selection }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/70">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Details</h2>

      {!selection && (
        <p className="text-sm text-slate-500">
          Click a train, station, or platform on the map to inspect it.
        </p>
      )}

      {selection?.kind === "train" && (
        <div>
          <div className="mb-2 flex items-center gap-2">
            <span className="h-3 w-3 rounded-sm" style={{ background: TYPE_COLOR[selection.train.type] ?? "#64748b" }} />
            <span className="text-lg font-semibold">{selection.train.id}</span>
          </div>
          <div className="mb-2 text-sm text-slate-400">{selection.train.name}</div>
          <Row label="Type" value={selection.train.type} />
          <Row label="Route" value={`${selection.train.source} → ${selection.train.destination}`} />
          <Row label="Corridor" value={selection.train.corridor} />
          <Row label="Between" value={`${selection.train.from_station} → ${selection.train.to_station}`} />
          <Row label="Status" value={selection.train.status.replace("_", " ")} />
          <Row label="Platform" value={selection.train.platform} />
          <Row label="km from BSR" value={selection.train.km_from_bsr} />
          <Row label="Departure"
            value={Math.abs(selection.train.minutes_to_departure) < 1
              ? "now"
              : `${selection.train.minutes_to_departure > 0 ? "in " : ""}${Math.round(Math.abs(selection.train.minutes_to_departure))}m${selection.train.minutes_to_departure < 0 ? " ago" : ""}`} />
        </div>
      )}

      {selection && selection.kind !== "train" && (
        <div>
          <div className="mb-2 text-lg font-semibold">{selection.node.id}</div>
          <Row label="Kind" value={selection.kind} />
          {selection.node.name && <Row label="Name" value={selection.node.name} />}
          {selection.node.corridor && <Row label="Corridor" value={selection.node.corridor} />}
          {selection.node.km != null && <Row label="km from BSR" value={selection.node.km} />}
          {selection.node.number != null && (
            <Row label="Platform" value={`P${selection.node.number}${(selection.node.number ?? 0) >= 6 ? " · MEMU" : " · slow/fast"}`} />
          )}
          {selection.node.serves && <Row label="Serves" value={selection.node.serves.join(", ")} />}
          {selection.node.connects && <Row label="Connects" value={selection.node.connects.join(", ")} />}
          {selection.node.parallel_to && <Row label="Parallel to" value={selection.node.parallel_to} />}
        </div>
      )}
    </div>
  );
}
