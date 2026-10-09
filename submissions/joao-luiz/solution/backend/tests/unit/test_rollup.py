"""Unit tests for T15: manager rollup (LEAD-26, LEAD-27, LEAD-28)."""

from datetime import timedelta

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.views.query import ViewFilter
from app.views.rollup import build_rollup


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
        "value": 100,
        "confidence": None,
        "manager": "Mia",
        "regional_office": "East",
    }
    fields.update(overrides)
    return Deal(**fields)  # type: ignore[arg-type]


def _repo() -> tuple[Deal, ...]:
    return (
        _deal(opportunity_id="ana-hot", sales_agent="Ana", value=100),
        _deal(
            opportunity_id="ana-old",
            sales_agent="Ana",
            value=1000,
            engage_date=TODAY - timedelta(days=212),
        ),
        _deal(
            opportunity_id="bruno",
            sales_agent="Bruno",
            value=50,
            manager="Leo",
            regional_office="West",
        ),
    )


def test_lead_26_rollup_counts_value_and_cooling_per_agent() -> None:
    rows = {row.sales_agent: row for row in build_rollup(_repo())}
    ana = rows["Ana"]
    assert ana.queued_count == 2
    assert ana.expected_value_sum == 1100
    assert ana.cooling_count == 1
    bruno = rows["Bruno"]
    assert bruno.queued_count == 1
    assert bruno.expected_value_sum == 50
    assert bruno.cooling_count == 0


def test_lead_27_good_deal_cooling_is_focar_and_esfriando() -> None:
    rows = {row.sales_agent: row for row in build_rollup(_repo(), ViewFilter(agent="Ana"))}
    assert rows["Ana"].good_deals_cooling == 1
    assert "Bruno" not in rows


def test_lead_28_filter_recomputes_the_rollup() -> None:
    ana_only = build_rollup(_repo(), ViewFilter(agent="Ana"))
    assert ana_only[0].good_deals_cooling == 1

    both = {row.sales_agent: row for row in build_rollup(_repo(), ViewFilter(office="East"))}
    assert set(both) == {"Ana"}
    assert both["Ana"].queued_count == 2

    west = build_rollup(_repo(), ViewFilter(office="West"))
    assert [row.sales_agent for row in west] == ["Bruno"]
    assert west[0].good_deals_cooling == 0
