from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class BarData(BaseModel):
    """OHLCV bar data (IB-compatible) with validation."""

    date: datetime
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    # average: float = 0.0
    # barCount: int = 0

    @field_validator('date')
    @classmethod
    def date_required(cls, v):
        if v is None:
            raise ValueError('date cannot be null')
        return v

    @model_validator(mode='after')
    def validate_ohlc(self):
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
        return self
