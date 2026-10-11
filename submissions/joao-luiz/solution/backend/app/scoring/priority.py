"""Priority is list value times chance of closing. No conversion model."""


def priority(value: float, chance: float) -> float:
    """PRIORIDADE = VALOR × CHANCE. Past the wall, chance is 0 so priority is 0."""
    return value * chance
