import type { QueueItem, ReviewItem } from "../api/client";
import { EmptyState } from "./EmptyState";
import { QueueList } from "./QueueList";

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
                  <dt>Estado</dt>
                  <dd>{item.estado}</dd>
                </div>
                <div>
                  <dt>Ação</dt>
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
  emptyMessage?: string | null;
  ghostAgent?: boolean;
}) {
  const showEmpty = ghostAgent || items.length === 0;

  return (
    <div>
      {ghostAgent ? (
        <EmptyState kind="ghost-agent" />
      ) : showEmpty ? (
        <EmptyState kind="only-revisar" count={revisar.length} />
      ) : (
        <QueueList items={items} />
      )}
      <ReviewSection items={revisar} />
    </div>
  );
}
