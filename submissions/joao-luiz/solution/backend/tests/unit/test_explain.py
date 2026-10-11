"""Unit tests for T13: Portuguese reason and action (LEAD-05)."""

from app.views.explain import action_for, chance_sentence, explain, wall_sentence


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


def test_chance_16_chance_sentence_uses_the_computed_percent() -> None:
    assert chance_sentence(0.47) == "47% dos deals desta idade fecharam."
    assert chance_sentence(0.2) == "20% dos deals desta idade fecharam."


def test_chance_17_wall_sentence_uses_the_computed_numbers() -> None:
    text = wall_sentence(77, 3)
    assert text == "Nenhum deal da base fechou depois de 77 dias; 3 abertos já passaram disso."
    assert "138" not in text
    other = wall_sentence(12, 9)
    assert "12" in other and "9" in other


def test_chance_18_action_matches_the_bucket() -> None:
    assert action_for("trabalhar") == "Avançar proposta"
    assert action_for("decidir") == "Requalificar ou encerrar"
    assert action_for("revisar") == "Qualificar conta/dados"
