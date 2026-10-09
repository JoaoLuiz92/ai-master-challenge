"""Unit tests for T3: assign keeps one deal or refuses (REPA-02, REPA-05, REPA-10..13)."""

from datetime import date

from app.handoffs.service import assign
from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.scoring.priority import priority
from app.scoring.urgency import urgency
from app.views.percentile import percentile_scores
from app.views.query import ViewFilter, build_queue

TEAM = {
    "Ana": ("Mia", "East"),
    "Bruno": ("Otto", "East"),
    "Carla": ("Boss", "West"),
}


def _deal(**overrides: object) -> Deal:
    fields: dict[str, object] = {
        "opportunity_id": "opp-1",
        "sales_agent": "Ana",
        "product": "GTK 500",
        "account": "Acme",
        "deal_stage": "Engaging",
        "engage_date": date(2017, 6, 1),
        "close_date": None,
        "close_value": None,
        "value": 26768,
        "confidence": None,
        "manager": "Mia",
        "regional_office": "East",
    }
    fields.update(overrides)
    return Deal(**fields)  # type: ignore[arg-type]


def _refused(deals: tuple[Deal, ...], to_agent: str, message: str):
    result = assign(deals, "opp-1", to_agent, TEAM)
    assert result.ok is False
    assert result.message == message
    assert result.deals is deals
    assert result.deals[0].sales_agent == "Ana"
    return result


def test_repa_02_assign_moves_the_one_deal() -> None:
    other = _deal(opportunity_id="opp-2", sales_agent="Luis", account="Beta")
    deals = (_deal(), other)
    result = assign(deals, "opp-1", "Bruno", TEAM)

    assert result.ok is True
    assert result.message is None
    moved = result.deals[0]
    assert len(result.deals) == 2
    assert sum(item.opportunity_id == "opp-1" for item in result.deals) == 1
    assert moved.sales_agent == "Bruno"
    assert moved.from_agent == "Ana"
    assert moved.manager == "Otto"
    assert moved.regional_office == "East"
    assert moved.opportunity_id == "opp-1"
    assert moved.product == "GTK 500"
    assert moved.account == "Acme"
    assert moved.value == 26768
    assert moved.engage_date == date(2017, 6, 1)
    assert result.deals[1] is other


def test_repa_05_destination_score_is_the_view_percentile_and_age_stays() -> None:
    origin = _deal(value=1000, engage_date=date(2017, 12, 1))
    resident = _deal(
        opportunity_id="opp-2",
        sales_agent="Bruno",
        manager="Otto",
        value=50000,
        engage_date=date(2017, 6, 1),
    )
    before_age = age_days(origin.engage_date)
    result = assign((origin, resident), "opp-1", "Bruno", TEAM)
    moved = next(deal for deal in result.deals if deal.opportunity_id == "opp-1")

    assert moved.value == 1000
    assert age_days(moved.engage_date) == before_age

    queue = build_queue(result.deals, ViewFilter(agent="Bruno"))
    ranks = [
        priority(deal.value, urgency(age_days(deal.engage_date)) or 0)
        for deal in result.deals
        if deal.sales_agent == "Bruno"
    ]
    expected = {
        deal.opportunity_id: score
        for deal, score in zip(
            (item for item in result.deals if item.sales_agent == "Bruno"),
            percentile_scores(ranks),
            strict=True,
        )
    }
    listed = next(item for item in queue.items if item.opportunity_id == "opp-1")
    assert listed.score == expected["opp-1"]
    assert listed.value == 1000
    assert listed.age_days == before_age
    assert listed.account == "Acme"
    assert listed.product == "GTK 500"


def test_repa_10_unknown_agent_keeps_the_owner() -> None:
    _refused((_deal(),), "Ninguém", "Colega não encontrado")


def test_repa_11_current_owner_keeps_the_owner() -> None:
    _refused((_deal(),), "Ana", "Este negócio já está com essa pessoa")


def test_repa_12_other_office_keeps_the_owner() -> None:
    _refused((_deal(),), "Carla", "Colega de outro escritório")


def test_owner_without_office_is_refused_as_other_office() -> None:
    _refused(
        (_deal(regional_office=None),),
        "Bruno",
        "Colega de outro escritório",
    )


def test_repa_13_closed_prospecting_and_incomplete_are_refused() -> None:
    message = "Este negócio não está na fila trabalhável"
    cases = (
        _deal(deal_stage="Won"),
        _deal(deal_stage="Lost"),
        _deal(deal_stage="Prospecting"),
        _deal(account=None),
        _deal(engage_date=None),
    )
    for deal in cases:
        _refused((deal,), "Bruno", message)


def test_missing_deal_is_refused_and_the_tuple_stays() -> None:
    deals = (_deal(),)
    result = assign(deals, "missing", "Bruno", TEAM)
    assert result.ok is False
    assert result.message == "Este negócio não está na fila trabalhável"
    assert result.deals is deals


def test_repa_16_second_assign_to_the_same_colleague_stays_one_deal() -> None:
    once = assign((_deal(),), "opp-1", "Bruno", TEAM)
    twice = assign(once.deals, "opp-1", "Bruno", TEAM)

    assert twice.ok is False
    assert twice.message == "Este negócio já está com essa pessoa"
    assert len(twice.deals) == 1
    assert twice.deals[0].sales_agent == "Bruno"
    assert twice.deals[0].opportunity_id == "opp-1"
