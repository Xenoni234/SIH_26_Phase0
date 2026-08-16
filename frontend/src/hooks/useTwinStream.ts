import { useEffect, useRef, useState } from "react";
import type { TwinTick } from "../types";
import { WS_URL, getSnapshot } from "../api/twin";

export type ConnState = "connecting" | "live" | "polling" | "offline";

interface StreamState {
  tick: TwinTick | null;
  conn: ConnState;
}

/**
 * Subscribes to the live simulation over WebSocket, with automatic reconnect
 * and a REST-polling fallback if the socket cannot be established.
 */
export function useTwinStream(): StreamState {
  const [tick, setTick] = useState<TwinTick | null>(null);
  const [conn, setConn] = useState<ConnState>("connecting");
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<number | null>(null);
  const retryRef = useRef<number | null>(null);

  useEffect(() => {
    let closed = false;

    const startPolling = () => {
      if (pollRef.current != null) return;
      setConn("polling");
      const poll = async () => {
        try {
          setTick(await getSnapshot());
          setConn((c) => (c === "offline" ? "polling" : c));
        } catch {
          setConn("offline");
        }
      };
      poll();
      pollRef.current = window.setInterval(poll, 2000);
    };

    const stopPolling = () => {
      if (pollRef.current != null) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };

    const connect = () => {
      setConn("connecting");
      let ws: WebSocket;
      try {
        ws = new WebSocket(WS_URL);
      } catch {
        startPolling();
        return;
      }
      wsRef.current = ws;

      ws.onopen = () => {
        stopPolling();
        setConn("live");
      };
      ws.onmessage = (ev) => {
        try {
          setTick(JSON.parse(ev.data) as TwinTick);
        } catch {
          /* ignore malformed frame */
        }
      };
      ws.onerror = () => ws.close();
      ws.onclose = () => {
        if (closed) return;
        startPolling();
        // try to re-establish the socket after a short delay
        retryRef.current = window.setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      closed = true;
      stopPolling();
      if (retryRef.current != null) clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, []);

  return { tick, conn };
}
