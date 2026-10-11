"""Unit tests for C7: view builder, percentile on Trabalhar (CHANCE-08, CHANCE-15)."""

from datetime import date, timedelta

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.views.query import ViewFilter, build_view


def _deal(**overrides: object) -> Deal:
    fields: dict[str, object] = {
        "opportunity_id": "opp",
        "sales_agent": "Ana",
        "product": "GTX Pro",
        "account": "Acme",
        "deal_stage": "Engaging",
        "engage_date": TODAY - timedelta(days=5),
        "close_date": None,
        "close_value": None,
        "value": 200,
        "confidence": None,
        "manager": "Mia",
        "regional_office": "East",
    }
    fields.update(overrides)
    return Deal(**fields)  # type: ignore[arg-type]


def _repo() -> tuple[Deal, ...]:
    return (
        _deal(
            opportunity_id="won",
            deal_stage="Won",
            engage_date=date(2017, 1, 1),
            close_date=date(2017, 1, 11),
        ),
        _deal(opportunity_id="low", value=100, engage_date=TODAY - timedelta(days=5)),
        _deal(opportunity_id="high", value=400, engage_date=TODAY - timedelta(days=5)),
        _deal(
            opportunity_id="parked",
            value=9999,
            engage_date=TODAY - timedelta(days=40),
        ),
        _deal(opportunity_id="no-account", account=None),
    )


def test_chance_08_percentile_is_only_over_trabalhar() -> None:
    view = build_view(_repo(), ViewFilter(agent="Ana"))
    work_ids = [item.opportunity_id for item in view.trabalhar]
    decide_ids = [item.opportunity_id for item in view.decidir]
    assert work_ids == ["high", "low"]
    assert "parked" in decide_ids
    assert "parked" not in work_ids
    assert view.trabalhar[0].score == 100
    assert view.decidir[0].score == 0
    assert view.trabalhar[0].value * view.trabalhar[0].chance >= (
        view.trabalhar[1].value * view.trabalhar[1].chance
    )


def test_chance_15_trabalhar_orders_by_score_desc() -> None:
    view = build_view(_repo(), ViewFilter(agent="Ana"))
    scores = [item.score for item in view.trabalhar]
    assert scores == sorted(scores, reverse=True)
    assert view.totals.trabalhar_count == 2
    assert view.totals.decidir_count == 1
    assert view.totals.revisar_count == 1
    assert {deal.opportunity_id for deal in view.revisar} == {"no-account"}


def test_chance_15_empty_trabalhar_keeps_decidir() -> None:
    repo = (
        _deal(
            opportunity_id="won",
            deal_stage="Won",
            engage_date=date(2017, 1, 1),
            close_date=date(2017, 1, 11),
        ),
        _deal(
            opportunity_id="parked",
            value=500,
            engage_date=TODAY - timedelta(days=40),
        ),
    )
    view = build_view(repo, ViewFilter(agent="Ana"))
    assert view.trabalhar == ()
    assert view.empty_message == "sem deals nesta visão"
    assert [item.opportunity_id for item in view.decidir] == ["parked"]
