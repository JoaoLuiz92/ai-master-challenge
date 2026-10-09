"""Unit tests for T10: workable queue vs Revisar (LEAD-16, LEAD-17, LEAD-18, LEAD-24)."""

from datetime import date

from app.ingestion.repository import Deal
from app.views.filter import split_view


def _deal(**overrides: object) -> Deal:
    fields: dict[str, object] = {
        "opportunity_id": "opp-1",
        "sales_agent": "Ana",
        "product": "GTK 500",
        "account": "Acme",
        "deal_stage": "Engaging",
        "engage_date": date(2017, 12, 1),
        "close_date": None,
        "close_value": None,
        "value": 26768,
        "confidence": None,
        "manager": "Mia",
        "regional_office": "East",
    }
    fields.update(overrides)
    return Deal(**fields)  # type: ignore[arg-type]


def test_lead_16_engaging_with_account_and_date_is_workable() -> None:
    deal = _deal()
    split = split_view((deal,))
    assert split.workable == (deal,)
    assert split.revisar == ()


def test_lead_16_missing_account_goes_to_revisar() -> None:
    deal = _deal(account=None)
    split = split_view((deal,))
    assert split.workable == ()
    assert split.revisar == (deal,)


def test_lead_17_missing_engage_date_goes_to_revisar() -> None:
    deal = _deal(engage_date=None)
    split = split_view((deal,))
    assert split.workable == ()
    assert split.revisar == (deal,)


def test_lead_18_closed_and_prospecting_stay_out_of_the_workable_queue() -> None:
    won = _deal(opportunity_id="won", deal_stage="Won")
    lost = _deal(opportunity_id="lost", deal_stage="Lost")
    prospecting = _deal(
        opportunity_id="pros", deal_stage="Prospecting", engage_date=None
    )
    split = split_view((won, lost, prospecting))
    assert split.workable == ()
    assert won not in split.revisar
    assert lost not in split.revisar
    assert split.revisar == (prospecting,)


def test_lead_24_filters_by_agent_manager_and_office() -> None:
    mine = _deal(opportunity_id="mine", sales_agent="Ana", manager="Mia", regional_office="East")
    other_agent = _deal(
        opportunity_id="other",
        sales_agent="Bruno",
        manager="Leo",
        regional_office="West",
    )
    other_manager = _deal(opportunity_id="mgr", sales_agent="Ana", manager="Leo")
    other_office = _deal(
        opportunity_id="off", sales_agent="Ana", manager="Mia", regional_office="West"
    )
    revisar_mine = _deal(opportunity_id="rev-mine", account=None)
    revisar_other = _deal(
        opportunity_id="rev",
        sales_agent="Bruno",
        manager="Leo",
        regional_office="West",
        account=None,
    )
    deals = (mine, other_agent, other_manager, other_office, revisar_mine, revisar_other)

    by_agent = split_view(deals, agent="Ana")
    assert by_agent.workable == (mine, other_manager, other_office)
    assert by_agent.revisar == (revisar_mine,)

    by_manager = split_view(deals, manager="Mia")
    assert by_manager.workable == (mine, other_office)
    assert by_manager.revisar == (revisar_mine,)

    by_office = split_view(deals, office="East")
    assert by_office.workable == (mine, other_manager)
    assert by_office.revisar == (revisar_mine,)

    combined = split_view(deals, agent="Ana", manager="Mia", office="East")
    assert combined.workable == (mine,)
    assert combined.revisar == (revisar_mine,)
