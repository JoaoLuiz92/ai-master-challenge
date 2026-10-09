"""Per-agent rollup for the manager view. Counts are recomputed per filter."""

from dataclasses import dataclass

from app.ingestion.repository import Deal
from app.views.query import QueueItem, ViewFilter, build_queue


@dataclass(frozen=True)
class RollupRow:
    sales_agent: str
    queued_count: int
    expected_value_sum: int
    cooling_count: int
    good_deals_cooling: int


def build_rollup(
    repo: tuple[Deal, ...],
    view_filter: ViewFilter | None = None,
) -> tuple[RollupRow, ...]:
    """One row per agent who has a workable deal in this view.

    A good deal cooling down is Focar (the high end of this view's SCORE)
    and Esfriando. Both are recomputed from the filtered queue.
    """
    view = build_queue(repo, view_filter)
    agent_of = {deal.opportunity_id: deal.sales_agent for deal in repo}
    buckets: dict[str, list[QueueItem]] = {}
    for item in view.items:
        buckets.setdefault(agent_of[item.opportunity_id], []).append(item)

    rows: list[RollupRow] = []
    for agent in sorted(buckets):
        items = buckets[agent]
        rows.append(
            RollupRow(
                sales_agent=agent,
                queued_count=len(items),
                expected_value_sum=sum(item.value for item in items),
                cooling_count=sum(1 for item in items if item.cooling),
                good_deals_cooling=sum(
                    1 for item in items if item.cooling and item.estado == "Focar"
                ),
            )
        )
    return tuple(rows)
