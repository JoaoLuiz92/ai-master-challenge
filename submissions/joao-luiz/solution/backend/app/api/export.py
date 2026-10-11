"""CSV of the current filtered view. Same deals, queues and order as the UI."""

import csv
import io

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.views.explain import action_for, explain
from app.views.query import QueueItem, ViewFilter, build_view

router = APIRouter()

DISPLAYED_COLUMNS = (
    "fila",
    "product",
    "account",
    "value",
    "deal_stage",
    "age_days",
    "score",
    "estado",
    "confidence",
    "reason",
    "action",
)


@router.get("/api/export.csv")
def export_csv(
    request: Request,
    agent: str | None = None,
    manager: str | None = None,
    office: str | None = None,
) -> Response:
    """Download is Trabalhar, then Decidir, then Revisar — the order on screen."""
    selected = ViewFilter(
        agent=_blank(agent),
        manager=_blank(manager),
        office=_blank(office),
    )
    deals: tuple[Deal, ...] = request.app.state.deals
    view = build_view(deals, selected)
    rows = (
        [_queue_row(item, "Trabalhar") for item in view.trabalhar]
        + [_queue_row(item, "Decidir") for item in view.decidir]
        + [_review_row(deal) for deal in view.revisar]
    )
    return Response(content=_csv(rows), media_type="text/csv")


def _queue_row(item: QueueItem, fila: str) -> dict[str, object]:
    return {
        "fila": fila,
        "product": item.product,
        "account": item.account,
        "value": item.value,
        "deal_stage": item.deal_stage,
        "age_days": item.age_days,
        "score": item.score,
        "estado": item.estado,
        "confidence": item.confidence,
        "reason": item.reason,
        "action": item.action,
    }


def _review_row(deal: Deal) -> dict[str, object]:
    age = age_days(deal.engage_date)
    text = explain(deal.product, deal.value, age, revisar=True)
    return {
        "fila": "Revisar",
        "product": deal.product,
        "account": deal.account or "",
        "value": deal.value,
        "deal_stage": deal.deal_stage,
        "age_days": "" if age is None else age,
        "score": "",
        "estado": "Revisar",
        "confidence": "",
        "reason": text.reason,
        "action": action_for("revisar"),
    }


def _csv(rows: list[dict[str, object]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(DISPLAYED_COLUMNS)
    for row in rows:
        writer.writerow([row[column] for column in DISPLAYED_COLUMNS])
    return buffer.getvalue()


def _blank(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value
