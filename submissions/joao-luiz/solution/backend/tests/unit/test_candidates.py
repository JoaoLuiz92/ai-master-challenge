"""Unit tests for T2: eligible colleagues (REPA-01, REPA-12)."""

from datetime import date

from app.handoffs.service import eligible_candidates
from app.ingestion.repository import Deal


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


def test_repa_01_lists_same_office_agents_except_the_owner() -> None:
    deals = (
        _deal(),
        _deal(opportunity_id="opp-2", sales_agent="Bruno"),
        _deal(opportunity_id="opp-3", sales_agent="Ana"),
        _deal(opportunity_id="opp-4", sales_agent="Carla", regional_office="West"),
        _deal(opportunity_id="opp-5", sales_agent="Bruno"),
    )

    assert eligible_candidates(deals, "opp-1") == ("Bruno",)


def test_repa_12_other_offices_are_excluded() -> None:
    deals = (
        _deal(),
        _deal(opportunity_id="opp-2", sales_agent="Carla", regional_office="West"),
    )

    assert eligible_candidates(deals, "opp-1") == ()


def test_unknown_deal_returns_empty() -> None:
    assert eligible_candidates((_deal(),), "missing") == ()


def test_owner_without_office_returns_empty() -> None:
    deals = (
        _deal(regional_office=None),
        _deal(opportunity_id="opp-2", sales_agent="Bruno", regional_office="East"),
    )

    assert eligible_candidates(deals, "opp-1") == ()


def test_repa_01_empty_portfolio_colleague_is_listed_from_the_roster() -> None:
    deals = (_deal(),)
    team = {
        "Ana": ("Mia", "East"),
        "Otto": ("Mia", "East"),
        "Carla": ("Boss", "West"),
    }

    assert eligible_candidates(deals, "opp-1", team_by_agent=team) == ("Otto",)
