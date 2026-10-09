import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchHandoffCandidates, postHandoff } from "./client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("handoff client", () => {
  it("posts opportunity_id and to_agent and returns the new owner", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({
          opportunity_id: "OPP-1",
          sales_agent: "Bruno",
          from_agent: "Ana",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await postHandoff({ opportunity_id: "OPP-1", to_agent: "Bruno" });

    expect(result).toEqual({
      opportunity_id: "OPP-1",
      sales_agent: "Bruno",
      from_agent: "Ana",
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/handoff");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({
      opportunity_id: "OPP-1",
      to_agent: "Bruno",
    });
  });

  it("throws the detail when the handoff is refused", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ detail: "Colega não encontrado" }), {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(postHandoff({ opportunity_id: "OPP-1", to_agent: "Ninguém" })).rejects.toThrow(
      "Colega não encontrado",
    );
  });

  it("gets the candidate names for the opportunity", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ candidates: ["Bruno", "Otto"] }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchHandoffCandidates("OPP 1")).resolves.toEqual(["Bruno", "Otto"]);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(
      "/api/handoff/candidates?opportunity_id=OPP+1",
    );
  });

  it("throws the detail when the candidate list fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ detail: "Colega de outro escritório" }), {
          status: 422,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(fetchHandoffCandidates("OPP-1")).rejects.toThrow("Colega de outro escritório");
  });
});
