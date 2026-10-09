/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ViewRoute } from "./route";
import { useViewData } from "./useViewData";

function Probe({ route }: { route: ViewRoute }) {
  const { snapshot, status } = useViewData(route);
  return (
    <div>
      <span data-testid="status">{status}</span>
      <span data-testid="view">{snapshot?.queue?.view ?? ""}</span>
      <span data-testid="rows">{snapshot?.rollup?.rows.length ?? ""}</span>
    </div>
  );
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function installFetch() {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.startsWith("/api/queue")) {
      const agent = new URL(url, "http://local").searchParams.get("agent");
      return json({
        view: `mine:${agent ?? ""}`,
        items: [],
        revisar: [],
        empty_message: null,
      });
    }
    if (url.startsWith("/api/rollup")) {
      return json({ rows: [{ sales_agent: "Anna Snelling" }] });
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
  cleanup();
  vi.unstubAllGlobals();
});

describe("useViewData", () => {
  it("loads the seller queue for a vendedor route", async () => {
    const fetchMock = installFetch();
    render(<Probe route={{ station: "vendedor", agente: "Anna Snelling" }} />);

    await vi.waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("ready");
    });
    expect(screen.getByTestId("view").textContent).toBe("mine:Anna Snelling");
    expect(calls(fetchMock)).toContain("/api/queue?view=mine&agent=Anna+Snelling");
  });

  it("loads the seller queue for a gestor drill route", async () => {
    const fetchMock = installFetch();
    render(
      <Probe route={{ station: "gestor", agente: "Anna Snelling", gestor: "Dustin Brinkmann" }} />,
    );

    await vi.waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("ready");
    });
    expect(calls(fetchMock)).toContain("/api/queue?view=mine&agent=Anna+Snelling");
    expect(calls(fetchMock).some((url) => url.startsWith("/api/queue?view=team"))).toBe(false);
  });

  it("loads rollup and agents for the gestor home and repeats the same slice on a matching route", async () => {
    const fetchMock = installFetch();
    const route: ViewRoute = {
      station: "gestor",
      gestor: "Dustin Brinkmann",
      escritorio: "Central",
    };
    const first = render(<Probe route={route} />);

    await vi.waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("ready");
    });
    expect(calls(fetchMock)).toEqual(
      expect.arrayContaining([
        "/api/rollup?manager=Dustin+Brinkmann&office=Central",
        "/api/agents",
      ]),
    );
    expect(calls(fetchMock).some((url) => url.startsWith("/api/queue"))).toBe(false);

    first.unmount();
    render(<Probe route={{ ...route }} />);
    await vi.waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("ready");
    });
    expect(calls(fetchMock)).toEqual(
      expect.arrayContaining([
        "/api/rollup?manager=Dustin+Brinkmann&office=Central",
        "/api/agents",
      ]),
    );
    const rollupCalls = calls(fetchMock).filter(
      (url) => url === "/api/rollup?manager=Dustin+Brinkmann&office=Central",
    );
    expect(rollupCalls).toHaveLength(2);
  });

  it("sets status error when a fetch fails instead of throwing uncaught", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => json({}, 500)),
    );
    render(<Probe route={{ station: "vendedor", agente: "Anna Snelling" }} />);

    await vi.waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("error");
    });
    expect(screen.getByTestId("view").textContent).toBe("");
  });
});
