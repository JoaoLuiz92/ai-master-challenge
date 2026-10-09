"""Unit tests for T6: urgency curve (LEAD-07)."""

import pytest

from app.scoring.urgency import urgency


def test_lead_07_day_zero_starts_the_ramp_at_half() -> None:
    assert urgency(0) == pytest.approx(0.5)


def test_lead_07_won_median_is_the_peak() -> None:
    assert urgency(57) == pytest.approx(1.0)


def test_lead_07_plateau_holds_through_won_p90() -> None:
    assert urgency(80) == pytest.approx(1.0)
    assert urgency(106) == pytest.approx(1.0)


def test_lead_07_decays_after_106_and_floors_at_212() -> None:
    assert urgency(107) < 1.0
    assert urgency(107) > 0.35
    # Halfway from 106d to 212d is halfway from 1.0 down to 0.35.
    assert urgency(159) == pytest.approx(0.675)
    assert urgency(212) == pytest.approx(0.35)
    assert urgency(10_000) == pytest.approx(0.35)
    assert urgency(10_000) != 0


def test_lead_07_missing_age_does_not_infer_urgency() -> None:
    assert urgency(None) is None
