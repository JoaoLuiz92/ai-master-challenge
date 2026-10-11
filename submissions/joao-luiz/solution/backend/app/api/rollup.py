"""Manager rollup for the filtered view. Each request recomputes the cut."""

from dataclasses import asdict

from fastapi import APIRouter, Request

from app.ingestion.repository import Deal
from app.views.query import ViewFilter
from app.views.rollup import build_rollup

router = APIRouter()


@router.get("/api/rollup")
def get_rollup(
    request: Request,
    manager: str | None = None,
    office: str | None = None,
) -> dict:
    selected = ViewFilter(manager=_blank(manager), office=_blank(office))
    deals: tuple[Deal, ...] = request.app.state.deals
    rows = build_rollup(deals, selected)
    return {
        "rows": [asdict(row) for row in rows],
        "parked_value": sum(row.decidir_value for row in rows),
    }


def _blank(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value
