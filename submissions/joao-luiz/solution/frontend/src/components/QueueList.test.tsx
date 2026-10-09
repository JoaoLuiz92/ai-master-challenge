/** @vitest-environment jsdom */

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { QueueItem } from "../api/client";
import { QueueList } from "./QueueList";

const LABELS = [
  "Produto",
  "Conta",
  "Valor",
  "Estágio",
  "Dias no funil",
  "SCORE",
  "Estado",
  "Confiança",
  "Motivo",
  "Ação",
];

function deal(overrides: Partial<QueueItem> = {}): QueueItem {
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
    reason: "GTX Pro · US$ 1.000 · 40 dias no funil · dentro do ciclo",
    action: "Avançar proposta",
    ...overrides,
  };
}

describe("QueueList", () => {
  it("shows the deal fields with Portuguese labels, reason, and action", () => {
    render(<QueueList items={[deal()]} />);

    for (const label of LABELS) {
      expect(screen.getByText(label)).toBeTruthy();
    }
    expect(screen.getByText("GTX Pro")).toBeTruthy();
    expect(screen.getByText("Acme")).toBeTruthy();
    expect(screen.getByText("US$ 1.000")).toBeTruthy();
    expect(screen.getByText("Engaging")).toBeTruthy();
    expect(screen.getByText("40")).toBeTruthy();
    expect(screen.getByText("90")).toBeTruthy();
    expect(screen.getByText("Focar")).toBeTruthy();
    expect(screen.getByText("Alta")).toBeTruthy();
    expect(
      screen.getByText("GTX Pro · US$ 1.000 · 40 dias no funil · dentro do ciclo"),
    ).toBeTruthy();
    expect(screen.getByText("Avançar proposta")).toBeTruthy();
    expect(screen.queryByText("Esfriando")).toBeNull();
  });

  it("shows the Esfriando badge only when age is above 106 days", () => {
    const { unmount } = render(<QueueList items={[deal({ age_days: 107 })]} />);
    expect(screen.getByText("Esfriando")).toBeTruthy();
    unmount();

    render(<QueueList items={[deal({ age_days: 106 })]} />);
    expect(screen.queryByText("Esfriando")).toBeNull();
  });
});
