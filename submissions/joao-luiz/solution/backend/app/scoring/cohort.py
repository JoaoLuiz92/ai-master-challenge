"""Cohort of deals with age and outcome. Open deals are censored, not dropped."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from app.constants import TODAY
from app.ingestion.repository import Deal
from app.scoring.age import age_days

Outcome = Literal["won", "lost", "censored"]


@dataclass(frozen=True)
class CohortEntry:
    age_days: int
    outcome: Outcome


def build_cohort(
    repo: tuple[Deal, ...],
    today: date = TODAY,
) -> tuple[CohortEntry, ...]:
    """One entry per deal that has an age. Still-open deals stay as censored."""
    return tuple(
        CohortEntry(age_days=age, outcome=_outcome(deal))
        for deal in repo
        if (age := _cohort_age(deal, today)) is not None
    )


def _outcome(deal: Deal) -> Outcome:
    if deal.deal_stage == "Won":
        return "won"
    if deal.deal_stage == "Lost":
        return "lost"
    return "censored"


def _cohort_age(deal: Deal, today: date) -> int | None:
    if deal.engage_date is None:
        return None
    if deal.deal_stage in ("Won", "Lost") and deal.close_date is not None:
        return (deal.close_date - deal.engage_date).days
    if today == TODAY:
        return age_days(deal.engage_date)
    return (today - deal.engage_date).days
