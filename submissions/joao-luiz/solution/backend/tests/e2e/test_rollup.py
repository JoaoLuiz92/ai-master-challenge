"""E2E tests for T18: GET /api/rollup (LEAD-26, LEAD-28)."""

from fastapi.testclient import TestClient

from app.main import create_app

ROW_FIELDS = {
    "sales_agent",
    "queued_count",
    "expected_value_sum",
    "cooling_count",
    "good_deals_cooling",
    "trabalhar_count",
    "trabalhar_value",
    "decidir_count",
    "decidir_value",
}


def test_lead_26_rollup_lists_agents_with_queue_value_and_cooling() -> None:
    with TestClient(create_app()) as client:
        body = client.get("/api/rollup", params={"manager": "Dustin Brinkmann"}).json()

    assert body["rows"]
    anna = next(row for row in body["rows"] if row["sales_agent"] == "Anna Snelling")
    assert anna.keys() >= ROW_FIELDS
    assert anna["queued_count"] > 0
    assert anna["expected_value_sum"] > 0
    assert anna["cooling_count"] >= 0
    assert anna["good_deals_cooling"] <= anna["cooling_count"]
    assert anna["trabalhar_count"] + anna["decidir_count"] == anna["queued_count"]
    assert "parked_value" in body
    assert body["parked_value"] >= anna["decidir_value"]


def test_lead_28_filter_recomputes_rollup_and_who_is_focar() -> None:
    with TestClient(create_app()) as client:
        wide = client.get("/api/rollup").json()["rows"]
        central = client.get("/api/rollup", params={"office": "Central"}).json()["rows"]

    wide_by_agent = {row["sales_agent"]: row for row in wide}
    central_names = {row["sales_agent"] for row in central}
    assert central_names
    assert central_names < set(wide_by_agent)
    changed = [
        row["sales_agent"]
        for row in central
        if row["good_deals_cooling"] != wide_by_agent[row["sales_agent"]]["good_deals_cooling"]
    ]
    assert changed
