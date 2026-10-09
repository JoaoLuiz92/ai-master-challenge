"""Ordered workable queue for one filtered view."""

from dataclasses import dataclass

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.scoring.confidence import confidence
from app.scoring.cooling import cooling
from app.scoring.priority import priority
from app.scoring.urgency import urgency
from app.views.estado import assign_estado
from app.views.explain import explain
from app.views.filter import split_view
from app.views.percentile import percentile_scores

EMPTY_VIEW_MESSAGE = "sem deals nesta visão"


@dataclass(frozen=True)
class ViewFilter:
    agent: str | None = None
    manager: str | None = None
    office: str | None = None


@dataclass(frozen=True)
class QueueItem:
    opportunity_id: str
    product: str
    account: str
    value: int
    deal_stage: str
    age_days: int
    score: int
    estado: str
    confidence: str
    reason: str
    action: str
    cooling: bool
    from_agent: str | None = None


@dataclass(frozen=True)
class QueueView:
    items: tuple[QueueItem, ...]
    empty_message: str | None


def build_queue(
    repo: tuple[Deal, ...],
    view_filter: ViewFilter | None = None,
) -> QueueView:
    """Workable deals of the view, highest PRIORIDADE first.

    SCORE and ESTADO are computed on this set only. An empty queue returns
    a message instead of failing.
    """
    selected = view_filter or ViewFilter()
    workable = split_view(
        repo,
        agent=selected.agent,
        manager=selected.manager,
        office=selected.office,
    ).workable
    if not workable:
        return QueueView(items=(), empty_message=EMPTY_VIEW_MESSAGE)

    closed_by_product: dict[str, int] = {}
    for deal in repo:
        if deal.deal_stage in ("Won", "Lost"):
            closed_by_product[deal.product] = closed_by_product.get(deal.product, 0) + 1

    prepared: list[tuple[Deal, int, float]] = []
    for deal in workable:
        age = age_days(deal.engage_date)
        if age is None:
            continue
        deal_urgency = urgency(age)
        if deal_urgency is None:
            continue
        prepared.append((deal, age, priority(deal.value, deal_urgency)))

    priorities = [rank for _deal, _age, rank in prepared]
    scores = percentile_scores(priorities)
    estados = assign_estado(priorities)
    items: list[QueueItem] = []
    for (deal, age, _rank), score, estado in zip(prepared, scores, estados, strict=True):
        assessed = confidence(
            deal.value,
            has_account=True,
            has_engage_date=True,
            closed_count=closed_by_product.get(deal.product, 0),
        )
        level = "Baixa" if deal.confidence == "Baixa" else assessed.level
        text = explain(deal.product, assessed.value, age)
        account = deal.account or ""
        items.append(
            QueueItem(
                opportunity_id=deal.opportunity_id,
                product=deal.product,
                account=account,
                value=assessed.value,
                deal_stage=deal.deal_stage,
                age_days=age,
                score=score,
                estado=estado,
                confidence=level,
                reason=text.reason,
                action=text.action,
                cooling=cooling(age),
                from_agent=deal.from_agent,
            )
        )

    order = sorted(range(len(items)), key=lambda index: (scores[index], priorities[index]), reverse=True)
    return QueueView(
        items=tuple(items[index] for index in order),
        empty_message=None,
    )
