"""Move one workable deal to a colleague. Memory only."""

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.handoffs.service import assign
from app.ingestion.repository import Deal

router = APIRouter()

_STATUS = {
    "unknown_agent": 404,
    "same_owner": 409,
    "other_office": 422,
    "not_workable": 422,
}


class HandoffBody(BaseModel):
    opportunity_id: str
    to_agent: str


@router.post("/api/handoff")
def post_handoff(body: HandoffBody, request: Request) -> dict:
    deals: tuple[Deal, ...] = request.app.state.deals
    result = assign(deals, body.opportunity_id, body.to_agent, team_by_agent(request))
    if not result.ok:
        raise HTTPException(
            status_code=_STATUS[result.error_code or "not_workable"],
            detail=result.message,
        )
    request.app.state.deals = result.deals
    moved = next(
        deal for deal in result.deals if deal.opportunity_id == body.opportunity_id
    )
    return {
        "opportunity_id": moved.opportunity_id,
        "sales_agent": moved.sales_agent,
        "from_agent": moved.from_agent,
    }


def team_by_agent(request: Request) -> dict[str, tuple[str | None, str | None]]:
    roster: dict[str, tuple[str | None, str | None]] = {}
    for row in request.app.state.raw_dataset.sales_teams.itertuples(index=False):
        roster[str(row.sales_agent)] = (_text(row.manager), _text(row.regional_office))
    return roster


def _text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None
