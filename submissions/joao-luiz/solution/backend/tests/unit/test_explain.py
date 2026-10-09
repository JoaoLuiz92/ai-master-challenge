"""Unit tests for T13: Portuguese reason and action (LEAD-05)."""

from app.views.explain import explain


def test_lead_05_within_cycle_reason_and_action() -> None:
    text = explain("GTX Pro", 4821, 40)
    assert text.reason == "GTX Pro · US$ 4.821 · 40 dias no funil · dentro do ciclo"
    assert text.action == "Avançar proposta"


def test_lead_05_day_106_is_still_inside_the_cycle() -> None:
    text = explain("GTX Pro", 4821, 106)
    assert text.reason == "GTX Pro · US$ 4.821 · 106 dias no funil · dentro do ciclo"
    assert text.action == "Avançar proposta"


def test_lead_05_cooling_reason_and_action() -> None:
    text = explain("GTX Pro", 4821, 107)
    assert text.reason == "GTX Pro · US$ 4.821 · 107 dias no funil · esfriando"
    assert text.action == "Reengajar antes de esfriar"


def test_lead_05_revisar_action() -> None:
    text = explain("GTK 500", 26768, None, revisar=True)
    assert text.action == "Qualificar conta/dados"
