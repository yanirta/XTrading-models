from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class BarData:
    """OHLCV bar data (IB-compatible) with validation.

    A slots dataclass rather than a pydantic model: a backtest builds millions of
    these, and pydantic costs ~11x the memory (~1080 vs ~96 bytes per bar) and
    ~3.5x the construction time for the same fields and checks. The contract is
    unchanged — keyword-only construction, numeric fields stored as float,
    `is_close_bar` mutable, the same OHLC rules and messages. Invalid input
    raises `ValueError` (OHLC rules) or `TypeError` (a missing or non-datetime
    `date`) instead of pydantic's `ValidationError`.
    """

    date: datetime
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    is_close_bar: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.date, datetime):
            raise TypeError(f"date must be a datetime, got {type(self.date).__name__}")
        # Store numbers as float, as the pydantic model did: an int volume would
        # otherwise round-trip through CSV as "1000" instead of "1000.0".
        self.open = float(self.open)
        self.high = float(self.high)
        self.low = float(self.low)
        self.close = float(self.close)
        self.volume = float(self.volume)
        self._validate_ohlc()

    def _validate_ohlc(self) -> None:
        """Validate OHLC relationships: High >= all, Low <= all."""
        if self.high < self.low:
            raise ValueError(f'High ({self.high}) must be >= Low ({self.low})')
        if self.high < self.open:
            raise ValueError(f'High ({self.high}) must be >= Open ({self.open})')
        if self.high < self.close:
            raise ValueError(f'High ({self.high}) must be >= Close ({self.close})')
        if self.low > self.open:
            raise ValueError(f'Low ({self.low}) must be <= Open ({self.open})')
        if self.low > self.close:
            raise ValueError(f'Low ({self.low}) must be <= Close ({self.close})')
