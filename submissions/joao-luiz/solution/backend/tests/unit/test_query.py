"""Unit tests for T14: ordered workable queue (LEAD-01, LEAD-02, LEAD-03, LEAD-04)."""

from datetime import date, timedelta

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.views.query import EMPTY_VIEW_MESSAGE, ViewFilter, build_queue


def _deal(**overrides: object) -> Deal:
    fields: dict[str, object] = {
        "opportunity_id": "opp",
        "sales_agent": "Ana",
        "product": "GTX Pro",
        "account": "Acme",
        "deal_stage": "Engaging",
        "engage_date": TODAY - timedelta(days=57),
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
        _deal(opportunity_id="low", value=100),
        _deal(opportunity_id="high", value=200),
        _deal(
            opportunity_id="old",
            value=100,
            engage_date=TODAY - timedelta(days=212),
        ),
        _deal(opportunity_id="won", deal_stage="Won", engage_date=date(2017, 6, 1)),
        _deal(opportunity_id="lost", deal_stage="Lost", product="MG Special", value=55),
        _deal(
            opportunity_id="pros",
            deal_stage="Prospecting",
            account=None,
            engage_date=None,
        ),
        _deal(opportunity_id="no-account", account=None),
        _deal(opportunity_id="bruno", sales_agent="Bruno", value=9999),
    )


def test_lead_03_highest_priority_is_first() -> None:
    view = build_queue(_repo(), ViewFilter(agent="Ana"))
    assert [item.opportunity_id for item in view.items] == ["high", "low", "old"]
    assert view.items[0].score == 100
    assert view.items[0].estado == "Focar"
    assert view.empty_message is None


def test_lead_02_closed_and_prospecting_stay_out() -> None:
    ids = {item.opportunity_id for item in build_queue(_repo(), ViewFilter(agent="Ana")).items}
    assert ids.isdisjoint({"won", "lost", "pros", "no-account"})


def test_lead_04_item_exposes_the_queue_fields() -> None:
    item = build_queue(_repo(), ViewFilter(agent="Ana")).items[0]
    assert item.product == "GTX Pro"
    assert item.account == "Acme"
    assert item.value == 200
    assert item.deal_stage == "Engaging"
    assert item.age_days == 57
    assert item.score == 100
    assert item.estado == "Focar"
    assert item.confidence == "Média"
    assert item.reason == "GTX Pro · US$ 200 · 57 dias no funil · dentro do ciclo"
    assert item.action == "Avançar proposta"
    assert item.cooling is False
    old = build_queue(_repo(), ViewFilter(agent="Ana")).items[2]
    assert old.opportunity_id == "old"
    assert old.age_days == 212
    assert old.cooling is True
    assert old.action == "Reengajar antes de esfriar"


def test_lead_01_empty_view_returns_a_message() -> None:
    view = build_queue(_repo(), ViewFilter(agent="Ninguem"))
    assert view.items == ()
    assert view.empty_message == EMPTY_VIEW_MESSAGE
    assert view.empty_message == "sem deals nesta visão"
