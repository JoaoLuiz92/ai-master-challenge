"""Integration: from_agent is session-only; restart restores the CSV owner (REPA-15, REPA-18, REPA-19)."""

from fastapi.testclient import TestClient

from app.handoffs.service import eligible_candidates
from app.ingestion.repository import Deal
from app.main import create_app
from app.views.filter import split_view


def _team(client: TestClient) -> dict[str, tuple[str | None, str | None]]:
    from app.api.handoff import team_by_agent

    return team_by_agent(client)


def _pair(client: TestClient) -> tuple[Deal, str]:
    deals: tuple[Deal, ...] = client.app.state.deals
    team = _team(client)
    for deal in split_view(deals).workable:
        names = eligible_candidates(deals, deal.opportunity_id, team_by_agent=team)
        if names:
            return deal, names[0]
    raise AssertionError("no same-office colleague for a workable deal")


def _queue_item(client: TestClient, agent: str, opportunity_id: str) -> dict:
    body = client.get("/api/queue", params={"view": "mine", "agent": agent}).json()
    return next(item for item in body["items"] if item["opportunity_id"] == opportunity_id)


def test_repa_15_restart_restores_the_csv_owner_and_drops_from_agent() -> None:
    with TestClient(create_app()) as client:
        deal, colleague = _pair(client)
        before = _queue_item(client, deal.sales_agent, deal.opportunity_id)
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": deal.opportunity_id, "to_agent": colleague},
        )
        moved = _queue_item(client, colleague, deal.opportunity_id)

    assert before["from_agent"] is None
    assert response.status_code == 200
    assert moved["from_agent"] == deal.sales_agent
    assert moved["opportunity_id"] == deal.opportunity_id

    with TestClient(create_app()) as restarted:
        owner = next(
            item
            for item in restarted.app.state.deals
            if item.opportunity_id == deal.opportunity_id
        )
        restored = _queue_item(restarted, deal.sales_agent, deal.opportunity_id)
        colleague_ids = {
            item["opportunity_id"]
            for item in restarted.get(
                "/api/queue", params={"view": "mine", "agent": colleague}
            ).json()["items"]
        }

    assert owner.sales_agent == deal.sales_agent
    assert owner.from_agent is None
    assert restored["from_agent"] is None
    assert deal.opportunity_id not in colleague_ids
