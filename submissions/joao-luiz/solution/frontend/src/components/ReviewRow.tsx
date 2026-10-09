import type { ReviewItem } from "../api/client";

export function parkedReason(item: ReviewItem): string {
  const parts: string[] = [];
  if (!item.account) {
    parts.push("sem conta");
  }
  if (item.age_days === null) {
    parts.push("sem data");
  }
  return parts.join(" · ");
}

export function ReviewRow({ item }: { item: ReviewItem }) {
  return (
    <article className="review-row">
      <h3>{item.product}</h3>
      <p>{parkedReason(item)}</p>
      <p>{item.action}</p>
    </article>
  );
}
