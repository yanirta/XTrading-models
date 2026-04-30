"""Abstract time provider interface."""

from abc import ABC, abstractmethod
from datetime import datetime, date, time as dtime
from zoneinfo import ZoneInfo

import pandas_market_calendars as mcal

_nyse = None


def _get_nyse():
    global _nyse
    if _nyse is None:
        _nyse = mcal.get_calendar("NYSE")
    return _nyse


def _prev_trading_day(d: date) -> date:
    cal = _get_nyse()
    candidate = d
    for _ in range(10):
        candidate = candidate.__class__.fromordinal(candidate.toordinal() - 1)
        schedule = cal.valid_days(start_date=candidate, end_date=candidate)
        if len(schedule) > 0:
            return candidate
    raise ValueError(f"No trading day found within 10 days before {d}")


class TimeProvider(ABC):
    """Abstract interface for time access.

    Constructed with a timezone (ZoneInfo) used for localize() and
    previous_trading_day().
    """

    def __init__(self, tz: ZoneInfo):
        self._tz = tz

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def today(self) -> date:
        pass

    def set_time(self, dt: datetime) -> None:
        """Advance simulated time. No-op for live providers."""
        pass

    def localize(self, dt: datetime) -> datetime:
        """Apply stored timezone to a naive datetime."""
        return dt.replace(tzinfo=self._tz)

    def previous_trading_day(self, d: date | None) -> datetime:
        """Return localized midnight datetime of the previous NYSE trading day.

        When d is None, uses self.now().date() as the reference.
        """
        reference = d if d is not None else self.now().date()
        prev = _prev_trading_day(reference)
        return self.localize(datetime.combine(prev, dtime(0, 0)))
