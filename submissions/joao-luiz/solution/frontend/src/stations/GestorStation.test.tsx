/** @vitest-environment jsdom */

import { act, cleanup, render, screen, waitFor } from "@testing-library/react";
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

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

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
    expect(screen.queryByRole("button", { name: "Passar para colega" })).toBeNull();
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
    expect(screen.queryByRole("button", { name: "Passar para colega" })).toBeNull();
  });

  it("offers Passar para colega on the drill only, including Acompanhar and not Revisar", () => {
    render(
      <GestorStation
        snapshot={{
          ...drillSnapshot(),
          queue: {
            view: "mine",
            items: [
              drillSnapshot().queue!.items[0]!,
              {
                ...drillSnapshot().queue!.items[0]!,
                opportunity_id: "OPP-2",
                estado: "Acompanhar",
                action: "Nutrir",
              },
            ],
            revisar: [
              {
                opportunity_id: "OPP-R",
                product: "GTK 500",
                account: null,
                deal_stage: "Engaging",
                value: 500,
                age_days: null,
                estado: "Revisar",
                reason: "sujeira",
                action: "Qualificar conta/dados",
              },
            ],
            empty_message: null,
          },
        }}
        route={{ station: "gestor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );

    expect(screen.getAllByRole("button", { name: "Passar para colega" })).toHaveLength(1);
    act(() => {
      screen.getByRole("button", { name: "Acompanhar (1)" }).click();
    });
    expect(screen.getAllByRole("button", { name: "Passar para colega" })).toHaveLength(2);
    act(() => {
      screen.getByRole("button", { name: "Revisar (1)" }).click();
    });
    expect(screen.getByText("Qualificar conta/dados")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: "Passar para colega" })).toHaveLength(2);
  });

  it("cancel leaves the deal and does not post", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      void init;
      const url = String(input);
      if (url.startsWith("/api/handoff/candidates")) {
        return json({ candidates: ["Bruno"] });
      }
      throw new Error(url);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <GestorStation
        snapshot={drillSnapshot()}
        route={{ station: "gestor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );

    screen.getByRole("button", { name: "Passar para colega" }).click();
    expect(await screen.findByRole("radio", { name: "Bruno" })).toBeTruthy();
    act(() => {
      screen.getByRole("button", { name: "Cancelar" }).click();
    });

    expect(screen.getByText("Avançar proposta")).toBeTruthy();
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
    expect(fetchMock.mock.calls.some((call) => (call[1] as RequestInit | undefined)?.method === "POST")).toBe(
      false,
    );
  });

  it("confirm refetches the origin queue and the deal leaves", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.startsWith("/api/handoff/candidates")) {
        return json({ candidates: ["Bruno"] });
      }
      if (url === "/api/handoff" && init?.method === "POST") {
        return json({
          opportunity_id: "OPP-1",
          sales_agent: "Bruno",
          from_agent: "Anna Snelling",
        });
      }
      if (url.startsWith("/api/queue")) {
        return json({ view: "mine", items: [], revisar: [], empty_message: "sem deals nesta visão" });
      }
      throw new Error(url);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <GestorStation
        snapshot={drillSnapshot()}
        route={{ station: "gestor", agente: "Anna Snelling" }}
        navigate={() => undefined}
      />,
    );

    screen.getByRole("button", { name: "Passar para colega" }).click();
    (await screen.findByRole("radio", { name: "Bruno" })).click();
    screen.getByRole("button", { name: "Confirmar" }).click();

    await waitFor(() => {
      expect(screen.queryByText("Avançar proposta")).toBeNull();
    });
    const posted = fetchMock.mock.calls.find((call) => (call[1] as RequestInit | undefined)?.method === "POST");
    expect(JSON.parse(String(posted?.[1] && (posted[1] as RequestInit).body))).toEqual({
      opportunity_id: "OPP-1",
      to_agent: "Bruno",
    });
    expect(
      fetchMock.mock.calls.some((call) => String(call[0]).includes("/api/queue") && String(call[0]).includes("Anna")),
    ).toBe(true);
  });
});
