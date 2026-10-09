"""Urgency from deal age. Age never zeroes the value and never drops the deal.

The curve is the one frozen in the spec, not the exploratory curve in eda.py.
"""

from app.constants import WON_MEDIAN, WON_P90

URGENCY_FLOOR = 0.35
_RAMP_START = 0.5
_DECAY_END = WON_P90 * 2


def urgency(age_days: int | None) -> float | None:
    """Map age in days to urgency in [0.35, 1.0].

    Ramp 0–57d from 0.5 to 1.0, plateau 1.0 through 106d, then linear decay
    to 0.35 at 212d. Older ages stay on the floor.

    None means the age is missing, so no urgency is inferred. Routing that
    deal to Revisar belongs to the view layer.
    """
    if age_days is None:
        return None
    if age_days <= WON_MEDIAN:
        return _RAMP_START + (1.0 - _RAMP_START) * (age_days / WON_MEDIAN)
    if age_days <= WON_P90:
        return 1.0
    drop = 1.0 - URGENCY_FLOOR
    raw = 1.0 - drop * (age_days - WON_P90) / (_DECAY_END - WON_P90)
    return max(URGENCY_FLOOR, raw)
