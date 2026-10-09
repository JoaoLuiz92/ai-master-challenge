import { describe, expect, it } from "vitest";

import type { QueueItem, QueueResponse, ReviewItem, RollupRow } from "../api/client";
import { deriveSellerKpis, deriveTeamKpis } from "./summary";

function item(overrides: Partial<QueueItem> = {}): QueueItem {
  return {
    opportunity_id: "OPP-1",
    product: "GTX Pro",
    account: "Acme",
    value: 1000,
    deal_stage: "Engaging",
    age_days: 40,
    score: 90,
    estado: "Focar",
    confidence: "Alta",
    reason: "motivo",
    action: "ação",
    ...overrides,
  };
}

function review(overrides: Partial<ReviewItem> = {}): ReviewItem {
  return {
    opportunity_id: "OPP-R",
    product: "GTK 500",
    account: null,
    deal_stage: "Engaging",
    value: 500,
    age_days: null,
    estado: "Revisar",
    reason: "sem conta",
    action: "Qualificar conta/dados",
    ...overrides,
  };
}

function queue(overrides: Partial<QueueResponse> = {}): QueueResponse {
  return {
    view: "mine",
    items: [],
    revisar: [],
    empty_message: null,
    ...overrides,
  };
}

function row(overrides: Partial<RollupRow> = {}): RollupRow {
  return {
    sales_agent: "Anna Snelling",
    queued_count: 8,
    expected_value_sum: 1000,
    cooling_count: 3,
    good_deals_cooling: 1,
    ...overrides,
  };
}

describe("deriveSellerKpis", () => {
  it("sums Focar value and count only from Focar items", () => {
    const kpis = deriveSellerKpis(
      queue({
        items: [
          item({ opportunity_id: "A", estado: "Focar", value: 2000 }),
          item({ opportunity_id: "B", estado: "Focar", value: 500 }),
          item({ opportunity_id: "C", estado: "Acompanhar", value: 9999 }),
        ],
        revisar: [review(), review({ opportunity_id: "OPP-R2" })],
      }),
    );
    expect(kpis.valorEmFocar).toBe(2500);
    expect(kpis.nFocar).toBe(2);
    expect(kpis.revisar).toBe(2);
  });

  it("counts Esfriando only when age_days is strictly greater than 106", () => {
    const atBoundary = deriveSellerKpis(
      queue({
        items: [item({ age_days: 106 }), item({ opportunity_id: "B", age_days: 40 })],
      }),
    );
    expect(atBoundary.esfriando).toBe(0);

    const over = deriveSellerKpis(
      queue({
        items: [item({ age_days: 107 }), item({ opportunity_id: "B", age_days: 106 })],
      }),
    );
    expect(over.esfriando).toBe(1);
  });

  it("returns zeros for an empty queue", () => {
    expect(deriveSellerKpis(queue())).toEqual({
      valorEmFocar: 0,
      nFocar: 0,
      esfriando: 0,
      revisar: 0,
    });
  });
});

describe("deriveTeamKpis", () => {
  it("sums team value, queued, cooling, and good-cooling from rollup rows", () => {
    expect(
      deriveTeamKpis([
        row(),
        row({
          sales_agent: "Darcel Schlecht",
          queued_count: 2,
          expected_value_sum: 500,
          cooling_count: 1,
          good_deals_cooling: 0,
        }),
      ]),
    ).toEqual({
      valorTime: 1500,
      naFila: 10,
      esfriando: 4,
      bonsEsfriando: 1,
    });
  });

  it("returns zeros for an empty rollup", () => {
    expect(deriveTeamKpis([])).toEqual({
      valorTime: 0,
      naFila: 0,
      esfriando: 0,
      bonsEsfriando: 0,
    });
  });
});
