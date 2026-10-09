"""SCORE is the percentile of PRIORIDADE inside the view that was passed in.

There is no global percentile. A new list is a new view.
"""


def percentile_scores(priorities: list[float]) -> list[int]:
    """SCORE = 100 × (deals in this list with priority ≤ this one) ÷ N.

    Ties share the score. A single deal scores 100. Order matches the input.
    """
    count = len(priorities)
    if count == 0:
        return []
    return [
        round(100 * sum(other <= value for other in priorities) / count)
        for value in priorities
    ]
