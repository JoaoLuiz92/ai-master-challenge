"""Unit tests for T8: confidence = min(completude, suporte) (LEAD-22)."""

from app.scoring.confidence import confidence


def test_lead_22_missing_account_is_baixa() -> None:
    assessed = confidence(
        26768, has_account=False, has_engage_date=True, closed_count=200
    )
    assert assessed.level == "Baixa"


def test_lead_22_missing_engage_date_is_baixa() -> None:
    assessed = confidence(
        26768, has_account=True, has_engage_date=False, closed_count=200
    )
    assert assessed.level == "Baixa"


def test_lead_22_complete_deal_with_support_is_alta() -> None:
    assessed = confidence(
        1000, has_account=True, has_engage_date=True, closed_count=100
    )
    assert assessed.level == "Alta"
    assert assessed.value == 1000


def test_lead_22_gtk_500_low_support_lowers_confidence_not_value() -> None:
    # GTK 500: catalog sales_price 26768, 25 closed (Won + Lost).
    assessed = confidence(
        26768, has_account=True, has_engage_date=True, closed_count=25
    )
    assert assessed.level == "Média"
    assert assessed.value == 26768


def test_lead_22_support_just_below_threshold_is_media() -> None:
    assessed = confidence(
        500, has_account=True, has_engage_date=True, closed_count=99
    )
    assert assessed.level == "Média"
    assert assessed.value == 500
