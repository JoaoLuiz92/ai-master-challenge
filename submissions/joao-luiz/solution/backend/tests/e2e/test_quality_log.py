"""E2E tests for T20: GET /api/quality-log (LEAD-13)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_lead_13_quality_log_lists_each_correction_including_gtxpro() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/quality-log")

    assert response.status_code == 200
    entries = response.json()["entries"]
    assert len(entries) == 3
    by_type = {entry["type"]: entry for entry in entries}
    assert set(by_type) == {"product_alias", "sector_alias", "location_alias"}

    product = by_type["product_alias"]
    assert product["correction"] == "alias GTXPro->GTX Pro"
    assert product["affected_rows"] == 1480

    sector = by_type["sector_alias"]
    assert sector["correction"] == "alias technolgy->technology"
    assert sector["affected_rows"] == 12

    location = by_type["location_alias"]
    assert location["correction"] == "alias Philipines->Philippines"
    assert location["affected_rows"] == 1
