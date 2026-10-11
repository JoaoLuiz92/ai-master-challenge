"""Integration tests for C9: backtest without leakage (CHANCE-20..24)."""

from datetime import date, timedelta

from app.analysis.backtest import DEFAULT_CUTOFFS, run_backtest, snapshot_at
from app.ingestion.loader import load_dataset
from app.ingestion.quality import normalize
from app.ingestion.repository import Deal, build_deals
from app.settings import get_settings


def _repo() -> tuple[Deal, ...]:
    return build_deals(normalize(load_dataset(get_settings().data_dir))[0])


def test_chance_20_snapshot_hides_closes_after_the_cutoff() -> None:
    cutoff = date(2017, 9, 30)
    repo = _repo()
    future_closed = [
        deal
        for deal in repo
        if deal.close_date is not None and deal.close_date > cutoff and deal.engage_date
        and deal.engage_date <= cutoff
    ]
    assert future_closed
    snap = snapshot_at(repo, cutoff)
    by_id = {deal.opportunity_id: deal for deal in snap}
    for deal in future_closed[:20]:
        seen = by_id[deal.opportunity_id]
        assert seen.close_date is None
        assert seen.close_value is None
        assert seen.deal_stage == "Engaging"
    assert all(
        deal.close_date is None or deal.close_date <= cutoff for deal in snap
    )
    assert all(
        deal.engage_date is None or deal.engage_date <= cutoff for deal in snap
    )


def test_chance_21_reports_three_rankings_on_at_least_three_cutoffs() -> None:
    report = run_backtest(_repo())
    assert len(report.cutoffs) >= 3
    assert tuple(row.cutoff for row in report.cutoffs) == DEFAULT_CUTOFFS
    for row in report.cutoffs:
        assert row.nova >= 0
        assert row.preco >= 0
        assert row.aleatorio >= 0


def test_chance_22_emits_new_vs_price_with_dispersion() -> None:
    report = run_backtest(_repo())
    assert isinstance(report.nova_vs_preco_delta, float)
    assert isinstance(report.dispersion, float)
    assert report.dispersion >= 0
    assert isinstance(report.adopted, bool)
    assert report.adopted is (report.nova_vs_preco_delta > 0)


def test_chance_20_ranking_input_has_no_field_after_cutoff() -> None:
    cutoff = date(2017, 8, 31)
    snap = snapshot_at(_repo(), cutoff)
    later = cutoff + timedelta(days=1)
    for deal in snap:
        if deal.close_date is not None:
            assert deal.close_date <= cutoff
        if deal.engage_date is not None:
            assert deal.engage_date <= cutoff
        assert deal.close_date != later
