"""Abstract time provider interface."""

from abc import ABC, abstractmethod
from datetime import datetime, date


class TimeProvider(ABC):
    """Abstract interface for time access."""

    @abstractmethod
    def now(self) -> datetime:
        pass

    @abstractmethod
    def today(self) -> date:
        pass

    def set_time(self, dt: datetime) -> None:
        """Advance simulated time. No-op for live providers."""
        pass
