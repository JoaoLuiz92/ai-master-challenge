import { useEffect, useState } from "react";

import {
  queuePath,
  rollupPath,
  type AgentsResponse,
  type QueueResponse,
  type RollupRow,
} from "../api/client";
import type { ViewRoute } from "./route";

export type DataSnapshot = {
  queue: QueueResponse | null;
  rollup: { rows: RollupRow[] } | null;
  agents: AgentsResponse;
};

export type ViewDataStatus = "loading" | "ready" | "error";

function isQueueRoute(route: ViewRoute): boolean {
  return route.station === "vendedor" || Boolean(route.agente);
}

async function read<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`GET ${path} failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function useViewData(route: ViewRoute): {
  snapshot: DataSnapshot | null;
  status: ViewDataStatus;
} {
  const [snapshot, setSnapshot] = useState<DataSnapshot | null>(null);
  const [status, setStatus] = useState<ViewDataStatus>("loading");

  useEffect(() => {
    let active = true;
    setStatus("loading");

    const request = isQueueRoute(route)
      ? Promise.all([
          read<QueueResponse>(queuePath("seller", { agent: route.agente })),
          read<AgentsResponse>("/api/agents"),
        ]).then(([queue, agents]) => ({ queue, rollup: null, agents }))
      : Promise.all([
          read<{ rows: RollupRow[] }>(
            rollupPath({ manager: route.gestor, office: route.escritorio }),
          ),
          read<AgentsResponse>("/api/agents"),
        ]).then(([rollup, agents]) => ({ queue: null, rollup, agents }));

    request
      .then((next) => {
        if (!active) {
          return;
        }
        setSnapshot(next);
        setStatus("ready");
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setSnapshot(null);
        setStatus("error");
      });

    return () => {
      active = false;
    };
  }, [route.station, route.agente, route.gestor, route.escritorio]);

  return { snapshot, status };
}
