"""FastAPI application factory. CSV load is a startup hook placeholder."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.settings = get_settings()
    yield


def create_app() -> FastAPI:
    return FastAPI(title="Lead Scorer", lifespan=lifespan)
