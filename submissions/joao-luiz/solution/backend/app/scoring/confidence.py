"""Confidence is min(completude, suporte). Weak support never changes list value."""

from dataclasses import dataclass
from typing import Literal

ConfidenceLevel = Literal["Alta", "Média", "Baixa"]

SUPPORT_MIN_CLOSED = 100
_RANK: dict[ConfidenceLevel, int] = {"Baixa": 0, "Média": 1, "Alta": 2}


@dataclass(frozen=True)
class ConfidenceAssessment:
    value: int
    level: ConfidenceLevel


def confidence(
    value: int,
    *,
    has_account: bool,
    has_engage_date: bool,
    closed_count: int,
) -> ConfidenceAssessment:
    """Map data quality and product support to Alta, Média, or Baixa.

    Missing account or engage_date is Baixa. A complete deal whose product
    has fewer than 100 closed rows is Média. Otherwise Alta. `value` is
    returned as given.
    """
    completude: ConfidenceLevel = (
        "Alta" if has_account and has_engage_date else "Baixa"
    )
    suporte: ConfidenceLevel = (
        "Alta" if closed_count >= SUPPORT_MIN_CLOSED else "Média"
    )
    level = completude if _RANK[completude] <= _RANK[suporte] else suporte
    return ConfidenceAssessment(value=value, level=level)
