"""Workable queue, Decidir and Revisar for the current filter."""

from dataclasses import asdict

from fastapi import APIRouter, Request

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.views.explain import action_for, explain
from app.views.query import QueueItem, ViewFilter, build_view

router = APIRouter()


@router.get("/api/queue")
def get_queue(
    request: Request,
    view: str | None = None,
    agent: str | None = None,
    manager: str | None = None,
    office: str | None = None,
) -> dict:
    """SCORE is the Trabalhar percentile of this filter."""
    selected = ViewFilter(
        agent=_blank(agent),
        manager=_blank(manager),
        office=_blank(office),
    )
    deals: tuple[Deal, ...] = request.app.state.deals
    result = build_view(deals, selected)
    trabalhar = [_queue_item(item) for item in result.trabalhar]
    decidir = [_queue_item(item) for item in result.decidir]
    revisar = [_review_item(deal) for deal in result.revisar]
    return {
        "view": _blank(view),
        "trabalhar": trabalhar,
        "decidir": decidir,
        "revisar": revisar,
        "items": trabalhar + decidir,
        "totals": asdict(result.totals),
        "empty_message": result.empty_message,
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
        "action": action_for("revisar"),
    }


def _blank(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value
