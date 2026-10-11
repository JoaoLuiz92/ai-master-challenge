/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { RollupRow } from "../api/client";
import { RollupTable } from "./RollupTable";

function row(overrides: Partial<RollupRow> = {}): RollupRow {
  return {
    sales_agent: "Anna Snelling",
    queued_count: 8,
    expected_value_sum: 48210,
    cooling_count: 3,
    good_deals_cooling: 1,
    trabalhar_count: 5,
    trabalhar_value: 800,
    decidir_count: 3,
    decidir_value: 47410,
    ...overrides,
  };
}

afterEach(cleanup);

describe("RollupTable", () => {
  it("renders a header cell for every column, including Bons esfriando", () => {
    render(
      <RollupTable
        rows={[
          row(),
          row({
            sales_agent: "Darcel Schlecht",
            queued_count: 2,
            expected_value_sum: 1000,
            cooling_count: 0,
            good_deals_cooling: 0,
            trabalhar_count: 2,
            trabalhar_value: 1000,
            decidir_count: 0,
            decidir_value: 0,
          }),
        ]}
        onSelectAgent={() => undefined}
      />,
    );

    const headers = screen.getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toEqual([
      "Vendedor",
      "Trabalhar",
      "Valor trabalhar",
      "Decidir",
      "Valor parado",
      "Esfriando",
      "Bons esfriando",
    ]);

    const anna = screen.getByRole("row", { name: /Anna Snelling/ });
    const annaCells = within(anna).getAllByRole("cell").map((cell) => cell.textContent);
    expect(annaCells).toEqual(["5", "US$ 800", "3", "US$ 47.410", "3", "1"]);
    expect(within(anna).getByText("US$ 47.410").closest("mark")).not.toBeNull();

    const darcel = screen.getByRole("row", { name: /Darcel Schlecht/ });
    expect(within(darcel).getByText("2")).toBeTruthy();
    expect(within(darcel).getByText("US$ 1.000")).toBeTruthy();
    expect(within(darcel).getByText("US$ 0")).toBeTruthy();
  });

  it("calls onSelectAgent when a seller row is activated", () => {
    const onSelectAgent = vi.fn();
    render(
      <RollupTable
        rows={[row(), row({ sales_agent: "Darcel Schlecht", good_deals_cooling: 0 })]}
        onSelectAgent={onSelectAgent}
      />,
    );

    screen.getByRole("button", { name: "Anna Snelling" }).click();
    expect(onSelectAgent).toHaveBeenCalledTimes(1);
    expect(onSelectAgent).toHaveBeenCalledWith("Anna Snelling");
  });
});
