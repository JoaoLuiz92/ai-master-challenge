"""Agent, manager, and office options for the filters.

An agent with no pipeline rows is an empty state, not a portfolio.
"""

import pandas as pd
from fastapi import APIRouter, Request

from app.ingestion.repository import Deal

router = APIRouter()


def build_agent_catalog(deals: tuple[Deal, ...], teams: pd.DataFrame) -> dict:
    """Roster from sales_teams, deal counts from the in-memory repository."""
    counts: dict[str, int] = {}
    for deal in deals:
        counts[deal.sales_agent] = counts.get(deal.sales_agent, 0) + 1

    agents: list[dict] = []
    seen: set[str] = set()
    for row in teams.itertuples(index=False):
        name = str(row.sales_agent)
        seen.add(name)
        count = counts.get(name, 0)
        agents.append(
            {
                "sales_agent": name,
                "manager": _text(row.manager),
                "regional_office": _text(row.regional_office),
                "deal_count": count,
                "empty": count == 0,
            }
        )
    for name in sorted(counts):
        if name in seen:
            continue
        agents.append(
            {
                "sales_agent": name,
                "manager": None,
                "regional_office": None,
                "deal_count": counts[name],
                "empty": False,
            }
        )
    agents.sort(key=lambda item: item["sales_agent"])
    managers = sorted({item["manager"] for item in agents if item["manager"]})
    offices = sorted({item["regional_office"] for item in agents if item["regional_office"]})
    return {"agents": agents, "managers": managers, "offices": offices}


@router.get("/api/agents")
def get_agents(request: Request) -> dict:
    return build_agent_catalog(request.app.state.deals, request.app.state.raw_dataset.sales_teams)


def _text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None
