"""FastAPI application factory. CRM CSVs load into memory on startup."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.api.export import router as export_router
from app.api.handoff import router as handoff_router
from app.api.quality_log import router as quality_log_router
from app.api.queue import router as queue_router
from app.api.rollup import router as rollup_router
from app.ingestion.loader import load_dataset
from app.ingestion.quality import normalize
from app.ingestion.repository import build_deals
from app.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings
    app.state.raw_dataset = load_dataset(settings.data_dir)
    normalized, quality_log = normalize(app.state.raw_dataset)
    app.state.quality_log = quality_log
    app.state.deals = build_deals(normalized)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Lead Scorer", lifespan=lifespan)
    app.include_router(agents_router)
    app.include_router(queue_router)
    app.include_router(rollup_router)
    app.include_router(export_router)
    app.include_router(quality_log_router)
    app.include_router(handoff_router)
    return app
