"""Split a filtered view into the workable queue and the Revisar section.

Won and Lost stay out of both. They are closed, not bad data.
"""

from dataclasses import dataclass

from app.ingestion.repository import Deal


@dataclass(frozen=True)
class ViewSplit:
    workable: tuple[Deal, ...]
    revisar: tuple[Deal, ...]


def split_view(
    deals: tuple[Deal, ...],
    *,
    agent: str | None = None,
    manager: str | None = None,
    office: str | None = None,
) -> ViewSplit:
    """Workable = Engaging with account and engage_date.

    Missing account and/or engage_date goes to Revisar. A set filter keeps
    only deals of that agent, manager, or office, in both sections.
    """
    workable: list[Deal] = []
    revisar: list[Deal] = []
    for deal in deals:
        if agent is not None and deal.sales_agent != agent:
            continue
        if manager is not None and deal.manager != manager:
            continue
        if office is not None and deal.regional_office != office:
            continue
        if (
            deal.deal_stage == "Engaging"
            and deal.account
            and deal.engage_date is not None
        ):
            workable.append(deal)
        elif not deal.account or deal.engage_date is None:
            revisar.append(deal)
    return ViewSplit(workable=tuple(workable), revisar=tuple(revisar))
