"""E2E tests for T16: GET /api/agents (LEAD-15, LEAD-24)."""

from fastapi.testclient import TestClient

from app.main import create_app

GHOST_AGENTS = {
    "Carl Lin",
    "Carol Thompson",
    "Elizabeth Anderson",
    "Mei-Mei Johns",
    "Natalya Ivanova",
}


def test_lead_15_agents_without_deals_are_an_empty_state() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/agents")

    assert response.status_code == 200
    body = response.json()
    agents = body["agents"]
    empty = {agent["sales_agent"] for agent in agents if agent["empty"]}
    assert empty == GHOST_AGENTS
    for agent in agents:
        if agent["sales_agent"] in GHOST_AGENTS:
            assert agent["deal_count"] == 0
            assert agent["empty"] is True
        else:
            assert agent["empty"] is False
            assert agent["deal_count"] > 0


def test_lead_24_lists_managers_and_offices_for_the_filters() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/agents").json()

    assert body["managers"]
    assert body["offices"]
    assert all(isinstance(name, str) for name in body["managers"])
    assert all(isinstance(name, str) for name in body["offices"])
    for agent in body["agents"]:
        if agent["manager"] is not None:
            assert agent["manager"] in body["managers"]
        if agent["regional_office"] is not None:
            assert agent["regional_office"] in body["offices"]
