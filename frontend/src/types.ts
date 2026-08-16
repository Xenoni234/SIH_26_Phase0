// Mirrors the backend JSON from /twin, /twin/summary, /stations, /trains.

export type TrainType =
  | "express"
  | "passenger"
  | "local"
  | "memu"
  | "freight"
  | "yard";

export interface TrainState {
  train_id: string;
  name: string | null;
  train_type: TrainType;
  corridor: string | null;
  direction: string | null;
  current_station: string | null;
  next_station: string | null;
  current_block: string | null;
  platform: number | null;
  lat: number | null;
  lon: number | null;
  speed_kmph: number | null;
  delay_minutes: number;
  priority: number;
  destination: string | null;
  eta: string | null;
  source: string;
  observed_at: string;
}

export interface GraphNode {
  id: string;
  kind: "station" | "platform" | "junction" | "yard" | "freight";
  name?: string;
  corridor?: string;
  km?: number;
  number?: number; // platform number
  station?: string;
  serves?: string[];
  connects?: string[];
  parallel_to?: string;
  [k: string]: unknown;
}

export interface GraphEdge {
  source: string;
  target: string;
  kind: string;
  block_id?: string;
  corridor?: string;
  length_km?: number;
  [k: string]: unknown;
}

export interface TwinResponse {
  junction: { code: string; name: string };
  summary: {
    nodes: number;
    edges: number;
    node_kinds: Record<string, number>;
  };
  graph: { nodes: GraphNode[]; edges: GraphEdge[] };
  trains: TrainState[];
}

export interface TwinSummary {
  junction: string;
  platforms: number;
  corridors: Record<string, number>;
  blocks: number;
  graph: { nodes: number; edges: number; node_kinds: Record<string, number> };
}

// --- Live simulation stream (/ws/twin, /sim/snapshot) ---
export interface SimTrain {
  id: string;
  name: string;
  type: TrainType;
  corridor: "north" | "western" | "diva" | string;
  from_station: string;
  to_station: string;
  frac: number;
  km_from_bsr: number;
  status: "approaching" | "departed" | "at_platform" | string;
  source: string;
  destination: string;
  platform: number | null;
  at_platform: boolean;
  minutes_to_departure: number;
}

export interface TwinTick {
  type: "twin_tick";
  sim_time: string;
  sim_speed: number;
  count: number;
  trains: SimTrain[];
}

// A unified selection for the detail panel.
export type Selection =
  | { kind: "station"; node: GraphNode }
  | { kind: "platform"; node: GraphNode }
  | { kind: "junction"; node: GraphNode }
  | { kind: "yard" | "freight"; node: GraphNode }
  | { kind: "train"; train: SimTrain }
  | null;
