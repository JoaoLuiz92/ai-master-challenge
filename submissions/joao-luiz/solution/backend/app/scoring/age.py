"""Deal age in days against the frozen TODAY anchor.

Age measures days. It never removes a deal from the queue.
"""

from datetime import date

from app.constants import TODAY


def age_days(engage_date: date | None) -> int | None:
    """Days from engage_date to TODAY.

    A missing engage_date returns None. That only signals that urgency must
    not be inferred later. This function does not substitute close_date and
    does not route the deal anywhere.
    """
    if engage_date is None:
        return None
    return (TODAY - engage_date).days
