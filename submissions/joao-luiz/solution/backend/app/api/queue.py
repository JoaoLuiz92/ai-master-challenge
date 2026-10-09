"""Workable queue and Revisar section for the current filter."""

from dataclasses import asdict

from fastapi import APIRouter, Request

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.views.explain import explain
from app.views.filter import split_view
from app.views.query import QueueItem, ViewFilter, build_queue

router = APIRouter()


@router.get("/api/queue")
def get_queue(
    request: Request,
    view: str | None = None,
    agent: str | None = None,
    manager: str | None = None,
    office: str | None = None,
) -> dict:
    """SCORE and ESTADO are computed on this filter, not on a cached global rank."""
    selected = ViewFilter(
        agent=_blank(agent),
        manager=_blank(manager),
        office=_blank(office),
    )
    deals: tuple[Deal, ...] = request.app.state.deals
    queue = build_queue(deals, selected)
    revisar = split_view(
        deals,
        agent=selected.agent,
        manager=selected.manager,
        office=selected.office,
    ).revisar
    return {
        "view": _blank(view),
        "items": [_queue_item(item) for item in queue.items],
        "revisar": [_review_item(deal) for deal in revisar],
        "empty_message": queue.empty_message,
    }


def _queue_item(item: QueueItem) -> dict:
    return asdict(item)


def _review_item(deal: Deal) -> dict:
    age = age_days(deal.engage_date)
    text = explain(deal.product, deal.value, age, revisar=True)
    return {
        "opportunity_id": deal.opportunity_id,
        "product": deal.product,
        "account": deal.account,
        "deal_stage": deal.deal_stage,
        "value": deal.value,
        "age_days": age,
        "estado": "Revisar",
        "reason": text.reason,
        "action": text.action,
    }


def _blank(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value
