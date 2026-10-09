/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { useViewRoute } from "./useViewRoute";

function Probe() {
  const { route, navigate } = useViewRoute();
  return (
    <div>
      <span data-testid="station">{route.station}</span>
      <span data-testid="agente">{route.agente ?? ""}</span>
      <span data-testid="gestor">{route.gestor ?? ""}</span>
      <button type="button" onClick={() => navigate({ station: "gestor", gestor: "Dustin Brinkmann" })}>
        ir-gestor
      </button>
    </div>
  );
}

afterEach(() => {
  cleanup();
  window.history.replaceState(null, "", "/");
});

describe("useViewRoute", () => {
  it("parses the current location on the first read", () => {
    window.history.replaceState(null, "", "/vendedor?agente=Anna+Snelling");
    render(<Probe />);
    expect(screen.getByTestId("station").textContent).toBe("vendedor");
    expect(screen.getByTestId("agente").textContent).toBe("Anna Snelling");
    expect(window.location.pathname).toBe("/vendedor");
  });

  it("pushes the next URL without a full reload", () => {
    window.history.replaceState(null, "", "/vendedor?agente=Anna+Snelling");
    const lengthBefore = window.history.length;
    render(<Probe />);

    act(() => {
      screen.getByRole("button", { name: "ir-gestor" }).click();
    });

    expect(screen.getByTestId("station").textContent).toBe("gestor");
    expect(screen.getByTestId("gestor").textContent).toBe("Dustin Brinkmann");
    expect(window.location.pathname).toBe("/gestor");
    expect(window.location.search).toBe("?gestor=Dustin+Brinkmann");
    expect(window.history.length).toBeGreaterThanOrEqual(lengthBefore);
  });

  it("updates the route on popstate back/forward", () => {
    window.history.replaceState(null, "", "/vendedor?agente=Anna+Snelling");
    render(<Probe />);

    act(() => {
      screen.getByRole("button", { name: "ir-gestor" }).click();
    });
    expect(screen.getByTestId("station").textContent).toBe("gestor");

    act(() => {
      window.history.pushState(null, "", "/vendedor?agente=Anna+Snelling");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });

    expect(screen.getByTestId("station").textContent).toBe("vendedor");
    expect(screen.getByTestId("agente").textContent).toBe("Anna Snelling");
    expect(window.location.pathname).toBe("/vendedor");
  });
});
