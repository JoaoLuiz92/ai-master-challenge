"""E2E tests for T19: GET /api/export.csv (LEAD-25)."""

import csv
import io

from fastapi.testclient import TestClient

from app.main import create_app

DISPLAYED_COLUMNS = [
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
]


def test_lead_25_csv_matches_the_filtered_queue_line_by_line() -> None:
    params = {"view": "mine", "agent": "Anna Snelling"}
    with TestClient(create_app()) as client:
        queue = client.get("/api/queue", params=params)
        exported = client.get("/api/export.csv", params=params)

    assert queue.status_code == 200
    items = queue.json()["items"]
    assert items
    assert exported.status_code == 200

    rows = list(csv.reader(io.StringIO(exported.text)))
    assert rows[0] == DISPLAYED_COLUMNS
    body = rows[1:]
    assert len(body) == len(items)
    for item, row in zip(items, body, strict=True):
        assert row == [str(item[column]) for column in DISPLAYED_COLUMNS]
