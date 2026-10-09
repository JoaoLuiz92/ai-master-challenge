"""Unit tests for T4: deals from a normalized dataset (LEAD-14)."""

from __future__ import annotations

from datetime import date

import pandas as pd

from app.ingestion.loader import RawDataset, load_dataset
from app.ingestion.quality import normalize
from app.ingestion.repository import Deal, build_deals
from app.settings import get_settings


def _real_raw() -> RawDataset:
    return load_dataset(get_settings().data_dir)


def _as_date(value: object) -> date | None:
    if value is None or pd.isna(value):
        return None
    return date.fromisoformat(str(value)[:10])


def _as_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def test_lead_14_former_gtxpro_rows_keep_catalog_price() -> None:
    raw = _real_raw()
    former_ids = set(
        raw.sales_pipeline.loc[
            raw.sales_pipeline["product"] == "GTXPro", "opportunity_id"
        ]
    )
    assert len(former_ids) == 1480

    normalized, _log = normalize(raw)
    deals = build_deals(normalized)
    matched = [deal for deal in deals if deal.opportunity_id in former_ids]

    assert len(matched) == 1480
    assert {deal.product for deal in matched} == {"GTX Pro"}
    assert {deal.value for deal in matched} == {4821}
    assert sum(deal.value == 0 for deal in matched) == 0
    assert all(deal.confidence is None for deal in matched)


def test_every_pipeline_row_becomes_a_deal() -> None:
    raw = _real_raw()
    normalized, _log = normalize(raw)
    deals = build_deals(normalized)
    pipeline = normalized.sales_pipeline
    prices = dict(
        zip(
            normalized.products["product"],
            normalized.products["sales_price"],
            strict=True,
        )
    )
    teams = normalized.sales_teams.set_index("sales_agent")

    assert len(deals) == len(pipeline) == 8800
    assert [deal.opportunity_id for deal in deals] == pipeline["opportunity_id"].tolist()
    assert all(isinstance(deal, Deal) for deal in deals)

    by_id = {deal.opportunity_id: deal for deal in deals}
    assert len(by_id) == 8800

    for row in pipeline.itertuples(index=False):
        deal = by_id[row.opportunity_id]
        expected_account = None if pd.isna(row.account) else str(row.account)
        team = teams.loc[row.sales_agent]
        assert deal.sales_agent == row.sales_agent
        assert deal.product == row.product
        assert deal.deal_stage == row.deal_stage
        assert deal.account == expected_account, row.opportunity_id
        assert deal.engage_date == _as_date(row.engage_date), row.opportunity_id
        assert deal.close_date == _as_date(row.close_date), row.opportunity_id
        assert deal.close_value == _as_float(row.close_value), row.opportunity_id
        assert deal.value == int(prices[row.product]), row.opportunity_id
        assert deal.confidence is None, row.opportunity_id
        assert deal.manager == team.manager, row.opportunity_id
        assert deal.regional_office == team.regional_office, row.opportunity_id

    assert sum(deal.account is None for deal in deals) == 1425
    assert sum(deal.engage_date is None for deal in deals) == 500
    assert sum(deal.value == 0 for deal in deals) == 0
    assert {deal.deal_stage for deal in deals} == {
        "Engaging",
        "Prospecting",
        "Won",
        "Lost",
    }


def test_unmatched_product_sets_value_zero_and_baixa_confidence() -> None:
    raw = RawDataset(
        accounts=pd.DataFrame(
            {
                "account": ["Cancity"],
                "sector": ["technology"],
                "office_location": ["United States"],
            }
        ),
        products=pd.DataFrame(
            {"product": ["GTX Pro"], "series": ["GTX"], "sales_price": [4821]}
        ),
        sales_teams=pd.DataFrame(
            {
                "sales_agent": ["Ada"],
                "manager": ["Boss"],
                "regional_office": ["Central"],
            }
        ),
        sales_pipeline=pd.DataFrame(
            {
                "opportunity_id": ["SYNTH-1"],
                "sales_agent": ["Ada"],
                "product": ["Unknown Widget"],
                "account": ["Cancity"],
                "deal_stage": ["Engaging"],
                "engage_date": ["2017-06-01"],
                "close_date": [None],
                "close_value": [None],
            }
        ),
    )

    normalized, _log = normalize(raw)
    deals = build_deals(normalized)

    assert len(deals) == 1
    deal = deals[0]
    assert deal.opportunity_id == "SYNTH-1"
    assert deal.product == "Unknown Widget"
    assert deal.account == "Cancity"
    assert deal.deal_stage == "Engaging"
    assert deal.engage_date == date(2017, 6, 1)
    assert deal.close_date is None
    assert deal.value == 0
    assert deal.confidence == "Baixa"
