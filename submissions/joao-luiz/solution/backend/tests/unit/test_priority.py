"""Unit tests for T7: priority = value × urgency (LEAD-06, LEAD-10)."""

import pytest

from app.scoring.priority import priority


def test_lead_06_priority_is_value_times_urgency() -> None:
    assert priority(1000, 1.0) == 1000
    assert priority(1000, 0.5) == 500
    assert priority(100, 0.35) == 35


def test_lead_06_higher_product_ranks_first() -> None:
    hot_cheap = priority(100, 1.0)
    cool_expensive = priority(1000, 0.35)
    assert cool_expensive > hot_cheap
    assert priority(500, 1.0) > priority(1000, 0.35)


def test_lead_10_probability_is_not_a_factor() -> None:
    assert list(priority.__code__.co_varnames) == ["value", "urgency"]
    with pytest.raises(TypeError):
        priority(1000, 1.0, 0.6)  # type: ignore[call-arg]
