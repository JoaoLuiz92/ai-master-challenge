"""E2E tests for GET /api/export.csv (CHANCE-28)."""

import csv
import io

from fastapi.testclient import TestClient

from app.main import create_app

DISPLAYED_COLUMNS = [
    "fila",
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


def test_chance_28_csv_includes_three_queues_in_screen_order() -> None:
    with TestClient(create_app()) as client:
        queue = client.get("/api/queue").json()
        exported = client.get("/api/export.csv")

    work = queue["trabalhar"]
    decide = queue["decidir"]
    review = queue["revisar"]
    assert work and decide and review
    assert exported.status_code == 200

    rows = list(csv.reader(io.StringIO(exported.text)))
    assert rows[0] == DISPLAYED_COLUMNS
    body = rows[1:]
    n_work, n_decide, n_review = len(work), len(decide), len(review)
    assert len(body) == n_work + n_decide + n_review
    filas = [row[0] for row in body]
    assert filas == (
        ["Trabalhar"] * n_work + ["Decidir"] * n_decide + ["Revisar"] * n_review
    )
    for item, row in zip(work, body[:n_work], strict=True):
        assert row[DISPLAYED_COLUMNS.index("product")] == item["product"]
        assert row[DISPLAYED_COLUMNS.index("estado")] == item["estado"]
        assert row[DISPLAYED_COLUMNS.index("action")] == item["action"]
    for item, row in zip(decide, body[n_work : n_work + n_decide], strict=True):
        assert row[DISPLAYED_COLUMNS.index("product")] == item["product"]
        assert row[DISPLAYED_COLUMNS.index("estado")] == "Decidir"
        assert row[DISPLAYED_COLUMNS.index("action")] == "Requalificar ou encerrar"
    for item, row in zip(review, body[n_work + n_decide :], strict=True):
        assert row[DISPLAYED_COLUMNS.index("product")] == item["product"]
        assert row[DISPLAYED_COLUMNS.index("estado")] == "Revisar"
        assert row[DISPLAYED_COLUMNS.index("action")] == "Qualificar conta/dados"


def test_chance_28_filtered_export_keeps_the_three_queues() -> None:
    params = {"agent": "Anna Snelling"}
    with TestClient(create_app()) as client:
        queue = client.get("/api/queue", params=params).json()
        exported = client.get("/api/export.csv", params=params)

    decide = queue["decidir"]
    review = queue["revisar"]
    assert decide and review
    body = list(csv.reader(io.StringIO(exported.text)))[1:]
    filas = [row[0] for row in body]
    assert "Decidir" in filas
    assert "Revisar" in filas
    assert len(body) == len(queue["trabalhar"]) + len(decide) + len(review)
