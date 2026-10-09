"""Unit tests for T9: Esfriando badge without dropping deals (LEAD-19, LEAD-20)."""

from app.scoring.cooling import cooling, mark_cooling


def test_lead_19_age_106_is_not_cooling() -> None:
    assert cooling(106) is False


def test_lead_19_age_above_106_is_cooling() -> None:
    assert cooling(107) is True
    assert cooling(400) is True


def test_lead_20_cooling_flag_keeps_every_deal() -> None:
    deals = (("a", 0), ("b", 106), ("c", 107), ("d", 400))
    flagged = mark_cooling(deals)
    assert [(deal_id, age) for deal_id, age, _flag in flagged] == list(deals)
    assert [flag for _deal_id, _age, flag in flagged] == [False, False, True, True]
