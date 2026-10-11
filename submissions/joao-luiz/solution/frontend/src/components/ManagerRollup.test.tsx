/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { RollupRow } from "../api/client";
import { ManagerRollup } from "./ManagerRollup";

function row(overrides: Partial<RollupRow> = {}): RollupRow {
  return {
    sales_agent: "Anna Snelling",
    queued_count: 3,
    expected_value_sum: 1100,
    cooling_count: 0,
    good_deals_cooling: 0,
    trabalhar_count: 1,
    trabalhar_value: 100,
    decidir_count: 2,
    decidir_value: 1000,
    ...overrides,
  };
}

afterEach(cleanup);

describe("ManagerRollup", () => {
  it("splits Trabalhar vs Decidir per agent and highlights parked value", () => {
    render(
      <ManagerRollup
        rows={[
          row(),
          row({
            sales_agent: "Darcel Schlecht",
            queued_count: 1,
            expected_value_sum: 50,
            trabalhar_count: 0,
            trabalhar_value: 0,
            decidir_count: 1,
            decidir_value: 50,
          }),
        ]}
        parkedValue={1050}
        onSelectAgent={() => undefined}
      />,
    );

    const parked = document.querySelector(".parked-value") as HTMLElement;
    expect(parked.textContent).toContain("Valor parado");
    expect(parked.querySelector("mark")?.textContent).toBe("US$ 1.050");

    const headers = screen.getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toContain("Trabalhar");
    expect(headers).toContain("Valor trabalhar");
    expect(headers).toContain("Decidir");
    expect(headers).toContain("Valor parado");

    const anna = screen.getByRole("row", { name: /Anna Snelling/ });
    expect(within(anna).getByText("1")).toBeTruthy();
    expect(within(anna).getByText("US$ 100")).toBeTruthy();
    expect(within(anna).getByText("2")).toBeTruthy();
    expect(within(anna).getByText("US$ 1.000").closest("mark")).not.toBeNull();
  });

  it("sums parked value from rows when the payload omits the total", () => {
    const onSelectAgent = vi.fn();
    render(
      <ManagerRollup
        rows={[row(), row({ sales_agent: "Darcel Schlecht", decidir_value: 50 })]}
        onSelectAgent={onSelectAgent}
      />,
    );

    expect(document.querySelector(".parked-value mark")?.textContent).toBe("US$ 1.050");
    screen.getByRole("button", { name: "Anna Snelling" }).click();
    expect(onSelectAgent).toHaveBeenCalledWith("Anna Snelling");
  });
});
