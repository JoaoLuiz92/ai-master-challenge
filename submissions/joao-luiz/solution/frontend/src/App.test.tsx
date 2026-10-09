/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function installFetch() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.startsWith("/api/queue")) {
      return json({
        view: "mine",
        items: [
          {
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
          },
        ],
        revisar: [],
        empty_message: null,
      });
    }
    if (url.startsWith("/api/rollup")) {
      return json({
        rows: [
          {
            sales_agent: "Anna Snelling",
            queued_count: 1,
            expected_value_sum: 1000,
            cooling_count: 0,
            good_deals_cooling: 0,
          },
        ],
      });
    }
    if (url === "/api/agents") {
      return json({
        agents: [
          {
            sales_agent: "Anna Snelling",
            manager: "Dustin Brinkmann",
            regional_office: "Central",
            deal_count: 1,
            empty: false,
          },
        ],
        managers: ["Dustin Brinkmann"],
        offices: ["Central"],
      });
    }
    throw new Error(`unexpected ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/");
});

describe("App", () => {
  it("redirects / to /vendedor?agente=Anna+Snelling", async () => {
    installFetch();
    window.history.replaceState(null, "", "/");
    render(<App />);

    await vi.waitFor(() => {
      expect(`${window.location.pathname}${window.location.search}`).toBe(
        "/vendedor?agente=Anna+Snelling",
      );
      expect(screen.getByLabelText("Vendedor")).toBeTruthy();
    });
    expect(screen.queryByLabelText("Visão")).toBeNull();
    expect(document.querySelector("select[name='visao']")).toBeNull();
  });

  it("renders the gestor station when the route is /gestor", async () => {
    installFetch();
    window.history.replaceState(null, "", "/gestor");
    render(<App />);

    await vi.waitFor(() => {
      expect(screen.getByLabelText("Gestor")).toBeTruthy();
    });
    expect(window.location.pathname).toBe("/gestor");
    expect(screen.getByText("Valor do time")).toBeTruthy();
    expect(screen.queryByLabelText("Vendedor")).toBeNull();

    act(() => {
      screen.getByRole("button", { name: "Vendedor" }).click();
    });
    await vi.waitFor(() => {
      expect(window.location.pathname).toBe("/vendedor");
    });
  });
});
