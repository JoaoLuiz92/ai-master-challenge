"""ESTADO from the view: the top slice of priority is Focar."""

import math

from app.views.percentile import percentile_scores


def assign_estado(priorities: list[float]) -> list[str]:
    """Mark ceil(20% × N) deals Focar, at least one when the view is not empty.

    The rest of the queue is Acompanhar. Rank comes from the view percentile,
    which follows PRIORIDADE. Output stays in input order.
    """
    count = len(priorities)
    if count == 0:
        return []
    cut = max(1, math.ceil(0.20 * count))
    scores = percentile_scores(priorities)
    ranked = sorted(range(count), key=lambda index: scores[index], reverse=True)
    focar = set(ranked[:cut])
    return ["Focar" if index in focar else "Acompanhar" for index in range(count)]
