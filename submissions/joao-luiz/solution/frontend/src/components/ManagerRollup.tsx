import type { RollupRow } from "../api/client";
import { RollupTable } from "./RollupTable";

export function ManagerRollup({ rows }: { rows: RollupRow[] }) {
  return <RollupTable rows={rows} onSelectAgent={() => undefined} />;
}
