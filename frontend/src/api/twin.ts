import type { TwinResponse, TwinSummary } from "../types";

const BASE = (import.meta.env.VITE_API_URL as string) ?? "http://localhost:8000";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
  return (await res.json()) as T;
}

export const getTwin = () => getJSON<TwinResponse>("/twin");
export const getSummary = () => getJSON<TwinSummary>("/twin/summary");

export interface StationsResponse {
  count: number;
  stations: { code: string; name: string; corridor: string; km_from_bsr: number }[];
}
export const getStations = () => getJSON<StationsResponse>("/stations");

import type { TwinTick } from "../types";
export const getSnapshot = () => getJSON<TwinTick>("/sim/snapshot");

export async function setSpeed(value: number): Promise<number> {
  const res = await fetch(`${BASE}/sim/speed?value=${value}`, { method: "POST" });
  if (!res.ok) throw new Error(`/sim/speed → HTTP ${res.status}`);
  return (await res.json()).sim_speed as number;
}

export const API_BASE = BASE;
export const WS_URL = BASE.replace(/^http/, "ws") + "/ws/twin";
