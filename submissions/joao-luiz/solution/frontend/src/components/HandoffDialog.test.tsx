/** @vitest-environment jsdom */

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { HandoffDialog } from "./HandoffDialog";

const fetchHandoffCandidates = vi.fn();
const postHandoff = vi.fn();

vi.mock("../api/client", () => ({
  fetchHandoffCandidates: (...args: unknown[]) => fetchHandoffCandidates(...args),
  postHandoff: (...args: unknown[]) => postHandoff(...args),
}));

afterEach(() => {
  cleanup();
  fetchHandoffCandidates.mockReset();
  postHandoff.mockReset();
});

function renderDialog(ageDays: number) {
  const onConfirmed = vi.fn();
  const onCancel = vi.fn();
  render(
    <HandoffDialog
      opportunityId="OPP-1"
      ageDays={ageDays}
      onConfirmed={onConfirmed}
      onCancel={onCancel}
    />,
  );
  return { onConfirmed, onCancel };
}

describe("HandoffDialog", () => {
  it("lists same-office colleagues and posts the chosen one", async () => {
    fetchHandoffCandidates.mockResolvedValue(["Bruno", "Otto"]);
    postHandoff.mockResolvedValue({
      opportunity_id: "OPP-1",
      sales_agent: "Bruno",
      from_agent: "Ana",
    });
    const { onConfirmed } = renderDialog(40);

    expect(await screen.findByRole("radio", { name: "Bruno" })).toBeTruthy();
    expect(screen.getByRole("radio", { name: "Otto" })).toBeTruthy();
    screen.getByRole("radio", { name: "Bruno" }).click();
    screen.getByRole("button", { name: "Confirmar" }).click();

    await waitFor(() => {
      expect(postHandoff).toHaveBeenCalledWith({ opportunity_id: "OPP-1", to_agent: "Bruno" });
    });
    expect(onConfirmed).toHaveBeenCalled();
  });

  it("includes the cooling sentence only when age_days is greater than 106", async () => {
    fetchHandoffCandidates.mockResolvedValue(["Bruno"]);
    const cooling = renderDialog(107);
    expect(await screen.findByText("Este negócio está esfriando.")).toBeTruthy();
    cooling.onCancel.mockClear();
    cleanup();

    fetchHandoffCandidates.mockResolvedValue(["Bruno"]);
    renderDialog(106);
    expect(await screen.findByRole("radio", { name: "Bruno" })).toBeTruthy();
    expect(screen.queryByText("Este negócio está esfriando.")).toBeNull();
  });

  it("cancel does not post and leaves the choice to the caller", async () => {
    fetchHandoffCandidates.mockResolvedValue(["Bruno"]);
    const { onCancel } = renderDialog(40);

    expect(await screen.findByRole("radio", { name: "Bruno" })).toBeTruthy();
    screen.getByRole("radio", { name: "Bruno" }).click();
    screen.getByRole("button", { name: "Cancelar" }).click();

    expect(postHandoff).not.toHaveBeenCalled();
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("shows the refusal detail and does not confirm", async () => {
    fetchHandoffCandidates.mockResolvedValue(["Bruno"]);
    postHandoff.mockRejectedValue(new Error("Colega não encontrado"));
    const { onConfirmed } = renderDialog(40);

    (await screen.findByRole("radio", { name: "Bruno" })).click();
    screen.getByRole("button", { name: "Confirmar" }).click();

    expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Colega não encontrado");
    expect(onConfirmed).not.toHaveBeenCalled();
  });

  it("says there is no colleague in this office and does not post", async () => {
    fetchHandoffCandidates.mockResolvedValue([]);
    renderDialog(40);

    expect(await screen.findByText("Nenhum colega neste escritório")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Confirmar" })).toBeNull();
    expect(postHandoff).not.toHaveBeenCalled();
  });
});
