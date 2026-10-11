"""Split a filtered view into Trabalhar, Decidir and Revisar."""

from __future__ import annotations

from dataclasses import dataclass

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.views.filter import split_view


@dataclass(frozen=True)
class Bucket:
    deals: tuple[Deal, ...]
    count: int
    value_sum: int


@dataclass(frozen=True)
class Buckets:
    trabalhar: Bucket
    decidir: Bucket
    revisar: Bucket


def bucketize(
    deals: tuple[Deal, ...],
    wall: int,
    *,
    agent: str | None = None,
    manager: str | None = None,
    office: str | None = None,
) -> Buckets:
    """Trabalhar = Engaging with account and age ≤ wall.

    Decidir = same but age > wall, ordered by list price descending.
    Revisar stays the split_view Revisar set.
    """
    split = split_view(deals, agent=agent, manager=manager, office=office)
    trabalhar: list[Deal] = []
    decidir: list[Deal] = []
    for deal in split.workable:
        age = age_days(deal.engage_date)
        if age is None:
            continue
        if age > wall:
            decidir.append(deal)
        else:
            trabalhar.append(deal)
    decidir.sort(key=lambda deal: deal.value, reverse=True)
    return Buckets(
        trabalhar=_as_bucket(trabalhar),
        decidir=_as_bucket(decidir),
        revisar=_as_bucket(split.revisar),
    )


def _as_bucket(deals: list[Deal] | tuple[Deal, ...]) -> Bucket:
    items = tuple(deals)
    return Bucket(
        deals=items,
        count=len(items),
        value_sum=sum(deal.value for deal in items),
    )
