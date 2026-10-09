/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { ReviewItem } from "../api/client";
import { ReviewRow } from "./ReviewRow";

function review(overrides: Partial<ReviewItem> = {}): ReviewItem {
  return {
    opportunity_id: "OPP-REVIEW",
    product: "GTK 500",
    account: null,
    deal_stage: "Engaging",
    value: 26768,
    age_days: 40,
    estado: "Revisar",
    reason: "GTK 500 · US$ 26.768",
    action: "Qualificar conta/dados",
    ...overrides,
  };
}

afterEach(cleanup);

describe("ReviewRow", () => {
  it("shows product, missing-account reason, and action, with no SCORE", () => {
    const { container } = render(<ReviewRow item={review({ account: null, age_days: 40 })} />);

    expect(screen.getByText("GTK 500")).toBeTruthy();
    expect(screen.getByText("sem conta")).toBeTruthy();
    expect(screen.getByText("Qualificar conta/dados")).toBeTruthy();
    expect(container.textContent).not.toMatch(/SCORE/i);
  });

  it("shows the missing-date reason when engage date is absent", () => {
    const { container } = render(
      <ReviewRow item={review({ account: "Acme", age_days: null })} />,
    );

    expect(screen.getByText("GTK 500")).toBeTruthy();
    expect(screen.getByText("sem data")).toBeTruthy();
    expect(screen.getByText("Qualificar conta/dados")).toBeTruthy();
    expect(container.textContent).not.toMatch(/SCORE/i);
  });
});
