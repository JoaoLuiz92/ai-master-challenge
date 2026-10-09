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
          }),
        ]}
        onSelectAgent={() => undefined}
      />,
    );

    const headers = screen.getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toEqual(["Vendedor", "Na fila", "Valor", "Esfriando", "Bons esfriando"]);

    const anna = screen.getByRole("row", { name: /Anna Snelling/ });
    expect(within(anna).getByText("8")).toBeTruthy();
    expect(within(anna).getByText("US$ 48.210")).toBeTruthy();
    expect(within(anna).getByText("3")).toBeTruthy();
    expect(within(anna).getByText("1")).toBeTruthy();

    const darcel = screen.getByRole("row", { name: /Darcel Schlecht/ });
    expect(within(darcel).getByText("2")).toBeTruthy();
    expect(within(darcel).getByText("US$ 1.000")).toBeTruthy();
    expect(within(darcel).getAllByText("0")).toHaveLength(2);
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
