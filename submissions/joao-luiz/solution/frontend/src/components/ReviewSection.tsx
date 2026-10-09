import type { QueueItem, ReviewItem } from "../api/client";
import { QueueList } from "./QueueList";

const EMPTY_VIEW_MESSAGE = "sem deals nesta visão";

const LABELS = {
  estado: "Estado",
  action: "Ação",
} as const;

export function EmptyState({ message }: { message: string }) {
  return <p role="status">{message}</p>;
}

export function ReviewSection({ items }: { items: ReviewItem[] }) {
  if (items.length === 0) {
    return null;
  }

  return (
    <section aria-labelledby="revisar-heading">
      <h2 id="revisar-heading">Revisar</h2>
      <ul>
        {items.map((item) => (
          <li key={item.opportunity_id}>
            <article>
              <h3>{item.product}</h3>
              <dl>
                <div>
                  <dt>{LABELS.estado}</dt>
                  <dd>{item.estado}</dd>
                </div>
                <div>
                  <dt>{LABELS.action}</dt>
                  <dd>{item.action}</dd>
                </div>
              </dl>
            </article>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function QueueLayout({
  items,
  revisar,
  emptyMessage,
  ghostAgent = false,
}: {
  items: QueueItem[];
  revisar: ReviewItem[];
  emptyMessage: string | null;
  ghostAgent?: boolean;
}) {
  const showEmpty = ghostAgent || items.length === 0;

  return (
    <div>
      {showEmpty ? (
        <EmptyState message={emptyMessage ?? EMPTY_VIEW_MESSAGE} />
      ) : (
        <QueueList items={items} />
      )}
      <ReviewSection items={revisar} />
    </div>
  );
}
