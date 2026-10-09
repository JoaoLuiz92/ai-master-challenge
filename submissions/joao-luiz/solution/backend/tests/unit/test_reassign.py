"""Unit tests for T1: in-memory reassignment (REPA-03, REPA-04, REPA-06, REPA-16)."""

from datetime import date

from app.ingestion.repository import Deal, reassign_deal


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


def test_repa_03_reassign_keeps_the_same_deal() -> None:
    origin = _deal()
    other = _deal(opportunity_id="opp-2", sales_agent="Luis", account="Beta")
    result = reassign_deal(
        (origin, other),
        "opp-1",
        to_agent="Bruno",
        from_agent="Ana",
        manager="Otto",
        office="East",
    )

    moved = next(deal for deal in result if deal.opportunity_id == "opp-1")
    untouched = next(deal for deal in result if deal.opportunity_id == "opp-2")

    assert moved.opportunity_id == "opp-1"
    assert moved.product == "GTK 500"
    assert moved.account == "Acme"
    assert moved.value == 26768
    assert moved.engage_date == date(2017, 6, 1)
    assert moved.close_date is None
    assert moved.deal_stage == "Engaging"
    assert moved.close_value is None
    assert moved.confidence is None
    assert moved.sales_agent == "Bruno"
    assert moved.from_agent == "Ana"
    assert untouched.sales_agent == "Luis"
    assert untouched.account == "Beta"
    assert untouched.from_agent is None


def test_repa_04_reassign_sets_manager_and_office_from_the_colleague() -> None:
    result = reassign_deal(
        (_deal(),),
        "opp-1",
        to_agent="Bruno",
        from_agent="Ana",
        manager="Otto",
        office="East",
    )

    deal = result[0]
    assert deal.manager == "Otto"
    assert deal.regional_office == "East"
    assert deal.sales_agent == "Bruno"


def test_repa_06_reassign_keeps_the_deal_count() -> None:
    deals = (
        _deal(),
        _deal(opportunity_id="opp-2", sales_agent="Luis"),
    )
    result = reassign_deal(
        deals,
        "opp-1",
        to_agent="Bruno",
        from_agent="Ana",
        manager="Otto",
        office="East",
    )

    assert len(result) == len(deals) == 2
    assert [deal.opportunity_id for deal in result] == ["opp-1", "opp-2"]


def test_unknown_opportunity_returns_the_same_tuple() -> None:
    deals = (_deal(), _deal(opportunity_id="opp-2"))
    result = reassign_deal(
        deals,
        "missing",
        to_agent="Bruno",
        from_agent="Ana",
        manager="Otto",
        office="East",
    )

    assert result is deals
    assert result[0].sales_agent == "Ana"
    assert result[0].from_agent is None


def test_repa_16_second_reassign_of_the_same_id_stays_one_deal() -> None:
    deals = (
        _deal(),
        _deal(opportunity_id="opp-2", sales_agent="Luis"),
    )
    once = reassign_deal(
        deals,
        "opp-1",
        to_agent="Bruno",
        from_agent="Ana",
        manager="Otto",
        office="East",
    )
    twice = reassign_deal(
        once,
        "opp-1",
        to_agent="Carla",
        from_agent="Bruno",
        manager="Rita",
        office="East",
    )

    matches = [deal for deal in twice if deal.opportunity_id == "opp-1"]
    assert len(matches) == 1
    assert len(twice) == 2
    assert matches[0].sales_agent == "Carla"
    assert matches[0].from_agent == "Bruno"
    assert matches[0].manager == "Rita"
    assert matches[0].product == "GTK 500"
    assert matches[0].account == "Acme"
    assert matches[0].value == 26768
    assert matches[0].engage_date == date(2017, 6, 1)
