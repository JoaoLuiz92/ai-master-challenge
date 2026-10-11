import type { RollupRow } from "../api/client";
import { formatValue } from "../format/money";
import { RollupTable } from "./RollupTable";

const LABELS = {
  parked: "Valor parado",
} as const;

export function ManagerRollup({
  rows,
  parkedValue,
  onSelectAgent,
}: {
  rows: RollupRow[];
  parkedValue?: number;
  onSelectAgent: (agent: string) => void;
}) {
  const parked =
    parkedValue ?? rows.reduce((sum, row) => sum + (row.decidir_value ?? 0), 0);
  return (
    <div className="manager-rollup">
      <p className="parked-value">
        <span className="parked-value__label">{LABELS.parked}</span>{" "}
        <mark>{formatValue(parked)}</mark>
      </p>
      <RollupTable rows={rows} onSelectAgent={onSelectAgent} />
    </div>
  );
}
