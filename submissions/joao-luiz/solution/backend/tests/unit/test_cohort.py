"""Unit tests for C1: cohort of closed + censored deals (CHANCE-01, CHANCE-04)."""

from datetime import date, timedelta

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.scoring.cohort import build_cohort


def _deal(**overrides: object) -> Deal:
    fields: dict[str, object] = {
        "opportunity_id": "opp",
        "sales_agent": "Ana",
        "product": "GTX Pro",
        "account": "Acme",
        "deal_stage": "Engaging",
        "engage_date": TODAY - timedelta(days=40),
        "close_date": None,
        "close_value": None,
        "value": 200,
        "confidence": None,
        "manager": "Mia",
        "regional_office": "East",
    }
    fields.update(overrides)
    return Deal(**fields)  # type: ignore[arg-type]


def test_chance_04_today_anchor_is_2017_12_31() -> None:
    assert TODAY == date(2017, 12, 31)
    open_deal = _deal(engage_date=date(2017, 12, 1))
    [entry] = build_cohort((open_deal,))
    assert entry.age_days == 30
    assert entry.age_days == age_days(date(2017, 12, 1))


def test_chance_01_won_is_tagged_won_with_cycle_age() -> None:
    won = _deal(
        deal_stage="Won",
        engage_date=date(2017, 1, 1),
        close_date=date(2017, 1, 11),
    )
    [entry] = build_cohort((won,))
    assert entry.outcome == "won"
    assert entry.age_days == 10
    assert entry.age_days != age_days(date(2017, 1, 1))


def test_chance_01_still_open_is_tagged_censored_not_dropped() -> None:
    opened = _deal(deal_stage="Engaging", engage_date=date(2016, 11, 1))
    won = _deal(
        opportunity_id="won",
        deal_stage="Won",
        engage_date=date(2017, 3, 1),
        close_date=date(2017, 4, 10),
    )
    cohort = build_cohort((opened, won))
    assert len(cohort) == 2
    by_outcome = {entry.outcome: entry for entry in cohort}
    assert set(by_outcome) == {"censored", "won"}
    assert by_outcome["censored"].age_days == (TODAY - date(2016, 11, 1)).days
    assert by_outcome["won"].age_days == 40


def test_chance_01_missing_engage_date_is_out_of_the_cohort() -> None:
    cohort = build_cohort((_deal(engage_date=None, deal_stage="Prospecting"),))
    assert cohort == ()


def test_chance_01_lost_stays_in_the_cohort_as_lost() -> None:
    lost = _deal(
        deal_stage="Lost",
        engage_date=date(2017, 2, 1),
        close_date=date(2017, 2, 15),
    )
    [entry] = build_cohort((lost,))
    assert entry.outcome == "lost"
    assert entry.age_days == 14


def test_chance_04_open_age_follows_the_today_argument() -> None:
    opened = _deal(engage_date=date(2017, 6, 1))
    [entry] = build_cohort((opened,), today=date(2017, 6, 11))
    assert entry.outcome == "censored"
    assert entry.age_days == 10
