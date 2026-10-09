/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { QueueItem, ReviewItem } from "../api/client";
import { QueueLayout } from "./ReviewSection";

function queued(overrides: Partial<QueueItem> = {}): QueueItem {
  return {
    opportunity_id: "OPP-QUEUE",
    product: "GTX Pro",
    account: "Acme",
    value: 1000,
    deal_stage: "Engaging",
    age_days: 40,
    score: 90,
    estado: "Focar",
    confidence: "Alta",
    reason: "GTX Pro · US$ 1.000 · 40 dias no funil · dentro do ciclo",
    action: "Avançar proposta",
    ...overrides,
  };
}

function review(overrides: Partial<ReviewItem> = {}): ReviewItem {
  return {
    opportunity_id: "OPP-REVIEW",
    product: "GTK 500",
    account: null,
    deal_stage: "Engaging",
    value: 26768,
    age_days: null,
    estado: "Revisar",
    reason: "GTK 500 · US$ 26.768",
    action: "Qualificar conta/dados",
    ...overrides,
  };
}

afterEach(cleanup);

describe("QueueLayout", () => {
  it("shows Revisar in a section separate from the ordered queue", () => {
    render(
      <QueueLayout
        items={[queued()]}
        revisar={[review()]}
        emptyMessage={null}
      />,
    );

    const queue = document.querySelector("ol");
    expect(queue).not.toBeNull();
    expect(within(queue as HTMLOListElement).getByText("GTX Pro")).toBeTruthy();
    expect(within(queue as HTMLOListElement).getByText("Avançar proposta")).toBeTruthy();
    expect(within(queue as HTMLOListElement).queryByText("GTK 500")).toBeNull();
    expect(within(queue as HTMLOListElement).queryByText("Qualificar conta/dados")).toBeNull();

    const revisar = screen.getByRole("region", { name: "Revisar" });
    expect(within(revisar).getByText("GTK 500")).toBeTruthy();
    expect(within(revisar).getByText("Estado")).toBeTruthy();
    expect(within(revisar).getByText("Qualificar conta/dados")).toBeTruthy();
    expect(within(revisar).queryByText("GTX Pro")).toBeNull();
    expect(within(revisar).queryByText("Avançar proposta")).toBeNull();
    expect(
      within(revisar)
        .getAllByText("Revisar")
        .some((node) => node.tagName === "DD"),
    ).toBe(true);
  });

  it("shows an empty state for a ghost agent instead of a portfolio", () => {
    render(
      <QueueLayout
        items={[]}
        revisar={[]}
        emptyMessage="sem deals nesta visão"
        ghostAgent
      />,
    );

    expect(screen.getByRole("status").textContent).toBe("sem deals nesta visão");
    expect(screen.queryByRole("list")).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.queryByRole("region", { name: "Revisar" })).toBeNull();
  });

  it("shows the empty-view message instead of an error and keeps Revisar separate", () => {
    render(
      <QueueLayout
        items={[]}
        revisar={[review()]}
        emptyMessage="sem deals nesta visão"
      />,
    );

    expect(screen.getByRole("status").textContent).toBe("sem deals nesta visão");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(document.querySelector("ol")).toBeNull();

    const revisar = screen.getByRole("region", { name: "Revisar" });
    expect(within(revisar).getByText("GTK 500")).toBeTruthy();
    expect(within(revisar).getByText("Qualificar conta/dados")).toBeTruthy();
  });
});
