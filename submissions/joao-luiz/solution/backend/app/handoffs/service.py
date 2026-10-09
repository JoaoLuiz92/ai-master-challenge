"""In-memory handoff. The CSVs stay the startup snapshot."""

from collections.abc import Mapping

from app.ingestion.repository import Deal

TeamRow = tuple[str | None, str | None]


def eligible_candidates(
    deals: tuple[Deal, ...],
    opportunity_id: str,
    team_by_agent: Mapping[str, TeamRow] | None = None,
) -> tuple[str, ...]:
    """Same-office colleagues, minus the current owner.

    Unknown deal or an owner without an office returns an empty tuple.
    When `team_by_agent` is given, names come from that roster, so a
    colleague with no deals is still listed. Otherwise names come from deals.
    """
    deal = _find(deals, opportunity_id)
    if deal is None or not deal.regional_office:
        return ()
    if team_by_agent is None:
        names: list[str] = []
        for item in deals:
            if item.regional_office != deal.regional_office:
                continue
            if item.sales_agent == deal.sales_agent or item.sales_agent in names:
                continue
            names.append(item.sales_agent)
        return tuple(names)
    return tuple(
        agent
        for agent, (_manager, office) in team_by_agent.items()
        if office == deal.regional_office and agent != deal.sales_agent
    )


def _find(deals: tuple[Deal, ...], opportunity_id: str) -> Deal | None:
    for deal in deals:
        if deal.opportunity_id == opportunity_id:
            return deal
    return None
