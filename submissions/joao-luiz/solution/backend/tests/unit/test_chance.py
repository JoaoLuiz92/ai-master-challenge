"""Unit tests for C2: survival table with censoring (CHANCE-01, CHANCE-03)."""

from app.scoring.chance import survival_table
from app.scoring.cohort import CohortEntry
from app.settings import get_settings

_BANDS = ((0, 9), (10, 19), (20, 29))


def _entry(age_days: int, outcome: str) -> CohortEntry:
    return CohortEntry(age_days=age_days, outcome=outcome)  # type: ignore[arg-type]


def _hand_cohort() -> tuple[CohortEntry, ...]:
    return (
        *(_entry(5, "won") for _ in range(4)),
        *(_entry(5, "lost") for _ in range(6)),
        *(_entry(15, "won") for _ in range(5)),
        _entry(15, "lost"),
        *(_entry(25, "won") for _ in range(3)),
        *(_entry(25, "censored") for _ in range(12)),
    )


def _chances(cohort: tuple[CohortEntry, ...]) -> list[float]:
    return [row.chance for row in survival_table(cohort, _BANDS)]


def test_chance_01_table_matches_hand_count_with_censoring() -> None:
    table = survival_table(_hand_cohort(), _BANDS)
    by_band = {(row.min_age, row.max_age): row.chance for row in table}
    assert by_band[(0, 9)] == 4 / 10
    assert by_band[(10, 19)] == 5 / 6
    assert by_band[(20, 29)] == 3 / 15


def test_chance_01_censoring_changes_the_curve_and_stops_it_increasing() -> None:
    with_censoring = _chances(_hand_cohort())
    closed_only = tuple(e for e in _hand_cohort() if e.outcome != "censored")
    without_censoring = _chances(closed_only)
    assert with_censoring != without_censoring
    assert without_censoring == [4 / 10, 5 / 6, 1.0]
    assert without_censoring[0] < without_censoring[1] < without_censoring[2]


def test_chance_01_censored_curve_is_non_increasing_after_peak() -> None:
    values = _chances(_hand_cohort())
    peak = max(range(len(values)), key=values.__getitem__)
    after = values[peak:]
    assert after == sorted(after, reverse=True)


def test_chance_01_band_without_won_is_zero() -> None:
    cohort = (_entry(5, "lost"), _entry(5, "censored"))
    [row] = survival_table(cohort, ((0, 9),))
    assert row.chance == 0.0


def test_chance_01_empty_band_is_zero() -> None:
    cohort = (_entry(5, "won"),)
    table = survival_table(cohort, ((0, 9), (10, 19)))
    assert table[0].chance == 1.0
    assert table[1].chance == 0.0


def test_chance_03_bands_come_from_config_not_from_logic() -> None:
    bands = get_settings().chance_bands
    assert bands == ((0, 29), (30, 59), (60, 89), (90, 10_000))
    table = survival_table(_hand_cohort(), bands)
    assert [(row.min_age, row.max_age) for row in table] == list(bands)
    other = ((0, 100),)
    other_table = survival_table(_hand_cohort(), other)
    assert [(row.min_age, row.max_age) for row in other_table] == list(other)
    assert len(table) != len(other_table)
