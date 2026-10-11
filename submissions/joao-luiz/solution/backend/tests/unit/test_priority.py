"""Unit tests for C5: priority = value × chance (CHANCE-06, CHANCE-07, CHANCE-09, CHANCE-10)."""

import pytest

from app.scoring.priority import priority


def test_chance_06_priority_is_value_times_chance() -> None:
    assert priority(1000, 0.47) == 470
    assert priority(1000, 0.5) == 500
    assert priority(100, 1.0) == 100


def test_chance_07_past_wall_priority_is_zero() -> None:
    assert priority(26768, 0.0) == 0
    cheap_live = priority(55, 0.4)
    expensive_dead = priority(26768, 0.0)
    assert cheap_live > expensive_dead


def test_chance_09_no_probability_model_term() -> None:
    assert list(priority.__code__.co_varnames) == ["value", "chance"]
    with pytest.raises(TypeError):
        priority(1000, 0.47, 0.6)  # type: ignore[call-arg]


def test_chance_10_urgency_is_not_in_the_function() -> None:
    assert "urgency" not in priority.__code__.co_varnames
    assert "urgency" not in (priority.__doc__ or "").lower()
