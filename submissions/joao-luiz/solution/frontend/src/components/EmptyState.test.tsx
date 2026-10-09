/** @vitest-environment jsdom */

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { EmptyState } from "./EmptyState";

afterEach(cleanup);

describe("EmptyState", () => {
  it("tells the user to pick another vendedor for a ghost agent", () => {
    render(<EmptyState kind="ghost-agent" />);
    expect(screen.getByRole("status").textContent).toBe(
      "Este nome não tem carteira. Escolha outro vendedor.",
    );
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("points to Revisar when the workable queue is empty", () => {
    render(<EmptyState kind="only-revisar" count={4} />);
    expect(screen.getByRole("status").textContent).toBe("Nada trabalhável. 4 em Revisar.");
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("says there are no sellers in the manager slice", () => {
    render(<EmptyState kind="no-sellers" />);
    expect(screen.getByRole("status").textContent).toBe(
      "nenhum vendedor neste gestor/escritório",
    );
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
