/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SituationStrip } from "./SituationStrip";

afterEach(cleanup);

describe("SituationStrip", () => {
  it("renders labels and values as text and number, without icons", () => {
    render(
      <SituationStrip
        items={[
          { label: "Valor em Focar", value: "US$ 1.000" },
          { label: "Nº Focar", value: "2" },
          { label: "Esfriando", value: "1" },
          { label: "Revisar", value: "3", onActivate: () => undefined },
        ]}
      />,
    );

    expect(screen.getByText("Valor em Focar")).toBeTruthy();
    expect(screen.getByText("US$ 1.000")).toBeTruthy();
    expect(screen.getByText("Nº Focar")).toBeTruthy();
    expect(screen.getByText("Esfriando")).toBeTruthy();
    expect(screen.getByText("Revisar")).toBeTruthy();
    expect(document.querySelector("svg")).toBeNull();
    expect(document.querySelector("img")).toBeNull();
  });

  it("turns only items with onActivate into buttons", () => {
    const onFocar = vi.fn();
    const onRevisar = vi.fn();
    render(
      <SituationStrip
        items={[
          { label: "Valor em Focar", value: "US$ 1.000", onActivate: onFocar },
          { label: "Esfriando", value: "1" },
          { label: "Bons esfriando", value: "0" },
          { label: "Revisar", value: "3", onActivate: onRevisar },
        ]}
      />,
    );

    const focar = screen.getByRole("button", { name: /Valor em Focar/ });
    const revisar = screen.getByRole("button", { name: /Revisar/ });
    focar.click();
    revisar.click();
    expect(onFocar).toHaveBeenCalledTimes(1);
    expect(onRevisar).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("button", { name: /Esfriando/ })).toBeNull();
    expect(screen.queryByRole("button", { name: /Bons esfriando/ })).toBeNull();
    expect(screen.getByText("Esfriando").closest("button")).toBeNull();
  });
});
