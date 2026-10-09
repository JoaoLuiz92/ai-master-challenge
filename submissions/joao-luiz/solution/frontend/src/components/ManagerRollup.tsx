import type { RollupRow } from "../api/client";

const LABELS = {
  vendor: "Vendedor",
  queued: "Na fila",
  value: "Valor",
  cooling: "Esfriando",
  goodCooling: "Bons esfriando",
} as const;

export function ManagerRollup({ rows }: { rows: RollupRow[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>{LABELS.vendor}</th>
          <th>{LABELS.queued}</th>
          <th>{LABELS.value}</th>
          <th>{LABELS.cooling}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((item) => (
          <tr key={item.sales_agent}>
            <td>{item.sales_agent}</td>
            <td>{item.queued_count}</td>
            <td>{formatValue(item.expected_value_sum)}</td>
            <td>{item.cooling_count}</td>
            {item.good_deals_cooling > 0 ? (
              <td>
                <mark>{`${LABELS.goodCooling} ${item.good_deals_cooling}`}</mark>
              </td>
            ) : null}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function formatValue(value: number): string {
  return `US$ ${value.toLocaleString("pt-BR")}`;
}
