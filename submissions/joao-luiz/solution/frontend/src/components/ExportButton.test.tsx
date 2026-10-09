/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ExportButton } from "./ExportButton";

const CSV = "product,account,value\nGTX Pro,Acme,1000\n";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("ExportButton", () => {
  it("downloads the csv of the active agent, manager, and office filter", async () => {
    const fetchMock = vi.fn(async (_input: RequestInfo | URL) => {
      return new Response(CSV, {
        status: 200,
        headers: { "Content-Type": "text/csv" },
      });
    });
    vi.stubGlobal("fetch", fetchMock);

    const downloaded: { blob: Blob | null } = { blob: null };
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: (blob: Blob) => {
        downloaded.blob = blob;
        return "blob:export";
      },
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: () => undefined,
    });

    const clicks: HTMLAnchorElement[] = [];
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function mockClick(
      this: HTMLAnchorElement,
    ) {
      clicks.push(this);
    });

    render(
      <ExportButton
        filter={{
          agent: "Anna Snelling",
          manager: "Dustin Brinkmann",
          office: "Central",
        }}
      />,
    );

    screen.getByRole("button", { name: "Exportar CSV" }).click();

    await vi.waitFor(() => {
      expect(clicks).toHaveLength(1);
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(
      "/api/export.csv?agent=Anna+Snelling&manager=Dustin+Brinkmann&office=Central",
    );
    expect(clicks[0]?.download).toBe("export.csv");
    expect(clicks[0]?.href).toContain("blob:export");
    expect(await downloaded.blob?.text()).toBe(CSV);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("shows an error instead of throwing when the export request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("nope", { status: 500 })),
    );

    render(<ExportButton filter={{ agent: "Anna Snelling" }} />);
    screen.getByRole("button", { name: "Exportar CSV" }).click();

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Não foi possível exportar o CSV",
    );
  });
});
