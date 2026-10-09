/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AppShell, TEMPORAL_ANCHOR } from "./AppShell";

afterEach(cleanup);

describe("AppShell", () => {
  it("navigates the rail between vendedor and gestor and marks the active station", () => {
    const onNavigate = vi.fn();
    render(
      <AppShell route={{ station: "vendedor" }} onNavigate={onNavigate}>
        <p>estação</p>
      </AppShell>,
    );

    expect(screen.getByRole("button", { name: "Vendedor" }).getAttribute("aria-current")).toBe(
      "page",
    );
    expect(screen.getByRole("button", { name: "Gestor" }).getAttribute("aria-current")).toBeNull();

    screen.getByRole("button", { name: "Gestor" }).click();
    expect(onNavigate).toHaveBeenCalledWith("gestor");
  });

  it("shows the temporal anchor and no Visão select", () => {
    render(
      <AppShell route={{ station: "gestor" }} onNavigate={() => undefined}>
        <p>estação</p>
      </AppShell>,
    );

    expect(screen.getByText(TEMPORAL_ANCHOR)).toBeTruthy();
    expect(TEMPORAL_ANCHOR).toBe("Visão em 31/12/2017");
    expect(screen.queryByRole("combobox")).toBeNull();
    expect(screen.queryByLabelText("Visão")).toBeNull();
    expect(document.querySelector("select")).toBeNull();
    expect(screen.getByRole("button", { name: "Gestor" }).getAttribute("aria-current")).toBe(
      "page",
    );
  });
});
