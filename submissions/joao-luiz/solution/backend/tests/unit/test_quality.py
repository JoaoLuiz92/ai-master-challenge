"""Unit tests for T3: CRM aliases and the quality log (LEAD-11/12/13)."""

from __future__ import annotations

import pandas as pd

from app.ingestion.loader import load_dataset
from app.ingestion.quality import QualityLogEntry, normalize
from app.settings import get_settings


def _real_raw():
    return load_dataset(get_settings().data_dir)


def _counts(series: pd.Series, value: str) -> int:
    return int((series == value).sum())


def test_lead_11_maps_gtxpro_to_gtx_pro_on_real_pipeline() -> None:
    raw = _real_raw()
    before = raw.sales_pipeline["product"]
    assert _counts(before, "GTXPro") == 1480
    gtx_pro_before = _counts(before, "GTX Pro")
    other = before[~before.isin(["GTXPro", "GTX Pro"])].value_counts()

    normalized, _log = normalize(raw)
    after = normalized.sales_pipeline["product"]

    assert _counts(raw.sales_pipeline["product"], "GTXPro") == 1480
    assert _counts(after, "GTXPro") == 0
    assert _counts(after, "GTX Pro") == gtx_pro_before + 1480
    assert len(after) == len(before)
    for name, count in other.items():
        assert _counts(after, str(name)) == int(count)


def test_lead_12_normalizes_sector_and_location_on_real_accounts() -> None:
    raw = _real_raw()
    sector_before = raw.accounts["sector"]
    location_before = raw.accounts["office_location"]
    assert _counts(sector_before, "technolgy") == 12
    assert _counts(location_before, "Philipines") == 1
    technology_before = _counts(sector_before, "technology")
    philippines_before = _counts(location_before, "Philippines")
    other_sectors = sector_before[
        ~sector_before.isin(["technolgy", "technology"])
    ].value_counts()
    other_locations = location_before[
        ~location_before.isin(["Philipines", "Philippines"])
    ].value_counts()

    normalized, _log = normalize(raw)
    sector_after = normalized.accounts["sector"]
    location_after = normalized.accounts["office_location"]

    assert _counts(raw.accounts["sector"], "technolgy") == 12
    assert _counts(raw.accounts["office_location"], "Philipines") == 1
    assert _counts(sector_after, "technolgy") == 0
    assert _counts(sector_after, "technology") == technology_before + 12
    assert _counts(location_after, "Philipines") == 0
    assert _counts(location_after, "Philippines") == philippines_before + 1
    assert len(sector_after) == len(sector_before)
    assert len(location_after) == len(location_before)
    for name, count in other_sectors.items():
        assert _counts(sector_after, str(name)) == int(count)
    for name, count in other_locations.items():
        assert _counts(location_after, str(name)) == int(count)


def test_lead_13_logs_correction_type_and_affected_rows() -> None:
    raw = _real_raw()

    _normalized, log = normalize(raw)

    assert len(log) == 3
    assert all(isinstance(entry, QualityLogEntry) for entry in log)
    by_type = {entry.type: entry for entry in log}
    assert set(by_type) == {"product_alias", "sector_alias", "location_alias"}

    product = by_type["product_alias"]
    assert product.correction == "alias GTXPro->GTX Pro"
    assert product.affected_rows == 1480

    sector = by_type["sector_alias"]
    assert sector.correction == "alias technolgy->technology"
    assert sector.affected_rows == 12

    location = by_type["location_alias"]
    assert location.correction == "alias Philipines->Philippines"
    assert location.affected_rows == 1
