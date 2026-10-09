import { describe, expect, it } from "vitest";

import { parseLocation, toUrl, type ViewRoute } from "./route";

describe("parseLocation", () => {
  it("reads the vendedor station from the path", () => {
    expect(parseLocation("/vendedor", "")).toEqual({ station: "vendedor" });
  });

  it("reads the gestor station from the path", () => {
    expect(parseLocation("/gestor", "")).toEqual({ station: "gestor" });
  });

  it("reads agente, gestor, and escritorio from the Portuguese query keys", () => {
    expect(
      parseLocation(
        "/gestor",
        "?agente=Anna+Snelling&gestor=Dustin+Brinkmann&escritorio=Central",
      ),
    ).toEqual({
      station: "gestor",
      agente: "Anna Snelling",
      gestor: "Dustin Brinkmann",
      escritorio: "Central",
    });
  });

  it("falls back to vendedor when the path is unknown", () => {
    expect(parseLocation("/desconhecido", "")).toEqual({ station: "vendedor" });
    expect(parseLocation("/", "")).toEqual({ station: "vendedor" });
  });
});

describe("toUrl", () => {
  it("writes Portuguese paths and query keys", () => {
    expect(toUrl({ station: "vendedor" })).toBe("/vendedor");
    expect(toUrl({ station: "gestor" })).toBe("/gestor");
    expect(
      toUrl({
        station: "vendedor",
        agente: "Anna Snelling",
      }),
    ).toBe("/vendedor?agente=Anna+Snelling");
    expect(
      toUrl({
        station: "gestor",
        gestor: "Dustin Brinkmann",
        escritorio: "Central",
      }),
    ).toBe("/gestor?gestor=Dustin+Brinkmann&escritorio=Central");
  });

  it("round-trips station and slice", () => {
    const routes: ViewRoute[] = [
      { station: "vendedor" },
      { station: "vendedor", agente: "Anna Snelling" },
      { station: "gestor" },
      {
        station: "gestor",
        agente: "Anna Snelling",
        gestor: "Dustin Brinkmann",
        escritorio: "Central",
      },
    ];

    for (const route of routes) {
      const url = toUrl(route);
      const [pathname, search = ""] = url.split("?");
      expect(parseLocation(pathname ?? "", search ? `?${search}` : "")).toEqual(route);
      expect(toUrl(parseLocation(pathname ?? "", search ? `?${search}` : ""))).toBe(url);
    }
  });
});
