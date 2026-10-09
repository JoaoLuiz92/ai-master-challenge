"""In-memory handoff. The CSVs stay the startup snapshot."""

from collections.abc import Mapping
from dataclasses import dataclass

from app.ingestion.repository import Deal, reassign_deal
from app.views.filter import split_view

TeamRow = tuple[str | None, str | None]

NOT_WORKABLE = "Este negócio não está na fila trabalhável"
UNKNOWN_AGENT = "Colega não encontrado"
OTHER_OFFICE = "Colega de outro escritório"
SAME_OWNER = "Este negócio já está com essa pessoa"


@dataclass(frozen=True)
class HandoffResult:
    ok: bool
    deals: tuple[Deal, ...]
    message: str | None = None
    error_code: str | None = None


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


def assign(
    deals: tuple[Deal, ...],
    opportunity_id: str,
    to_agent: str,
    team_by_agent: Mapping[str, TeamRow],
) -> HandoffResult:
    """Validate, then replace the owner. Never writes a file.

    Order: deal exists and is workable, colleague exists, same office,
    not the current owner. A refusal returns the same tuple.
    """
    deal = _find(deals, opportunity_id)
    if deal is None or not _is_workable(deals, opportunity_id):
        return _reject(deals, "not_workable", NOT_WORKABLE)
    row = team_by_agent.get(to_agent)
    if row is None:
        return _reject(deals, "unknown_agent", UNKNOWN_AGENT)
    manager, office = row
    if not deal.regional_office or office != deal.regional_office:
        return _reject(deals, "other_office", OTHER_OFFICE)
    if to_agent == deal.sales_agent:
        return _reject(deals, "same_owner", SAME_OWNER)
    return HandoffResult(
        ok=True,
        deals=reassign_deal(
            deals,
            opportunity_id,
            to_agent,
            deal.sales_agent,
            manager,
            office,
        ),
    )


def _is_workable(deals: tuple[Deal, ...], opportunity_id: str) -> bool:
    return any(item.opportunity_id == opportunity_id for item in split_view(deals).workable)


def _reject(deals: tuple[Deal, ...], code: str, message: str) -> HandoffResult:
    return HandoffResult(ok=False, deals=deals, message=message, error_code=code)


def _find(deals: tuple[Deal, ...], opportunity_id: str) -> Deal | None:
    for deal in deals:
        if deal.opportunity_id == opportunity_id:
            return deal
    return None
