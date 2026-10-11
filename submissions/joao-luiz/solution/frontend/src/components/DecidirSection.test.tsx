/** @vitest-environment jsdom */

import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { QueueItem } from "../api/client";
import { DecidirSection } from "./DecidirSection";

const WALL =
  "Nenhum deal da base fechou depois de 138 dias; 12 abertos já passaram disso.";

function parked(overrides: Partial<QueueItem> = {}): QueueItem {
  return {
    opportunity_id: "OPP-D1",
    product: "GTX Plus",
    account: "Globex",
    value: 500,
    deal_stage: "Engaging",
    age_days: 200,
    score: 0,
    estado: "Decidir",
    confidence: "Baixa",
    reason: WALL,
    action: "Requalificar ou encerrar",
    ...overrides,
  };
}

function appearsBefore(first: HTMLElement, second: HTMLElement): boolean {
  return (first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
}

afterEach(cleanup);

describe("DecidirSection", () => {
  it("renders Decidir apart from Trabalhar, ordered by price desc, with the wall sentence", () => {
    render(
      <DecidirSection
        items={[
          parked({ opportunity_id: "cheap", product: "GTK 500", value: 50 }),
          parked({ opportunity_id: "rich", product: "GTX Pro", value: 4000 }),
        ]}
      />,
    );

    const region = screen.getByRole("region", { name: "Decidir" });
    expect(within(region).getByText(WALL)).toBeTruthy();
    expect(within(region).getAllByText("Requalificar ou encerrar")).toHaveLength(2);

    const expensive = within(region).getByText("GTX Pro");
    const cheap = within(region).getByText("GTK 500");
    expect(appearsBefore(expensive, cheap)).toBe(true);
    expect(within(region).queryByText("Avançar proposta")).toBeNull();
    expect(within(region).queryByText(/fecharam/)).toBeNull();
  });

  it("shows the decision list with a work empty state, not an error", () => {
    render(<DecidirSection items={[parked()]} workEmpty />);

    expect(screen.getByRole("status").textContent).toBe("Nada para trabalhar agora.");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(screen.getByRole("region", { name: "Decidir" })).toBeTruthy();
    expect(screen.getByText("GTX Plus")).toBeTruthy();
    expect(screen.getByText("Requalificar ou encerrar")).toBeTruthy();
  });

  it("renders nothing when there is no decision queue", () => {
    const { container } = render(<DecidirSection items={[]} workEmpty />);
    expect(container.textContent).toBe("");
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
