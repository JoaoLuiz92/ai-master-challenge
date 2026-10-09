import type { QueueResponse, RollupRow } from "../api/client";

export type SellerKpis = {
  valorEmFocar: number;
  nFocar: number;
  esfriando: number;
  revisar: number;
};

export type TeamKpis = {
  valorTime: number;
  naFila: number;
  esfriando: number;
  bonsEsfriando: number;
};

const COOLING_AFTER_DAYS = 106;

export function deriveSellerKpis(queue: QueueResponse): SellerKpis {
  const focar = queue.items.filter((item) => item.estado === "Focar");
  return {
    valorEmFocar: focar.reduce((sum, item) => sum + item.value, 0),
    nFocar: focar.length,
    esfriando: queue.items.filter((item) => item.age_days > COOLING_AFTER_DAYS).length,
    revisar: queue.revisar.length,
  };
}

export function deriveTeamKpis(rows: RollupRow[]): TeamKpis {
  return {
    valorTime: rows.reduce((sum, row) => sum + row.expected_value_sum, 0),
    naFila: rows.reduce((sum, row) => sum + row.queued_count, 0),
    esfriando: rows.reduce((sum, row) => sum + row.cooling_count, 0),
    bonsEsfriando: rows.reduce((sum, row) => sum + row.good_deals_cooling, 0),
  };
}
