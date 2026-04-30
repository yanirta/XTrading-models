"""Tests for TimeProvider localize() and previous_trading_day()."""

from datetime import date, datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from xtrading_models import TimeProvider

_ET = ZoneInfo("US/Eastern")


class ConcreteTimeProvider(TimeProvider):
    """Minimal concrete provider for testing base methods."""

    def __init__(self, current: datetime):
        super().__init__(_ET)
        self._current = current

    def now(self) -> datetime:
        return self._current

    def today(self) -> date:
        return self._current.date()


class TestLocalize:

    def test_naive_datetime_gets_timezone(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        naive = datetime(2025, 6, 15, 9, 30)
        result = tp.localize(naive)
        assert result.tzinfo is not None
        assert result.tzinfo == _ET

    def test_localized_date_equals_naive_date(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        naive = datetime(2025, 6, 15, 9, 30)
        result = tp.localize(naive)
        assert result.date() == naive.date()
        assert result.hour == 9
        assert result.minute == 30


class TestPreviousTradingDay:

    def test_previous_trading_day_from_date(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        # Jan 3 2025 is Friday; previous trading day = Jan 2 (Thursday)
        result = tp.previous_trading_day(date(2025, 1, 3))
        assert result.date() == date(2025, 1, 2)

    def test_result_is_midnight(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        result = tp.previous_trading_day(date(2025, 1, 3))
        assert result.hour == 0
        assert result.minute == 0

    def test_result_is_timezone_aware(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        result = tp.previous_trading_day(date(2025, 1, 3))
        assert result.tzinfo is not None

    def test_skips_weekend(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 6, 10, 0, tzinfo=_ET))
        # Jan 6 2025 is Monday; previous trading day = Jan 3 (Friday)
        result = tp.previous_trading_day(date(2025, 1, 6))
        assert result.date() == date(2025, 1, 3)

    def test_skips_holiday(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        # Jan 2 2025: previous trading day skips Jan 1 (New Year's) → Dec 31 2024
        result = tp.previous_trading_day(date(2025, 1, 2))
        assert result.date() == date(2024, 12, 31)

    def test_uses_now_when_d_is_none(self):
        current = datetime(2025, 1, 3, 15, 0, tzinfo=_ET)
        tp = ConcreteTimeProvider(current)
        # None → uses now() = Jan 3; previous = Jan 2
        result = tp.previous_trading_day(None)
        assert result.date() == date(2025, 1, 2)
