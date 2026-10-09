"""E2E tests for T17: GET /api/queue (LEAD-01, LEAD-04, LEAD-18, LEAD-23)."""

from fastapi.testclient import TestClient

from app.main import create_app

QUEUE_FIELDS = {
    "product",
    "account",
    "value",
    "deal_stage",
    "age_days",
    "score",
    "estado",
    "confidence",
    "reason",
    "action",
}


def test_lead_01_queue_is_engaging_with_account_ordered_by_score() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/queue", params={"view": "mine", "agent": "Anna Snelling"}).json()

    items = body["items"]
    assert items
    assert body["empty_message"] is None
    scores = [item["score"] for item in items]
    assert scores == sorted(scores, reverse=True)
    assert all(item["deal_stage"] == "Engaging" for item in items)
    assert all(item["account"] for item in items)
    assert items[0].keys() >= QUEUE_FIELDS
    assert items[0]["estado"] in {"Focar", "Acompanhar"}


def test_lead_18_revisar_is_separate_from_the_workable_queue() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/queue", params={"view": "mine", "agent": "Anna Snelling"}).json()

    item_ids = {item["opportunity_id"] for item in body["items"]}
    review_ids = {item["opportunity_id"] for item in body["revisar"]}
    assert body["revisar"]
    assert item_ids.isdisjoint(review_ids)
    assert all(item["estado"] == "Revisar" for item in body["revisar"])
    assert all(item["action"] == "Qualificar conta/dados" for item in body["revisar"])
    assert all(item["account"] is None or item["age_days"] is None for item in body["revisar"])
    stages = {item["deal_stage"] for item in body["items"]} | {
        item["deal_stage"] for item in body["revisar"]
    }
    assert stages.isdisjoint({"Won", "Lost"})


def test_lead_23_switching_view_recomputes_the_percentile() -> None:
    with TestClient(create_app()) as client:
        mine = client.get(
            "/api/queue", params={"view": "mine", "agent": "Anna Snelling"}
        ).json()
        team = client.get(
            "/api/queue", params={"view": "team", "manager": "Dustin Brinkmann"}
        ).json()

    mine_scores = {item["opportunity_id"]: item["score"] for item in mine["items"]}
    changed = [
        item["opportunity_id"]
        for item in team["items"]
        if item["opportunity_id"] in mine_scores
        and item["score"] != mine_scores[item["opportunity_id"]]
    ]
    assert changed


def test_empty_agent_returns_the_empty_state_message() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/queue", params={"agent": "Carl Lin"}).json()

    assert body["items"] == []
    assert body["revisar"] == []
    assert body["empty_message"] == "sem deals nesta visão"
