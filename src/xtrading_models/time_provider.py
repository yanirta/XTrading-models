"""Abstract time provider interface."""

from abc import ABC, abstractmethod
from datetime import date, datetime, time


class TimeProvider(ABC):
    """Abstract interface for time access."""

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def today(self) -> date:
        pass

    def set_time(self, dt: datetime) -> None:  # noqa: ARG002
        """Advance simulated time. No-op for live providers."""
        pass

    def combine(self, t: time) -> datetime:
        """Return a timezone-aware datetime for today at the given time."""
        now = self.now()
        return datetime.combine(now.date(), t, tzinfo=now.tzinfo)
