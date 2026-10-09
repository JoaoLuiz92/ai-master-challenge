"""Scaffold checks for T1 Done-when: factory, frozen constants, in-memory settings."""

from datetime import date

from fastapi import FastAPI

from app.constants import TODAY, WON_MEDIAN, WON_P90
from app.main import create_app
from app.settings import Settings, get_settings


def test_frozen_constants_match_spec() -> None:
    assert TODAY == date(2017, 12, 31)
    assert WON_MEDIAN == 57
    assert WON_P90 == 106


def test_create_app_returns_fastapi() -> None:
    from fastapi.testclient import TestClient

    app = create_app()
    assert isinstance(app, FastAPI)
    with TestClient(app) as client:
        assert client.app.state.settings.data_dir.name == "data"


def test_settings_point_at_csv_dir_without_database() -> None:
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.data_dir.name == "data"
    assert settings.data_dir.is_dir()
    assert not hasattr(settings, "database_url")
    assert "database" not in Settings.__dataclass_fields__
