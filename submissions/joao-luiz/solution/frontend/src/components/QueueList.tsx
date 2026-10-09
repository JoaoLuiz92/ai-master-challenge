import type { QueueItem } from "../api/client";
import { DealCard } from "./DealCard";

export function QueueList({ items }: { items: QueueItem[] }) {
  return (
    <ol>
      {items.map((item) => (
        <li key={item.opportunity_id}>
          <DealCard
            item={item}
            variant={item.estado === "Acompanhar" ? "acompanhar" : "focar"}
          />
        </li>
      ))}
    </ol>
  );
}
