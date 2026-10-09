/** @vitest-environment jsdom */

import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { CollapsibleBand } from "./CollapsibleBand";

afterEach(cleanup);

describe("CollapsibleBand", () => {
  it("starts expanded when defaultOpen is true and shows the count", () => {
    render(
      <CollapsibleBand title="Focar" count={8} defaultOpen>
        <p>herói</p>
      </CollapsibleBand>,
    );

    expect(screen.getByRole("button", { name: "Focar (8)" }).getAttribute("aria-expanded")).toBe(
      "true",
    );
    expect(screen.getByText("herói")).toBeTruthy();
  });

  it("starts collapsed with the count in the title", () => {
    render(
      <CollapsibleBand title="Acompanhar" count={32} defaultOpen={false}>
        <p>linha compacta</p>
      </CollapsibleBand>,
    );

    expect(screen.getByRole("button", { name: "Acompanhar (32)" }).getAttribute("aria-expanded")).toBe(
      "false",
    );
    expect(screen.queryByText("linha compacta")).toBeNull();
  });

  it("toggles open and closed when the title is activated", () => {
    render(
      <CollapsibleBand title="Revisar" count={4} defaultOpen={false}>
        <p>parado</p>
      </CollapsibleBand>,
    );

    const title = screen.getByRole("button", { name: "Revisar (4)" });
    act(() => {
      title.click();
    });
    expect(title.getAttribute("aria-expanded")).toBe("true");
    expect(screen.getByText("parado")).toBeTruthy();

    act(() => {
      title.click();
    });
    expect(title.getAttribute("aria-expanded")).toBe("false");
    expect(screen.queryByText("parado")).toBeNull();
  });
});
