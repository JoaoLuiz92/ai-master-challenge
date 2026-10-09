"""Integration tests for T2: load the four CRM CSVs, fail closed on missing files."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.ingestion.loader import DatasetLoadError, RawDataset, load_dataset
from app.main import create_app
from app.settings import Settings, get_settings

PIPELINE_COLUMNS = [
    "opportunity_id",
    "sales_agent",
    "product",
    "account",
    "deal_stage",
    "engage_date",
    "close_date",
    "close_value",
]
ACCOUNT_COLUMNS = [
    "account",
    "sector",
    "year_established",
    "revenue",
    "employees",
    "office_location",
    "subsidiary_of",
]
PRODUCT_COLUMNS = ["product", "series", "sales_price"]
TEAM_COLUMNS = ["sales_agent", "manager", "regional_office"]
REQUIRED_CSVS = (
    "accounts.csv",
    "products.csv",
    "sales_teams.csv",
    "sales_pipeline.csv",
)


def _copy_csvs(dest: Path, names: tuple[str, ...] = REQUIRED_CSVS) -> None:
    src = get_settings().data_dir
    for name in names:
        shutil.copy(src / name, dest / name)


def test_load_dataset_reads_four_real_csvs_with_csv_columns() -> None:
    raw = load_dataset(get_settings().data_dir)

    assert isinstance(raw, RawDataset)
    assert len(raw.sales_pipeline) == 8800
    assert len(raw.accounts) == 85
    assert len(raw.products) == 7
    assert len(raw.sales_teams) == 35
    assert list(raw.sales_pipeline.columns) == PIPELINE_COLUMNS
    assert list(raw.accounts.columns) == ACCOUNT_COLUMNS
    assert list(raw.products.columns) == PRODUCT_COLUMNS
    assert list(raw.sales_teams.columns) == TEAM_COLUMNS
    assert [field.name for field in RawDataset.__dataclass_fields__.values()] == [
        "accounts",
        "products",
        "sales_teams",
        "sales_pipeline",
    ]


def test_load_dataset_raises_when_required_csv_is_missing(tmp_path: Path) -> None:
    _copy_csvs(tmp_path, ("accounts.csv", "products.csv", "sales_teams.csv"))

    with pytest.raises(DatasetLoadError, match="sales_pipeline.csv"):
        load_dataset(tmp_path)


def test_load_dataset_raises_when_required_csv_is_unreadable(tmp_path: Path) -> None:
    _copy_csvs(tmp_path)
    (tmp_path / "products.csv").write_bytes(b"")

    with pytest.raises(DatasetLoadError, match="products.csv"):
        load_dataset(tmp_path)


def test_lifespan_stores_raw_dataset_on_app_state() -> None:
    app = create_app()
    with TestClient(app) as client:
        raw = client.app.state.raw_dataset
        assert isinstance(raw, RawDataset)
        assert len(raw.sales_pipeline) == 8800
        assert len(raw.accounts) == 85
        assert len(raw.products) == 7
        assert len(raw.sales_teams) == 35


def test_missing_csv_prevents_startup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.main.get_settings", lambda: Settings(data_dir=tmp_path))
    app = create_app()

    with pytest.raises(DatasetLoadError):
        with TestClient(app):
            pass
