"""Survival chance by age band. Censored deals count as non-Won."""

from __future__ import annotations

from dataclasses import dataclass

from app.scoring.cohort import CohortEntry


@dataclass(frozen=True)
class BandChance:
    min_age: int
    max_age: int
    chance: float


def survival_table(
    cohort: tuple[CohortEntry, ...],
    bands: tuple[tuple[int, int], ...],
) -> tuple[BandChance, ...]:
    """Chance per band = Won ÷ deals whose age falls in the band.

    Lost and still-open (censored) stay in the denominator. A band with no
    Won, or no deals at all, is 0.
    """
    return tuple(_chance_in_band(cohort, min_age, max_age) for min_age, max_age in bands)


def _chance_in_band(
    cohort: tuple[CohortEntry, ...],
    min_age: int,
    max_age: int,
) -> BandChance:
    reached = [entry for entry in cohort if min_age <= entry.age_days <= max_age]
    if not reached:
        return BandChance(min_age=min_age, max_age=max_age, chance=0.0)
    won = sum(1 for entry in reached if entry.outcome == "won")
    return BandChance(min_age=min_age, max_age=max_age, chance=won / len(reached))
