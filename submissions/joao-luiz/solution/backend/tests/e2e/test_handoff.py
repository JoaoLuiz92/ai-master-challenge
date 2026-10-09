"""E2E tests for T4: POST /api/handoff (REPA-02, REPA-03, REPA-04, REPA-10..13)."""

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


def _item(client: TestClient, agent: str, opportunity_id: str) -> dict:
    body = client.get("/api/queue", params={"view": "mine", "agent": agent}).json()
    return next(item for item in body["items"] if item["opportunity_id"] == opportunity_id)


def test_repa_02_post_moves_the_deal_between_queues() -> None:
    with TestClient(create_app()) as client:
        deal, colleague = _pair(client)
        before_count = len(client.app.state.deals)
        before = _item(client, deal.sales_agent, deal.opportunity_id)
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": deal.opportunity_id, "to_agent": colleague},
        )
        origin = client.get(
            "/api/queue", params={"view": "mine", "agent": deal.sales_agent}
        ).json()
        moved = _item(client, colleague, deal.opportunity_id)
        stored = next(
            item
            for item in client.app.state.deals
            if item.opportunity_id == deal.opportunity_id
        )
        colleague_manager, colleague_office = _team(client)[colleague]

    assert response.status_code == 200
    assert response.json() == {
        "opportunity_id": deal.opportunity_id,
        "sales_agent": colleague,
        "from_agent": deal.sales_agent,
    }
    assert deal.opportunity_id not in {item["opportunity_id"] for item in origin["items"]}
    assert moved["opportunity_id"] == before["opportunity_id"]
    assert moved["product"] == before["product"]
    assert moved["account"] == before["account"]
    assert moved["value"] == before["value"]
    assert moved["age_days"] == before["age_days"]
    assert stored.manager == colleague_manager
    assert stored.regional_office == colleague_office
    assert len(client.app.state.deals) == before_count
    assert sum(item.opportunity_id == deal.opportunity_id for item in client.app.state.deals) == 1


def test_repa_10_unknown_agent_is_404_and_keeps_the_owner() -> None:
    with TestClient(create_app()) as client:
        deal, _colleague = _pair(client)
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": deal.opportunity_id, "to_agent": "Ninguém"},
        )
        owner = next(
            item
            for item in client.app.state.deals
            if item.opportunity_id == deal.opportunity_id
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Colega não encontrado"
    assert owner.sales_agent == deal.sales_agent


def test_repa_11_same_owner_is_409_and_keeps_the_owner() -> None:
    with TestClient(create_app()) as client:
        deal, _colleague = _pair(client)
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": deal.opportunity_id, "to_agent": deal.sales_agent},
        )
        owner = next(
            item
            for item in client.app.state.deals
            if item.opportunity_id == deal.opportunity_id
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Este negócio já está com essa pessoa"
    assert owner.sales_agent == deal.sales_agent


def test_repa_12_other_office_is_422_and_keeps_the_owner() -> None:
    with TestClient(create_app()) as client:
        deal, _colleague = _pair(client)
        outsider = next(
            agent
            for agent, (_manager, office) in _team(client).items()
            if office != deal.regional_office
        )
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": deal.opportunity_id, "to_agent": outsider},
        )
        owner = next(
            item
            for item in client.app.state.deals
            if item.opportunity_id == deal.opportunity_id
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Colega de outro escritório"
    assert owner.sales_agent == deal.sales_agent


def test_repa_13_deal_outside_the_workable_queue_is_422() -> None:
    with TestClient(create_app()) as client:
        deal, colleague = _pair(client)
        won = next(item for item in client.app.state.deals if item.deal_stage == "Won")
        response = client.post(
            "/api/handoff",
            json={"opportunity_id": won.opportunity_id, "to_agent": colleague},
        )
        owner = next(
            item
            for item in client.app.state.deals
            if item.opportunity_id == won.opportunity_id
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Este negócio não está na fila trabalhável"
    assert owner.sales_agent == won.sales_agent
