import type { QueueItem } from "../api/client";
import { formatValue } from "../format/money";

const LABELS = {
  heading: "Decidir",
  value: "Valor",
  action: "Ação",
  emptyWork: "Nada para trabalhar agora.",
} as const;

export function DecidirSection({
  items,
  workEmpty = false,
}: {
  items: QueueItem[];
  workEmpty?: boolean;
}) {
  if (items.length === 0) {
    return null;
  }
  const ordered = [...items].sort((left, right) => right.value - left.value);
  return (
    <section className="decidir-section" aria-labelledby="decidir-heading">
      {workEmpty ? <p role="status">{LABELS.emptyWork}</p> : null}
      <h2 id="decidir-heading">{LABELS.heading}</h2>
      <p className="decidir-section__wall">{ordered[0].reason}</p>
      <ol>
        {ordered.map((item) => (
          <li key={item.opportunity_id}>
            <article className="decidir-row">
              <h3>{item.product}</h3>
              <p>{item.account}</p>
              <dl>
                <div>
                  <dt>{LABELS.value}</dt>
                  <dd>{formatValue(item.value)}</dd>
                </div>
                <div>
                  <dt>{LABELS.action}</dt>
                  <dd>{item.action}</dd>
                </div>
              </dl>
            </article>
          </li>
        ))}
      </ol>
    </section>
  );
}
