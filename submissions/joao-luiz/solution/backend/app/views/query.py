"""Ordered workable queue for one filtered view."""

from dataclasses import dataclass

from app.ingestion.repository import Deal
from app.scoring.age import age_days
from app.scoring.chance import chance, past_wall_open_count, resolve_wall, survival_table
from app.scoring.cohort import build_cohort
from app.scoring.confidence import confidence
from app.scoring.cooling import cooling
from app.scoring.priority import priority
from app.scoring.urgency import urgency
from app.settings import get_settings
from app.views.buckets import bucketize
from app.views.estado import assign_estado
from app.views.explain import action_for, chance_sentence, explain, wall_sentence
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
    chance: float = 0.0
    from_agent: str | None = None


@dataclass(frozen=True)
class QueueView:
    items: tuple[QueueItem, ...]
    empty_message: str | None


@dataclass(frozen=True)
class ViewTotals:
    trabalhar_count: int
    trabalhar_value: int
    decidir_count: int
    decidir_value: int
    revisar_count: int


@dataclass(frozen=True)
class ViewResult:
    trabalhar: tuple[QueueItem, ...]
    decidir: tuple[QueueItem, ...]
    revisar: tuple[Deal, ...]
    totals: ViewTotals
    empty_message: str | None


def build_view(
    repo: tuple[Deal, ...],
    view_filter: ViewFilter | None = None,
) -> ViewResult:
    """Trabalhar scored by value × chance. SCORE is the Trabalhar percentile."""
    selected = view_filter or ViewFilter()
    table, wall = _chance_model(repo)
    past_count = past_wall_open_count(repo, wall)
    buckets = bucketize(
        repo,
        wall,
        agent=selected.agent,
        manager=selected.manager,
        office=selected.office,
    )
    trabalhar = _score_trabalhar(repo, buckets.trabalhar.deals, table, wall)
    decide_reason = wall_sentence(wall, past_count)
    decide_action = action_for("decidir")
    decidir = tuple(
        _queue_item(
            deal,
            age_days(deal.engage_date) or 0,
            0,
            "Decidir",
            0.0,
            reason=decide_reason,
            action=decide_action,
        )
        for deal in buckets.decidir.deals
    )
    empty = EMPTY_VIEW_MESSAGE if not trabalhar else None
    return ViewResult(
        trabalhar=trabalhar,
        decidir=decidir,
        revisar=buckets.revisar.deals,
        totals=ViewTotals(
            trabalhar_count=buckets.trabalhar.count,
            trabalhar_value=buckets.trabalhar.value_sum,
            decidir_count=buckets.decidir.count,
            decidir_value=buckets.decidir.value_sum,
            revisar_count=buckets.revisar.count,
        ),
        empty_message=empty,
    )


def _chance_model(
    repo: tuple[Deal, ...],
) -> tuple[tuple, int]:
    cohort = build_cohort(repo)
    settings = get_settings()
    table = survival_table(cohort, settings.chance_bands)
    return table, resolve_wall(cohort, settings.wall_override)


def _score_trabalhar(
    repo: tuple[Deal, ...],
    deals: tuple[Deal, ...],
    table: tuple,
    wall: int,
) -> tuple[QueueItem, ...]:
    if not deals:
        return ()
    closed_by_product: dict[str, int] = {}
    for deal in repo:
        if deal.deal_stage in ("Won", "Lost"):
            closed_by_product[deal.product] = closed_by_product.get(deal.product, 0) + 1
    prepared: list[tuple[Deal, int, float, float]] = []
    for deal in deals:
        age = age_days(deal.engage_date)
        if age is None:
            continue
        deal_chance = chance(age, table, wall) or 0.0
        prepared.append((deal, age, deal_chance, priority(deal.value, deal_chance)))
    priorities = [rank for _deal, _age, _chance, rank in prepared]
    scores = percentile_scores(priorities)
    estados = assign_estado(priorities)
    items = [
        _queue_item(
            deal,
            age,
            score,
            estado,
            deal_chance,
            closed_by_product,
            reason=chance_sentence(deal_chance),
            action=action_for("trabalhar"),
        )
        for (deal, age, deal_chance, _rank), score, estado in zip(
            prepared, scores, estados, strict=True
        )
    ]
    order = sorted(
        range(len(items)),
        key=lambda index: (scores[index], priorities[index]),
        reverse=True,
    )
    return tuple(items[index] for index in order)


def _queue_item(
    deal: Deal,
    age: int,
    score: int,
    estado: str,
    deal_chance: float,
    closed_by_product: dict[str, int] | None = None,
    reason: str | None = None,
    action: str | None = None,
) -> QueueItem:
    closed = closed_by_product or {}
    assessed = confidence(
        deal.value,
        has_account=bool(deal.account),
        has_engage_date=deal.engage_date is not None,
        closed_count=closed.get(deal.product, 0),
    )
    level = "Baixa" if deal.confidence == "Baixa" else assessed.level
    text = explain(deal.product, assessed.value, age)
    return QueueItem(
        opportunity_id=deal.opportunity_id,
        product=deal.product,
        account=deal.account or "",
        value=assessed.value,
        deal_stage=deal.deal_stage,
        age_days=age,
        score=score,
        estado=estado,
        confidence=level,
        reason=reason if reason is not None else text.reason,
        action=action if action is not None else text.action,
        cooling=cooling(age),
        chance=deal_chance,
        from_agent=deal.from_agent,
    )


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
