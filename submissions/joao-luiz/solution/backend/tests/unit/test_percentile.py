"""Unit tests for T11: SCORE percentile of the current view (LEAD-09, LEAD-23)."""

from app.views.percentile import percentile_scores


def test_lead_09_single_deal_scores_100() -> None:
    assert percentile_scores([250]) == [100]


def test_lead_09_score_counts_priorities_at_or_below() -> None:
    assert percentile_scores([1, 2, 3, 4]) == [25, 50, 75, 100]
    assert all(0 <= score <= 100 for score in percentile_scores([1, 2, 3, 4]))


def test_lead_09_ties_share_the_same_percentile() -> None:
    assert percentile_scores([1, 2, 2, 4]) == [25, 75, 75, 100]


def test_lead_23_score_changes_when_the_view_changes() -> None:
    assert percentile_scores([10]) == [100]
    assert percentile_scores([10, 20]) == [50, 100]
    assert percentile_scores([5, 10]) == [50, 100]
