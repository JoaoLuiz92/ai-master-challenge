/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { RollupRow } from "../api/client";
import { ManagerRollup } from "./ManagerRollup";

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

describe("ManagerRollup", () => {
  it("shows per-agent queued count, expected value, and cooling", () => {
    render(
      <ManagerRollup
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
      />,
    );

    expect(screen.getByText("Vendedor")).toBeTruthy();
    expect(screen.getByText("Na fila")).toBeTruthy();
    expect(screen.getByText("Valor")).toBeTruthy();
    expect(screen.getByText("Esfriando")).toBeTruthy();

    const anna = screen.getByRole("row", { name: /Anna Snelling/ });
    expect(within(anna).getByText("8")).toBeTruthy();
    expect(within(anna).getByText("US$ 48.210")).toBeTruthy();
    expect(within(anna).getByText("3")).toBeTruthy();

    const darcel = screen.getByRole("row", { name: /Darcel Schlecht/ });
    expect(within(darcel).getByText("2")).toBeTruthy();
    expect(within(darcel).getByText("US$ 1.000")).toBeTruthy();
    expect(within(darcel).getByText("0")).toBeTruthy();
  });

  it("highlights only agents with good deals cooling down", () => {
    render(
      <ManagerRollup
        rows={[
          row({ good_deals_cooling: 2, cooling_count: 4 }),
          row({
            sales_agent: "Darcel Schlecht",
            queued_count: 2,
            expected_value_sum: 1000,
            cooling_count: 1,
            good_deals_cooling: 0,
          }),
        ]}
      />,
    );

    const anna = screen.getByRole("row", { name: /Anna Snelling/ });
    expect(within(anna).getByText("Bons esfriando 2")).toBeTruthy();

    const darcel = screen.getByRole("row", { name: /Darcel Schlecht/ });
    expect(within(darcel).queryByText(/Bons esfriando/)).toBeNull();
    expect(within(darcel).getByText("1")).toBeTruthy();
  });
});
