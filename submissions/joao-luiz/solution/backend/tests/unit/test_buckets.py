"""Unit tests for C6: Trabalhar / Decidir / Revisar (CHANCE-11, CHANCE-12, CHANCE-13, CHANCE-14)."""

from datetime import timedelta

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.views.buckets import bucketize


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
        _deal(opportunity_id="work", value=100, engage_date=TODAY - timedelta(days=10)),
        _deal(opportunity_id="work-young", value=50, engage_date=TODAY - timedelta(days=2)),
        _deal(opportunity_id="decide-hi", value=500, engage_date=TODAY - timedelta(days=20)),
        _deal(opportunity_id="decide-lo", value=80, engage_date=TODAY - timedelta(days=15)),
        _deal(opportunity_id="no-account", account=None),
        _deal(
            opportunity_id="pros",
            deal_stage="Prospecting",
            account=None,
            engage_date=None,
        ),
        _deal(opportunity_id="won", deal_stage="Won", engage_date=TODAY - timedelta(days=3)),
        _deal(opportunity_id="bruno", sales_agent="Bruno", engage_date=TODAY - timedelta(days=20)),
    )


def test_chance_11_past_wall_engaging_goes_to_decidir() -> None:
    buckets = bucketize(_repo(), wall=10, agent="Ana")
    work_ids = [deal.opportunity_id for deal in buckets.trabalhar.deals]
    decide_ids = [deal.opportunity_id for deal in buckets.decidir.deals]
    assert "work" in work_ids
    assert "work-young" in work_ids
    assert "decide-hi" in decide_ids
    assert "decide-lo" in decide_ids
    assert "work" not in decide_ids
    assert "decide-hi" not in work_ids


def test_chance_12_decidir_is_ordered_by_price_desc() -> None:
    buckets = bucketize(_repo(), wall=10, agent="Ana")
    assert [deal.opportunity_id for deal in buckets.decidir.deals] == [
        "decide-hi",
        "decide-lo",
    ]
    assert [deal.value for deal in buckets.decidir.deals] == [500, 80]


def test_chance_13_revisar_keeps_bad_data_and_prospecting() -> None:
    buckets = bucketize(_repo(), wall=10, agent="Ana")
    review_ids = {deal.opportunity_id for deal in buckets.revisar.deals}
    assert review_ids == {"no-account", "pros"}
    all_ids = (
        {deal.opportunity_id for deal in buckets.trabalhar.deals}
        | {deal.opportunity_id for deal in buckets.decidir.deals}
        | review_ids
    )
    assert all_ids.isdisjoint({"won", "bruno"})


def test_chance_14_each_bucket_has_count_and_value() -> None:
    buckets = bucketize(_repo(), wall=10, agent="Ana")
    assert buckets.trabalhar.count == 2
    assert buckets.trabalhar.value_sum == 150
    assert buckets.decidir.count == 2
    assert buckets.decidir.value_sum == 580
    assert buckets.revisar.count == 2
    assert buckets.trabalhar.count + buckets.decidir.count + buckets.revisar.count == 6
