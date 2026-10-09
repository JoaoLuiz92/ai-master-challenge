"""Unit tests for T12: Focar is the top 20% of the view (LEAD-21)."""

from app.views.estado import assign_estado


def test_lead_21_single_deal_is_focar() -> None:
    assert assign_estado([10]) == ["Focar"]


def test_lead_21_five_deals_keep_the_top_one() -> None:
    labels = assign_estado([10, 50, 30, 20, 40])
    assert labels == ["Acompanhar", "Focar", "Acompanhar", "Acompanhar", "Acompanhar"]
    assert labels.count("Focar") == 1


def test_lead_21_six_deals_keep_the_top_two() -> None:
    labels = assign_estado([10, 60, 30, 20, 40, 50])
    assert labels.count("Focar") == 2
    assert labels[1] == "Focar"
    assert labels[5] == "Focar"
    assert labels.count("Acompanhar") == 4
