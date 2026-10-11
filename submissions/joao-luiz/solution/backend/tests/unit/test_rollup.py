"""Unit tests for C11: rollup Trabalhar vs Decidir (CHANCE-25, CHANCE-26, CHANCE-27)."""

from datetime import date, timedelta

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
        "engage_date": TODAY - timedelta(days=5),
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
        _deal(
            opportunity_id="won",
            deal_stage="Won",
            engage_date=date(2017, 1, 1),
            close_date=date(2017, 1, 11),
        ),
        _deal(opportunity_id="ana-work", sales_agent="Ana", value=100),
        _deal(
            opportunity_id="ana-parked",
            sales_agent="Ana",
            value=1000,
            engage_date=TODAY - timedelta(days=40),
        ),
        _deal(
            opportunity_id="bruno-parked",
            sales_agent="Bruno",
            value=50,
            manager="Leo",
            regional_office="West",
            engage_date=TODAY - timedelta(days=40),
        ),
    )


def test_chance_25_rollup_splits_trabalhar_and_decidir() -> None:
    rows = {row.sales_agent: row for row in build_rollup(_repo())}
    ana = rows["Ana"]
    assert ana.trabalhar_count == 1
    assert ana.trabalhar_value == 100
    assert ana.decidir_count == 1
    assert ana.decidir_value == 1000
    assert ana.queued_count == 2
    assert ana.expected_value_sum == 1100
    bruno = rows["Bruno"]
    assert bruno.trabalhar_count == 0
    assert bruno.decidir_count == 1
    assert bruno.decidir_value == 50


def test_chance_26_parked_value_is_the_decidir_sum() -> None:
    rows = build_rollup(_repo())
    assert sum(row.decidir_value for row in rows) == 1050


def test_chance_27_filter_recomputes_both_rollups() -> None:
    east = {row.sales_agent: row for row in build_rollup(_repo(), ViewFilter(office="East"))}
    assert set(east) == {"Ana"}
    west = build_rollup(_repo(), ViewFilter(office="West"))
    assert [row.sales_agent for row in west] == ["Bruno"]
    assert west[0].decidir_value == 50
    ana_only = build_rollup(_repo(), ViewFilter(agent="Ana"))
    assert ana_only[0].trabalhar_count == 1
    assert "Bruno" not in {row.sales_agent for row in ana_only}
