"""Tests for TimeProvider ABC."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from xtrading_models import TimeProvider

_ET = ZoneInfo("US/Eastern")


class ConcreteTimeProvider(TimeProvider):
    """Minimal concrete provider for testing."""

    def __init__(self, current: datetime):
        self._current = current

    def now(self) -> datetime:
        return self._current

    def today(self) -> date:
        return self._current.date()


class TestTimeProviderABC:

    def test_now_returns_injected_time(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        assert tp.now() == datetime(2025, 1, 2, 10, 0, tzinfo=_ET)

    def test_today_returns_date(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        assert tp.today() == date(2025, 1, 2)

    def test_set_time_is_noop_on_base(self):
        tp = ConcreteTimeProvider(datetime(2025, 1, 2, 10, 0, tzinfo=_ET))
        tp.set_time(datetime(2025, 6, 1, tzinfo=_ET))
        assert tp.now() == datetime(2025, 1, 2, 10, 0, tzinfo=_ET)
