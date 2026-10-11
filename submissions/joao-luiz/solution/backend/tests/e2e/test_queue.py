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
        body = client.get("/api/queue").json()

    work = body["trabalhar"]
    decide = body["decidir"]
    assert work or decide
    assert all(item["deal_stage"] == "Engaging" for item in work + decide)
    assert all(item["account"] for item in work + decide)
    if work:
        scores = [item["score"] for item in work]
        assert scores == sorted(scores, reverse=True)
        assert work[0].keys() >= QUEUE_FIELDS
        assert work[0]["estado"] in {"Focar", "Acompanhar"}
    if decide:
        assert decide[0]["estado"] == "Decidir"


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
        world = client.get("/api/queue").json()
        east = client.get("/api/queue", params={"office": "East"}).json()

    world_scores = {item["opportunity_id"]: item["score"] for item in world["trabalhar"]}
    changed = [
        item["opportunity_id"]
        for item in east["trabalhar"]
        if item["opportunity_id"] in world_scores
        and item["score"] != world_scores[item["opportunity_id"]]
    ]
    assert world["trabalhar"]
    assert east["trabalhar"]
    assert changed


def test_empty_agent_returns_the_empty_state_message() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/queue", params={"agent": "Carl Lin"}).json()

    assert body["items"] == []
    assert body["trabalhar"] == []
    assert body["decidir"] == []
    assert body["revisar"] == []
    assert body["empty_message"] == "sem deals nesta visão"


def test_chance_14_queue_returns_three_buckets_with_totals() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/queue", params={"view": "mine", "agent": "Anna Snelling"}).json()

    assert "trabalhar" in body and "decidir" in body and "revisar" in body
    totals = body["totals"]
    assert totals["trabalhar_count"] == len(body["trabalhar"])
    assert totals["decidir_count"] == len(body["decidir"])
    assert totals["revisar_count"] == len(body["revisar"])
    work_ids = {item["opportunity_id"] for item in body["trabalhar"]}
    decide_ids = {item["opportunity_id"] for item in body["decidir"]}
    review_ids = {item["opportunity_id"] for item in body["revisar"]}
    assert work_ids.isdisjoint(decide_ids)
    assert work_ids.isdisjoint(review_ids)
    assert decide_ids.isdisjoint(review_ids)
    if body["decidir"]:
        prices = [item["value"] for item in body["decidir"]]
        assert prices == sorted(prices, reverse=True)
        assert all(item["action"] == "Requalificar ou encerrar" for item in body["decidir"])
    if body["trabalhar"]:
        scores = [item["score"] for item in body["trabalhar"]]
        assert scores == sorted(scores, reverse=True)


def test_chance_29_switching_view_recomputes_trabalhar_percentile() -> None:
    with TestClient(create_app()) as client:
        world = client.get("/api/queue").json()
        east = client.get("/api/queue", params={"office": "East"}).json()

    world_scores = {item["opportunity_id"]: item["score"] for item in world["trabalhar"]}
    changed = [
        item["opportunity_id"]
        for item in east["trabalhar"]
        if item["opportunity_id"] in world_scores
        and item["score"] != world_scores[item["opportunity_id"]]
    ]
    assert world["trabalhar"] and east["trabalhar"]
    assert changed
