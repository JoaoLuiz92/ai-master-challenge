"""Integration: assign does not write the CSVs or an overlay (REPA-14, REPA-17)."""

from fastapi.testclient import TestClient

from app.handoffs.service import assign, eligible_candidates
from app.main import create_app
from app.settings import get_settings
from app.views.filter import split_view

SOURCE_CSVS = (
    "accounts.csv",
    "products.csv",
    "sales_teams.csv",
    "sales_pipeline.csv",
)


def test_repa_14_assign_leaves_source_csv_bytes_and_adds_no_overlay() -> None:
    data_dir = get_settings().data_dir
    before = {path.name: path.read_bytes() for path in data_dir.iterdir() if path.is_file()}

    with TestClient(create_app()) as client:
        deals = client.app.state.deals
        deal = split_view(deals).workable[0]
        team = {
            str(row.sales_agent): (
                None if row.manager is None else str(row.manager),
                None if row.regional_office is None else str(row.regional_office),
            )
            for row in client.app.state.raw_dataset.sales_teams.itertuples(index=False)
        }
        colleague = eligible_candidates(
            deals, deal.opportunity_id, team_by_agent=team
        )[0]
        result = assign(deals, deal.opportunity_id, colleague, team)

    after = {path.name: path.read_bytes() for path in data_dir.iterdir() if path.is_file()}
    moved = next(item for item in result.deals if item.opportunity_id == deal.opportunity_id)

    assert result.ok is True
    assert moved.sales_agent == colleague
    assert moved.from_agent == deal.sales_agent
    assert len(result.deals) == len(deals)
    assert after.keys() == before.keys()
    assert "handoffs.jsonl" not in after
    for name in SOURCE_CSVS:
        assert after[name] == before[name]
