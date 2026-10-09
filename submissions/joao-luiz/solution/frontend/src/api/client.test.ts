import { afterEach, describe, expect, it, vi } from "vitest";

import { createViewClient, type QueueItem } from "./client";

const DEAL = "OPP-1";

function item(score: number): QueueItem {
  return {
    opportunity_id: DEAL,
    product: "GTX Pro",
    account: "Acme",
    value: 1000,
    deal_stage: "Engaging",
    age_days: 40,
    score,
    estado: "Focar",
    confidence: "Alta",
    reason: "GTX Pro · US$ 1.000 · 40 dias no funil · dentro do ciclo",
    action: "Avançar proposta",
  };
}

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
      const team = url.includes("view=team");
      return json({
        view: team ? "team" : "mine",
        items: [item(team ? 10 : 90)],
        revisar: [],
        empty_message: null,
      });
    }
    if (url.startsWith("/api/rollup")) {
      return json({ rows: [] });
    }
    if (url === "/api/agents") {
      return json({ agents: [], managers: [], offices: [] });
    }
    throw new Error(`unexpected ${url}`);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function calls(fetchMock: ReturnType<typeof installFetch>): string[] {
  return fetchMock.mock.calls.map((call) => String(call[0]));
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("view client", () => {
  it("refetches the queue when the role switches and keeps the new score", async () => {
    const fetchMock = installFetch();
    const client = createViewClient();

    const mine = await client.load();
    expect(mine.role).toBe("seller");
    expect(mine.queue.items[0]?.score).toBe(90);
    expect(calls(fetchMock)).toEqual(
      expect.arrayContaining(["/api/queue?view=mine", "/api/rollup", "/api/agents"]),
    );

    const team = await client.setRole("manager");
    expect(team.role).toBe("manager");
    expect(team.queue.items[0]?.opportunity_id).toBe(DEAL);
    expect(team.queue.items[0]?.score).toBe(10);
    expect(calls(fetchMock)).toContain("/api/queue?view=team");
  });

  it("sends agent, manager, and office on the next queue read", async () => {
    const fetchMock = installFetch();
    const client = createViewClient();

    await client.setFilter({
      agent: "Anna Snelling",
      manager: "Dustin Brinkmann",
      office: "Central",
    });

    expect(calls(fetchMock)).toContain(
      "/api/queue?view=mine&agent=Anna+Snelling&manager=Dustin+Brinkmann&office=Central",
    );
    expect(calls(fetchMock)).toContain("/api/rollup?manager=Dustin+Brinkmann&office=Central");
    expect(client.getState()?.filter).toEqual({
      agent: "Anna Snelling",
      manager: "Dustin Brinkmann",
      office: "Central",
    });
  });
});
