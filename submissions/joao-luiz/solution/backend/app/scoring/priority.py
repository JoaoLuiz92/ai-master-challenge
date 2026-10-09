"""Priority is list value times urgency. Conversion probability is not an input."""


def priority(value: float, urgency: float) -> float:
    """PRIORIDADE = VALOR × URGÊNCIA. No other factor."""
    return value * urgency
