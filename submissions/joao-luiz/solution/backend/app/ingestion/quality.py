"""Apply known CRM aliases and record each correction. No joins."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.ingestion.loader import RawDataset

PRODUCT_ALIASES = {
    "GTXPro": "GTX Pro",
}

SECTOR_ALIASES = {
    "technolgy": "technology",
}

LOCATION_ALIASES = {
    "Philipines": "Philippines",
}

CorrectionType = Literal["product_alias", "sector_alias", "location_alias"]


@dataclass(frozen=True)
class QualityLogEntry:
    correction: str
    type: CorrectionType
    affected_rows: int


def normalize(raw: RawDataset) -> tuple[RawDataset, list[QualityLogEntry]]:
    pipeline = raw.sales_pipeline.copy()
    accounts = raw.accounts.copy()
    log: list[QualityLogEntry] = []

    pipeline["product"], product_log = _apply_aliases(
        pipeline["product"], PRODUCT_ALIASES, "product_alias"
    )
    log.extend(product_log)

    accounts["sector"], sector_log = _apply_aliases(
        accounts["sector"], SECTOR_ALIASES, "sector_alias"
    )
    log.extend(sector_log)

    accounts["office_location"], location_log = _apply_aliases(
        accounts["office_location"], LOCATION_ALIASES, "location_alias"
    )
    log.extend(location_log)

    normalized = RawDataset(
        accounts=accounts,
        products=raw.products,
        sales_teams=raw.sales_teams,
        sales_pipeline=pipeline,
    )
    return normalized, log


def _apply_aliases(
    series: pd.Series,
    aliases: dict[str, str],
    correction_type: CorrectionType,
) -> tuple[pd.Series, list[QualityLogEntry]]:
    updated = series
    entries: list[QualityLogEntry] = []
    for source, target in aliases.items():
        affected = int((updated == source).sum())
        if affected == 0:
            continue
        updated = updated.replace({source: target})
        entries.append(
            QualityLogEntry(
                correction=f"alias {source}->{target}",
                type=correction_type,
                affected_rows=affected,
            )
        )
    return updated, entries
