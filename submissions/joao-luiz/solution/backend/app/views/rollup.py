"""Per-agent rollup for the manager view. Counts are recomputed per filter."""

from dataclasses import dataclass

from app.ingestion.repository import Deal
from app.views.query import QueueItem, ViewFilter, build_view


@dataclass(frozen=True)
class RollupRow:
    sales_agent: str
    queued_count: int
    expected_value_sum: int
    cooling_count: int
    good_deals_cooling: int
    trabalhar_count: int
    trabalhar_value: int
    decidir_count: int
    decidir_value: int


def build_rollup(
    repo: tuple[Deal, ...],
    view_filter: ViewFilter | None = None,
) -> tuple[RollupRow, ...]:
    """One row per agent with Trabalhar or Decidir in this view."""
    view = build_view(repo, view_filter)
    agent_of = {deal.opportunity_id: deal.sales_agent for deal in repo}
    work: dict[str, list[QueueItem]] = {}
    decide: dict[str, list[QueueItem]] = {}
    for item in view.trabalhar:
        work.setdefault(agent_of[item.opportunity_id], []).append(item)
    for item in view.decidir:
        decide.setdefault(agent_of[item.opportunity_id], []).append(item)
    agents = sorted(set(work) | set(decide))
    rows: list[RollupRow] = []
    for agent in agents:
        working = work.get(agent, [])
        parked = decide.get(agent, [])
        both = working + parked
        rows.append(
            RollupRow(
                sales_agent=agent,
                queued_count=len(both),
                expected_value_sum=sum(item.value for item in both),
                cooling_count=sum(1 for item in both if item.cooling),
                good_deals_cooling=sum(
                    1 for item in working if item.cooling and item.estado == "Focar"
                ),
                trabalhar_count=len(working),
                trabalhar_value=sum(item.value for item in working),
                decidir_count=len(parked),
                decidir_value=sum(item.value for item in parked),
            )
        )
    return tuple(rows)
