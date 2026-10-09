/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { DataSnapshot } from "../routing/useViewData";
import { GestorStation } from "./GestorStation";

function homeSnapshot(rows = true): DataSnapshot {
  return {
    queue: null,
    rollup: {
      rows: rows
        ? [
            {
              sales_agent: "Anna Snelling",
              queued_count: 8,
              expected_value_sum: 1000,
              cooling_count: 3,
              good_deals_cooling: 1,
            },
          ]
        : [],
    },
    agents: {
      agents: [],
      managers: ["Dustin Brinkmann"],
      offices: ["Central"],
    },
  };
}

function drillSnapshot(): DataSnapshot {
  return {
    queue: {
      view: "mine",
      items: [
        {
          opportunity_id: "OPP-1",
          product: "GTX Pro",
          account: "Acme",
          value: 2000,
          deal_stage: "Engaging",
          age_days: 40,
          score: 90,
          estado: "Focar",
          confidence: "Alta",
          reason: "motivo",
          action: "Avançar proposta",
        },
      ],
      revisar: [],
      empty_message: null,
    },
    rollup: null,
    agents: {
      agents: [],
      managers: ["Dustin Brinkmann"],
      offices: ["Central"],
    },
  };
}

afterEach(cleanup);

describe("GestorStation", () => {
  it("shows team strip and rollup on home, without the team queue or export", () => {
    render(
      <GestorStation
        snapshot={homeSnapshot()}
        route={{ station: "gestor", gestor: "Dustin Brinkmann" }}
        navigate={() => undefined}
      />,
    );

    expect(screen.getByLabelText("Gestor")).toBeTruthy();
    expect(screen.getByLabelText("Escritório")).toBeTruthy();
    expect(screen.queryByLabelText("Vendedor")).toBeNull();
    expect(screen.getByText("Valor do time")).toBeTruthy();
    expect(screen.getAllByText("Na fila").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Bons esfriando").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Anna Snelling" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Exportar CSV" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Focar (1)" })).toBeNull();
  });

  it("drills into a seller queue, switches the strip, and shows export", () => {
    const navigate = vi.fn();
    const { rerender } = render(
      <GestorStation
        snapshot={homeSnapshot()}
        route={{ station: "gestor" }}
        navigate={navigate}
      />,
    );

    screen.getByRole("button", { name: "Anna Snelling" }).click();
    expect(navigate).toHaveBeenCalledWith(
      expect.objectContaining({ station: "gestor", agente: "Anna Snelling" }),
    );

    rerender(
      <GestorStation
        snapshot={drillSnapshot()}
        route={{ station: "gestor", agente: "Anna Snelling" }}
        navigate={navigate}
      />,
    );

    expect(screen.getByText("Valor em Focar")).toBeTruthy();
    expect(screen.getAllByText("US$ 2.000").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Focar (1)" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Exportar CSV" })).toBeTruthy();
    expect(screen.queryByRole("columnheader", { name: "Vendedor" })).toBeNull();
  });

  it("clears agente and restores the rollup without leaving /gestor", () => {
    const navigate = vi.fn();
    render(
      <GestorStation
        snapshot={drillSnapshot()}
        route={{ station: "gestor", agente: "Anna Snelling", gestor: "Dustin Brinkmann" }}
        navigate={navigate}
      />,
    );

    act(() => {
      screen.getByRole("button", { name: "Voltar ao time" }).click();
    });
    expect(navigate.mock.calls[0]?.[0].station).toBe("gestor");
    expect(navigate.mock.calls[0]?.[0].gestor).toBe("Dustin Brinkmann");
    expect(navigate.mock.calls[0]?.[0].agente).toBeUndefined();
  });

  it("shows the no-sellers empty state and no export", () => {
    render(
      <GestorStation
        snapshot={homeSnapshot(false)}
        route={{ station: "gestor" }}
        navigate={() => undefined}
      />,
    );
    expect(screen.getByRole("status").textContent).toBe(
      "nenhum vendedor neste gestor/escritório",
    );
    expect(screen.queryByRole("button", { name: "Exportar CSV" })).toBeNull();
  });
});
