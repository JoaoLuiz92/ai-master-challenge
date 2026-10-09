"""Unit tests for T5: deal age against frozen TODAY (LEAD-08)."""

from datetime import date

from app.constants import TODAY
from app.scoring.age import age_days


def test_lead_08_valid_engage_date_is_days_before_frozen_today() -> None:
    assert TODAY == date(2017, 12, 31)
    assert age_days(date(2017, 12, 27)) == 4


def test_lead_08_missing_engage_date_returns_none() -> None:
    assert age_days(None) is None


def test_lead_08_engage_date_on_today_is_zero_days() -> None:
    assert age_days(date(2017, 12, 31)) == 0
