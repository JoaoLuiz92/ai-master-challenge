"""Offline backtest: reconstruct the queue at past cutoffs with no future leakage."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, timedelta
from random import Random
from statistics import median, pstdev

from app.ingestion.repository import Deal
from app.scoring.chance import chance, resolve_wall, survival_table
from app.scoring.cohort import build_cohort
from app.scoring.priority import priority
from app.settings import get_settings
from app.views.filter import split_view

DEFAULT_CUTOFFS: tuple[date, ...] = (
    date(2017, 6, 30),
    date(2017, 8, 31),
    date(2017, 9, 30),
)
HORIZON_DAYS = 90
TOP_N = 5


@dataclass(frozen=True)
class CutoffCapture:
    cutoff: date
    nova: float
    preco: float
    preco_parede: float
    aleatorio: float


@dataclass(frozen=True)
class BacktestReport:
    cutoffs: tuple[CutoffCapture, ...]
    nova_vs_preco_delta: float
    dispersion: float
    adopted: bool


def snapshot_at(repo: tuple[Deal, ...], cutoff: date) -> tuple[Deal, ...]:
    """Deals as known on cutoff. Future closes are still open. Later engages are gone."""
    seen: list[Deal] = []
    for deal in repo:
        if deal.engage_date is not None and deal.engage_date > cutoff:
            continue
        if deal.close_date is not None and deal.close_date <= cutoff:
            seen.append(deal)
            continue
        if deal.engage_date is None:
            seen.append(deal)
            continue
        seen.append(
            replace(deal, deal_stage="Engaging", close_date=None, close_value=None)
        )
    return tuple(seen)


def run_backtest(
    repo: tuple[Deal, ...],
    cutoffs: tuple[date, ...] = DEFAULT_CUTOFFS,
    top_n: int = TOP_N,
) -> BacktestReport:
    rows: list[CutoffCapture] = []
    for cutoff in cutoffs:
        snap = snapshot_at(repo, cutoff)
        nova_ids = _top_n_by(snap, cutoff, top_n, kind="nova")
        preco_ids = _top_n_by(snap, cutoff, top_n, kind="preco")
        preco_parede_ids = _top_n_by(snap, cutoff, top_n, kind="preco_parede")
        random_ids = _top_n_by(snap, cutoff, top_n, kind="aleatorio")
        rows.append(
            CutoffCapture(
                cutoff=cutoff,
                nova=_captured_revenue(repo, nova_ids, cutoff),
                preco=_captured_revenue(repo, preco_ids, cutoff),
                preco_parede=_captured_revenue(repo, preco_parede_ids, cutoff),
                aleatorio=_captured_revenue(repo, random_ids, cutoff),
            )
        )
    deltas = [row.nova - row.preco for row in rows]
    delta = float(median(deltas))
    spread = float(pstdev(deltas)) if len(deltas) > 1 else 0.0
    return BacktestReport(
        cutoffs=tuple(rows),
        nova_vs_preco_delta=delta,
        dispersion=spread,
        adopted=delta > 0,
    )


def _top_n_by(
    snap: tuple[Deal, ...],
    cutoff: date,
    top_n: int,
    kind: str,
) -> frozenset[str]:
    candidates = [
        deal
        for deal in split_view(snap).workable
        if deal.engage_date is not None and deal.engage_date <= cutoff
    ]
    if kind == "nova":
        table, wall = _model(snap, cutoff)
        scored = sorted(
            candidates,
            key=lambda deal: _expected(deal, table, wall, cutoff),
            reverse=True,
        )
    elif kind == "preco":
        scored = sorted(candidates, key=lambda deal: deal.value, reverse=True)
    elif kind == "preco_parede":
        _, wall = _model(snap, cutoff)
        within = [
            deal
            for deal in candidates
            if deal.engage_date is not None
            and (cutoff - deal.engage_date).days <= wall
        ]
        scored = sorted(within, key=lambda deal: deal.value, reverse=True)
    else:
        scored = list(candidates)
        Random(0).shuffle(scored)
    picked: list[str] = []
    per_agent: dict[str, int] = {}
    for deal in scored:
        taken = per_agent.get(deal.sales_agent, 0)
        if taken >= top_n:
            continue
        picked.append(deal.opportunity_id)
        per_agent[deal.sales_agent] = taken + 1
    return frozenset(picked)


def _expected(deal: Deal, table, wall: int, cutoff: date) -> float:
    age = (cutoff - deal.engage_date).days if deal.engage_date else None
    deal_chance = chance(age, table, wall) or 0.0
    return priority(deal.value, deal_chance)


def _model(snap: tuple[Deal, ...], cutoff: date):
    cohort = build_cohort(snap, today=cutoff)
    # Open ages in the snapshot use cutoff, not TODAY, via build_cohort(today=cutoff).
    settings = get_settings()
    table = survival_table(cohort, settings.chance_bands)
    return table, resolve_wall(cohort, settings.wall_override)


def _captured_revenue(
    original: tuple[Deal, ...],
    picked: frozenset[str],
    cutoff: date,
) -> float:
    end = cutoff + timedelta(days=HORIZON_DAYS)
    total = 0.0
    for deal in original:
        if deal.opportunity_id not in picked:
            continue
        if deal.deal_stage != "Won" or deal.close_date is None:
            continue
        if cutoff < deal.close_date <= end:
            total += deal.close_value or 0.0
    return total
