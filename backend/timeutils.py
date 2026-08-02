"""Time helpers, in one place.

`datetime.utcnow()` is deprecated and scheduled for removal from Python. The
obvious replacement, `datetime.now(timezone.utc)`, is NOT a drop-in here: it
returns an *aware* datetime, while every `DateTime` column in models.py is
declared without `timezone=True` and therefore stores *naive* values. Comparing
an aware datetime with a naive one raises TypeError, so a careless swap would
turn a deprecation warning into a runtime crash in the sales report.

Hence two helpers with different jobs:
  - `utc_now()`      writes timestamps, and stays naive to match the columns.
  - `colombia_today()` answers "what day is it at the restaurant", which is a
                     different question from "what day is it on the server".
"""
from datetime import datetime, timedelta, timezone

# Colombia is UTC-5 the whole year — the country does not observe daylight
# saving time, so a fixed offset is correct rather than a simplification.
COLOMBIA_TZ = timezone(timedelta(hours=-5))


def utc_now() -> datetime:
    """Now in UTC, without tzinfo — exactly what `datetime.utcnow()` returned.

    Used as the default for created_at/updated_at columns.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def colombia_today():
    """Today's date where the restaurant is.

    A server in UTC rolls over to the next day at 19:00 Colombian time, so
    asking the server for "today" would close the till five hours early.
    """
    return datetime.now(COLOMBIA_TZ).date()
