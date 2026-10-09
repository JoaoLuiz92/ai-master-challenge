/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { QueueItem, ReviewItem } from "../api/client";
import type { DataSnapshot } from "../routing/useViewData";
import { VendedorStation } from "./VendedorStation";

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
    action: "Avançar proposta",
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
    reason: "sujeira",
    action: "Qualificar conta/dados",
    ...overrides,
  };
}

function snapshot(overrides: Partial<DataSnapshot> = {}): DataSnapshot {
  return {
    queue: {
      view: "mine",
      items: [
        item(),
        item({ opportunity_id: "OPP-2", estado: "Acompanhar", action: "Nutrir" }),
      ],
      revisar: [review()],
      empty_message: null,
    },
    rollup: null,
    agents: {
      agents: [
        {
          sales_agent: "Anna Snelling",
          manager: "Dustin Brinkmann",
          regional_office: "Central",
          deal_count: 2,
          empty: false,
        },
        {
          sales_agent: "Ghost",
          manager: null,
          regional_office: null,
          deal_count: 0,
          empty: true,
        },
      ],
      managers: ["Dustin Brinkmann"],
      offices: ["Central"],
    },
    ...overrides,
  };
}

afterEach(cleanup);

describe("VendedorStation", () => {
  it("shows only the vendedor selector, the strip, Focar open, and collapsed bands with counts", () => {
    render(
      <VendedorStation
        snapshot={snapshot()}
        route={{ station: "vendedor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );

    expect(screen.getByLabelText("Vendedor")).toBeTruthy();
    expect(screen.queryByLabelText("Gestor")).toBeNull();
    expect(screen.queryByLabelText("Escritório")).toBeNull();
    expect(screen.getByText("Valor em Focar")).toBeTruthy();
    expect(screen.getByText("Nº Focar")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Focar (1)" }).getAttribute("aria-expanded")).toBe(
      "true",
    );
    expect(screen.getByRole("button", { name: "Acompanhar (1)" }).getAttribute("aria-expanded")).toBe(
      "false",
    );
    expect(screen.getByRole("button", { name: "Revisar (1)" }).getAttribute("aria-expanded")).toBe(
      "false",
    );
    expect(screen.getByText("Avançar proposta")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Passar para colega" })).toBeNull();
    expect(screen.queryByText("Nutrir")).toBeNull();
    expect(screen.getByRole("button", { name: "Exportar CSV" })).toBeTruthy();
  });

  it("opens the Revisar band when the Revisar KPI is activated", () => {
    render(
      <VendedorStation
        snapshot={snapshot()}
        route={{ station: "vendedor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );

    act(() => {
      screen.getByRole("button", { name: "Revisar1" }).click();
    });
    expect(screen.getByRole("button", { name: "Revisar (1)" }).getAttribute("aria-expanded")).toBe(
      "true",
    );
    expect(screen.getByText("Qualificar conta/dados")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Passar para colega" })).toBeNull();
  });

  it("shows the ghost empty state and the only-Revisar empty Focar state", () => {
    const { unmount } = render(
      <VendedorStation
        snapshot={snapshot()}
        route={{ station: "vendedor", agente: "Ghost" }}
        navigate={() => undefined}
      />,
    );
    expect(screen.getByRole("status").textContent).toBe(
      "Este nome não tem carteira. Escolha outro vendedor.",
    );
    unmount();

    render(
      <VendedorStation
        snapshot={snapshot({
          queue: {
            view: "mine",
            items: [],
            revisar: [review()],
            empty_message: null,
          },
        })}
        route={{ station: "vendedor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );
    expect(screen.getByRole("status").textContent).toBe("Nada trabalhável. 1 em Revisar.");
  });
});
