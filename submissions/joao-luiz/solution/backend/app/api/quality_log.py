"""Corrections recorded when the CSVs were normalized at startup."""

from dataclasses import asdict

from fastapi import APIRouter, Request

from app.ingestion.quality import QualityLogEntry

router = APIRouter()


@router.get("/api/quality-log")
def get_quality_log(request: Request) -> dict:
    """The log is the one produced by ingestion, not a second pass over the CSVs."""
    log: list[QualityLogEntry] = request.app.state.quality_log
    return {"entries": [asdict(entry) for entry in log]}
