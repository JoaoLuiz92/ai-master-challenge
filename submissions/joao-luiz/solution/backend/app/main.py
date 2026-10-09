"""FastAPI application factory. CRM CSVs load into memory on startup."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ingestion.loader import load_dataset
from app.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings
    app.state.raw_dataset = load_dataset(settings.data_dir)
    yield


def create_app() -> FastAPI:
    return FastAPI(title="Lead Scorer", lifespan=lifespan)
