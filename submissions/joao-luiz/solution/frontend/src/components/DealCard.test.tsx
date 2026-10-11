/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import type { QueueItem } from "../api/client";
import { DealCard, SCORE_TOOLTIP } from "./DealCard";

function deal(overrides: Partial<QueueItem> = {}): QueueItem {
  return {
    opportunity_id: "OPP-1",
    product: "GTX Pro",
    account: "Acme",
    value: 1000,
    deal_stage: "Engaging",
    age_days: 40,
    score: 90,
    estado: "Focar",
    confidence: "Alta",
    reason: "47% dos deals desta idade fecharam.",
    action: "Avançar proposta",
    ...overrides,
  };
}

function appearsBefore(first: HTMLElement, second: HTMLElement): boolean {
  return (first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
}

afterEach(cleanup);

describe("DealCard focar", () => {
  it("renders action, then chance sentence, then value/age, then Estado", () => {
    render(<DealCard item={deal()} variant="focar" />);

    const action = screen.getByRole("heading", { name: "Avançar proposta" });
    const chance = screen.getByText("47% dos deals desta idade fecharam.");
    const value = screen.getByText("US$ 1.000");
    const age = screen.getByText("40");
    const estado = screen.getByText("Focar");

    expect(appearsBefore(action, chance)).toBe(true);
    expect(appearsBefore(chance, value)).toBe(true);
    expect(appearsBefore(value, age)).toBe(true);
    expect(appearsBefore(age, estado)).toBe(true);
  });

  it("shows the chance sentence and Portuguese labels", () => {
    render(<DealCard item={deal()} variant="focar" />);

    expect(screen.getByText("47% dos deals desta idade fecharam.")).toBeTruthy();
    expect(screen.getByText("Chance")).toBeTruthy();
    expect(screen.getByText("Valor")).toBeTruthy();
    expect(screen.getByText("Dias no funil")).toBeTruthy();
    expect(screen.getByText("Estado")).toBeTruthy();
    expect(screen.queryByText(/dentro do ciclo/)).toBeNull();
    expect(screen.queryByText(/urgência/i)).toBeNull();
  });

  it("keeps SCORE secondary with the tooltip and hides stage, percentil, and PRIORIDADE", () => {
    const { container } = render(<DealCard item={deal()} variant="focar" />);
    const score = screen.getByText(/SCORE/);

    expect(score.className).toContain("deal-card__score");
    expect(score.getAttribute("title")).toBe(SCORE_TOOLTIP);
    expect(SCORE_TOOLTIP).toBe("posição nesta visão, 0–100");
    expect(container.textContent).not.toMatch(/percentil/i);
    expect(screen.queryByText("Estágio")).toBeNull();
    expect(screen.queryByText("Engaging")).toBeNull();
    expect(screen.queryByText(/PRIORIDADE/i)).toBeNull();
    expect(screen.getByText("Valor").closest("div")?.textContent).toContain("US$ 1.000");
  });

  it("shows the Esfriando badge only when age_days is strictly greater than 106", () => {
    const { unmount } = render(<DealCard item={deal({ age_days: 107 })} variant="focar" />);
    const badge = screen.getByText("Esfriando");
    expect(badge.className).toContain("badge-cooling");
    unmount();

    render(<DealCard item={deal({ age_days: 106 })} variant="focar" />);
    expect(screen.queryByText("Esfriando")).toBeNull();
  });
});

describe("DealCard handoff", () => {
  it("shows Passar para colega only when the drill asks for it", () => {
    const onPass = () => undefined;
    const { unmount } = render(<DealCard item={deal()} variant="focar" onPass={onPass} />);
    expect(screen.getByRole("button", { name: "Passar para colega" })).toBeTruthy();
    unmount();

    render(<DealCard item={deal({ estado: "Acompanhar" })} variant="acompanhar" onPass={onPass} />);
    expect(screen.getByRole("button", { name: "Passar para colega" })).toBeTruthy();
    cleanup();

    render(<DealCard item={deal()} variant="focar" />);
    expect(screen.queryByRole("button", { name: "Passar para colega" })).toBeNull();
  });

  it("prints Veio de as text and omits it when the deal was not passed", () => {
    const { unmount } = render(
      <DealCard item={deal({ from_agent: "Ana" })} variant="focar" />,
    );
    const trace = screen.getByText("Veio de Ana");
    expect(trace.tagName).toBe("P");
    expect(trace.querySelector("button")).toBeNull();
    unmount();

    render(<DealCard item={deal()} variant="focar" />);
    expect(screen.queryByText(/Veio de/)).toBeNull();
  });
});

describe("DealCard acompanhar", () => {
  it("renders a compact row with product, account, value, action, and SCORE in the corner", () => {
    render(
      <DealCard
        item={deal({ estado: "Acompanhar", score: 40 })}
        variant="acompanhar"
      />,
    );

    expect(screen.getByText("GTX Pro")).toBeTruthy();
    expect(screen.getByText("Acme")).toBeTruthy();
    expect(screen.getByText("US$ 1.000")).toBeTruthy();
    expect(screen.getByText("Avançar proposta")).toBeTruthy();
    expect(screen.getByText("47% dos deals desta idade fecharam.")).toBeTruthy();
    const score = screen.getByText(/SCORE/);
    expect(score.className).toContain("deal-card__score");
    expect(score.getAttribute("title")).toBe(SCORE_TOOLTIP);
    expect(screen.queryByText("Engaging")).toBeNull();
  });
});
