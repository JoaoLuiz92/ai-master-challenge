"""Portuguese reason and action for one deal. Templates, not generated prose."""

from dataclasses import dataclass

from app.constants import WON_P90


@dataclass(frozen=True)
class Explanation:
    reason: str
    action: str


def explain(
    product: str,
    value: int,
    age_days: int | None,
    *,
    revisar: bool = False,
) -> Explanation:
    """Reason uses the PRD shape. Action follows the cycle, or Revisar."""
    if revisar or age_days is None:
        action = "Qualificar conta/dados"
    elif age_days > WON_P90:
        action = "Reengajar antes de esfriar"
    else:
        action = "Avançar proposta"

    money = f"US$ {_thousands(value)}"
    if age_days is None:
        reason = f"{product} · {money}"
    else:
        cycle = "esfriando" if age_days > WON_P90 else "dentro do ciclo"
        reason = f"{product} · {money} · {age_days} dias no funil · {cycle}"
    return Explanation(reason=reason, action=action)


def _thousands(value: int) -> str:
    return f"{value:,}".replace(",", ".")
