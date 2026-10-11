import type { RollupRow } from "../api/client";
import { formatValue } from "../format/money";

const LABELS = {
  vendor: "Vendedor",
  work: "Trabalhar",
  workValue: "Valor trabalhar",
  decide: "Decidir",
  parked: "Valor parado",
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
          <th>{LABELS.work}</th>
          <th>{LABELS.workValue}</th>
          <th>{LABELS.decide}</th>
          <th>{LABELS.parked}</th>
          <th>{LABELS.cooling}</th>
          <th>{LABELS.goodCooling}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((item) => {
          const parked = item.decidir_value ?? 0;
          return (
            <tr key={item.sales_agent}>
              <th scope="row">
                <button type="button" onClick={() => onSelectAgent(item.sales_agent)}>
                  {item.sales_agent}
                </button>
              </th>
              <td>{item.trabalhar_count ?? 0}</td>
              <td>{formatValue(item.trabalhar_value ?? 0)}</td>
              <td>{item.decidir_count ?? 0}</td>
              <td>
                {parked > 0 ? <mark>{formatValue(parked)}</mark> : formatValue(parked)}
              </td>
              <td>{item.cooling_count}</td>
              <td>
                {item.good_deals_cooling > 0 ? (
                  <mark>{item.good_deals_cooling}</mark>
                ) : (
                  item.good_deals_cooling
                )}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
