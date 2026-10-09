"""Esfriando badge. Age above 106 days flags the deal and never drops it."""

from app.constants import WON_P90


def cooling(age_days: int | None) -> bool:
    """True only when age is strictly greater than 106 days."""
    return age_days is not None and age_days > WON_P90


def mark_cooling(
    deals: tuple[tuple[str, int | None], ...],
) -> tuple[tuple[str, int | None, bool], ...]:
    """Attach the badge. Every deal is returned; cooling is not a filter."""
    return tuple((deal_id, age_days, cooling(age_days)) for deal_id, age_days in deals)
