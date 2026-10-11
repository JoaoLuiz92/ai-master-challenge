"""CSV of the current filtered queue. Same deals and order as GET /api/queue."""

import csv
import io

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.ingestion.repository import Deal
from app.views.query import QueueItem, ViewFilter, build_view

router = APIRouter()

DISPLAYED_COLUMNS = (
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
    """The download is the workable queue of this filter, not a second ranking."""
    selected = ViewFilter(
        agent=_blank(agent),
        manager=_blank(manager),
        office=_blank(office),
    )
    deals: tuple[Deal, ...] = request.app.state.deals
    view = build_view(deals, selected)
    return Response(content=_csv(view.trabalhar + view.decidir), media_type="text/csv")


def _csv(items: tuple[QueueItem, ...]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(DISPLAYED_COLUMNS)
    for item in items:
        writer.writerow([getattr(item, column) for column in DISPLAYED_COLUMNS])
    return buffer.getvalue()


def _blank(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value
