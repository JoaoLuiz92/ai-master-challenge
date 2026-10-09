"""Join a normalized CRM dataset into deals. Does not apply aliases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

import pandas as pd

from app.ingestion.loader import RawDataset

CatalogConfidence = Literal["Baixa"]


@dataclass(frozen=True)
class Deal:
    opportunity_id: str
    sales_agent: str
    product: str
    account: str | None
    deal_stage: str
    engage_date: date | None
    close_date: date | None
    close_value: float | None
    value: int
    confidence: CatalogConfidence | None
    manager: str | None
    regional_office: str | None


def build_deals(dataset: RawDataset) -> tuple[Deal, ...]:
    """One deal per pipeline row. Price is the catalog sales_price of product.

    `dataset` must already be normalized. A product still missing from the
    catalog gets value 0 and confidence Baixa. That flag is only the catalog
    miss; the confidence formula belongs elsewhere.
    """
    price_by_product = {
        str(product): int(price)
        for product, price in zip(
            dataset.products["product"],
            dataset.products["sales_price"],
            strict=True,
        )
    }
    team_by_agent = {
        str(agent): (_text(manager), _text(office))
        for agent, manager, office in zip(
            dataset.sales_teams["sales_agent"],
            dataset.sales_teams["manager"],
            dataset.sales_teams["regional_office"],
            strict=True,
        )
    }

    deals: list[Deal] = []
    for row in dataset.sales_pipeline.itertuples(index=False):
        product = _text(row.product) or ""
        price = price_by_product.get(product)
        matched = price is not None
        agent = _text(row.sales_agent) or ""
        team = team_by_agent.get(agent)
        deals.append(
            Deal(
                opportunity_id=_text(row.opportunity_id) or "",
                sales_agent=agent,
                product=product,
                account=_text(row.account),
                deal_stage=_text(row.deal_stage) or "",
                engage_date=_as_date(row.engage_date),
                close_date=_as_date(row.close_date),
                close_value=_as_float(row.close_value),
                value=price if matched else 0,
                confidence=None if matched else "Baixa",
                manager=None if team is None else team[0],
                regional_office=None if team is None else team[1],
            )
        )
    return tuple(deals)


def _text(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _as_date(value: object) -> date | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _as_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)
