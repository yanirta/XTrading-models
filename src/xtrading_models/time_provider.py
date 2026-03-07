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
