import { describe, expect, it } from "vitest";

import { formatValue } from "./money";

describe("formatValue", () => {
  it("formats thousands with the pt-BR separator", () => {
    expect(formatValue(1000)).toBe("US$ 1.000");
    expect(formatValue(48210)).toBe("US$ 48.210");
  });

  it("formats zero", () => {
    expect(formatValue(0)).toBe("US$ 0");
  });
});
