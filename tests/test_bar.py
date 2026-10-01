from datetime import datetime
import dataclasses

import pytest
from xtrading_models import BarData


def test_create_bardata():
    """Test creating a basic OHLCV bar."""
    bar = BarData(
        date=datetime(2026, 1, 2, 9, 30),
        open=150.00,
        high=151.50,
        low=149.75,
        close=151.00,
        volume=1000000
    )

    assert bar.date == datetime(2026, 1, 2, 9, 30)
    assert bar.open == 150.00
    assert bar.high == 151.50
    assert bar.low == 149.75
    assert bar.close == 151.00
    assert bar.volume == 1000000


def test_bardata_date_required():
    """Test that date is required (cannot be None)."""
    with pytest.raises(TypeError, match="date"):
        BarData(
            open=150.00,
            high=151.50,
            low=149.75,
            close=151.00,
            volume=1000000
        )


def test_bardata_date_explicitly_null():
    """Test that explicitly passing None for date is rejected."""
    with pytest.raises(TypeError, match="date must be a datetime"):
        BarData(
            date=None,
            open=150.00,
            high=151.50,
            low=149.75,
            close=151.00,
            volume=1000000
        )


def test_bardata_high_less_than_low():
    """Test that High < Low is rejected."""
    with pytest.raises(ValueError, match="High.*must be >= Low"):
        BarData(
            date=datetime(2026, 1, 2, 9, 30),
            open=150.00,
            high=149.00,  # High < Low - invalid
            low=149.75,
            close=150.50,
            volume=1000000
        )


def test_bardata_high_less_than_open():
    """Test that High < Open is rejected."""
    with pytest.raises(ValueError, match="High.*must be >= Open"):
        BarData(
            date=datetime(2026, 1, 2, 9, 30),
            open=151.00,
            high=150.00,  # High < Open - invalid
            low=149.75,
            close=150.50,
            volume=1000000
        )


def test_bardata_high_less_than_close():
    """Test that High < Close is rejected."""
    with pytest.raises(ValueError, match="High.*must be >= Close"):
        BarData(
            date=datetime(2026, 1, 2, 9, 30),
            open=150.00,
            high=150.50,  # High < Close - invalid
            low=149.75,
            close=151.00,
            volume=1000000
        )


def test_bardata_low_greater_than_open():
    """Test that Low > Open is rejected."""
    with pytest.raises(ValueError, match="Low.*must be <= Open"):
        BarData(
            date=datetime(2026, 1, 2, 9, 30),
            open=149.00,
            high=151.50,
            low=150.00,  # Low > Open - invalid
            close=150.50,
            volume=1000000
        )


def test_bardata_low_greater_than_close():
    """Test that Low > Close is rejected."""
    with pytest.raises(ValueError, match="Low.*must be <= Close"):
        BarData(
            date=datetime(2026, 1, 2, 9, 30),
            open=150.50,
            high=151.50,
            low=150.00,  # Low > Close - invalid
            close=149.75,
            volume=1000000
        )


def test_bardata_valid_edge_case_all_equal():
    """Test that all prices equal is valid (e.g., no movement)."""
    bar = BarData(
        date=datetime(2026, 1, 2, 9, 30),
        open=150.00,
        high=150.00,
        low=150.00,
        close=150.00,
        volume=100
    )
    assert bar.high == bar.low == bar.open == bar.close


def test_bardata_valid_edge_case_high_equals_open():
    """Test that High == Open is valid."""
    bar = BarData(
        date=datetime(2026, 1, 2, 9, 30),
        open=151.50,
        high=151.50,
        low=149.75,
        close=150.00,
        volume=1000
    )
    assert bar.high == bar.open


def test_bardata_valid_edge_case_low_equals_close():
    """Test that Low == Close is valid."""
    bar = BarData(
        date=datetime(2026, 1, 2, 9, 30),
        open=151.00,
        high=151.50,
        low=149.75,
        close=149.75,
        volume=1000
    )
    assert bar.low == bar.close


def _bar(**overrides) -> BarData:
    fields = dict(date=datetime(2026, 1, 2, 9, 30), open=150.0, high=151.5, low=149.75, close=151.0, volume=1000)
    fields.update(overrides)
    return BarData(**fields)


def test_bardata_uses_slots():
    """No per-instance __dict__ — the memory saving this type exists for."""
    bar = _bar()
    assert not hasattr(bar, "__dict__")
    with pytest.raises(AttributeError):
        bar.not_a_field = 1


def test_bardata_numeric_fields_are_stored_as_float():
    """Ints become floats, as under pydantic — CSV output depends on it."""
    bar = _bar(open=150, high=152, low=149, close=151, volume=1000)
    assert all(type(v) is float for v in (bar.open, bar.high, bar.low, bar.close, bar.volume))


def test_bardata_rejects_string_date():
    """No silent coercion of an ISO string, unlike pydantic."""
    with pytest.raises(TypeError, match="date must be a datetime"):
        _bar(date="2026-01-02T09:30:00")


def test_bardata_is_keyword_only():
    with pytest.raises(TypeError):
        BarData(datetime(2026, 1, 2, 9, 30), 150.0, 151.5, 149.75, 151.0, 1000)


def test_bardata_is_close_bar_is_mutable():
    """The backtest marks the session's last bar in place."""
    bar = _bar()
    bar.is_close_bar = True
    assert bar.is_close_bar is True


def test_bardata_replace_revalidates():
    """dataclasses.replace replaces model_copy and runs the same checks."""
    bar = _bar()
    moved = dataclasses.replace(bar, date=datetime(2026, 1, 2, 9, 35))
    assert moved.date == datetime(2026, 1, 2, 9, 35) and moved.close == bar.close
    with pytest.raises(ValueError, match="High.*must be >= Low"):
        dataclasses.replace(bar, high=100.0)


def test_bardata_equality_compares_fields():
    assert _bar() == _bar()
    assert _bar() != _bar(close=150.5)
