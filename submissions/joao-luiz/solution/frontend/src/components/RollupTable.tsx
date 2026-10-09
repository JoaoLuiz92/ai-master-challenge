import type { RollupRow } from "../api/client";
import { formatValue } from "../format/money";

const LABELS = {
  vendor: "Vendedor",
  queued: "Na fila",
  value: "Valor",
  cooling: "Esfriando",
  goodCooling: "Bons esfriando",
} as const;

export function RollupTable({
  rows,
  onSelectAgent,
}: {
  rows: RollupRow[];
  onSelectAgent: (agent: string) => void;
}) {
  return (
    <table className="rollup-table">
      <thead>
        <tr>
          <th>{LABELS.vendor}</th>
          <th>{LABELS.queued}</th>
          <th>{LABELS.value}</th>
          <th>{LABELS.cooling}</th>
          <th>{LABELS.goodCooling}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((item) => (
          <tr key={item.sales_agent}>
            <th scope="row">
              <button type="button" onClick={() => onSelectAgent(item.sales_agent)}>
                {item.sales_agent}
              </button>
            </th>
            <td>{item.queued_count}</td>
            <td>{formatValue(item.expected_value_sum)}</td>
            <td>{item.cooling_count}</td>
            <td>
              {item.good_deals_cooling > 0 ? (
                <mark>{item.good_deals_cooling}</mark>
              ) : (
                item.good_deals_cooling
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
