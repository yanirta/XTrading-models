from typing import Optional, ClassVar
from pydantic import BaseModel, Field, model_validator, field_validator


UNSET_DOUBLE = float('inf')
UNSET_INTEGER = 2**31 - 1


class Order(BaseModel):
    """Base order class for trading."""

    model_config = {
        'arbitrary_types_allowed': True,
        'validate_assignment': True,  # Validate on mutation
    }

    _next_order_id: ClassVar[int] = 1

    orderId: int = Field(default=0)
    permId: int = 0
    clientId: int = 0
    action: str = ''
    totalQuantity: float = 0.0
    orderType: str = ''
    price: float = Field(default=UNSET_DOUBLE, allow_inf_nan=True)
    tif: str = ''
    goodTillDate: str = ''
    goodAfterTime: str = ''
    ocaGroup: str = ''
    orderRef: str = ''
    parentId: int = UNSET_INTEGER
    transmit: bool = True
    children: list['Order'] = Field(default_factory=list)

    @field_validator('price', mode='before')
    @classmethod
    def allow_unset_price(cls, v):
        """Allow UNSET_DOUBLE sentinel value."""
        return v

    def model_post_init(self, __context) -> None:
        """Auto-assign orderId after initialization."""
        if self.orderId == 0:
            self.orderId = Order._next_order_id
            Order._next_order_id += 1

    def add_child(self, child: 'Order') -> None:
        """Add a child order and set its parentId."""
        child.parentId = self.orderId
        self.children.append(child)

class LimitOrder(Order):
    """Limit order."""

    @field_validator('price', mode='before')
    @classmethod
    def allow_unset_price(cls, v):
        """Allow UNSET_DOUBLE sentinel value."""
        return v

    def __init__(self, action: str, totalQuantity: float, price: float, **kwargs):
        super().__init__(
            orderType='LMT',
            action=action,
            totalQuantity=totalQuantity,
            price=price,
            **kwargs
        )

class MarketOrder(Order):
    """Market order."""

    def __init__(self, action: str, totalQuantity: float, **kwargs):
        super().__init__(
            orderType='MKT',
            action=action,
            totalQuantity=totalQuantity,
            **kwargs
        )

class StopOrder(Order):
    """Base class for all stop-triggered orders.

    All stop order types share:
    - triggered: whether the stop condition has been met
    - triggerPrice: the actual price at which the stop triggered (for debugging)
    """

    triggered: bool = False
    triggerPrice: Optional[float] = None

    def __init__(self, action: str, totalQuantity: float, stopPrice: float, **kwargs):
        kwargs.setdefault('orderType', 'STP')
        super().__init__(
            action=action,
            totalQuantity=totalQuantity,
            price=stopPrice,
            **kwargs
        )

class StopLimitOrder(StopOrder):
    """Stop limit order - triggers at stop price, then evaluates as limit."""

    limitPrice: float = UNSET_DOUBLE

    @field_validator('limitPrice', mode='before')
    @classmethod
    def allow_unset_limit_price(cls, v):
        """Allow UNSET_DOUBLE sentinel value."""
        return v

    def __init__(self, action: str, totalQuantity: float, limitPrice: float, stopPrice: float, **kwargs):
        super().__init__(
            action=action,
            totalQuantity=totalQuantity,
            stopPrice=stopPrice,
            orderType='STP LMT',
            limitPrice=limitPrice,
            **kwargs
        )

class TrailingOrder(StopOrder):
    """Base class for trailing orders."""

    trailingDistance: Optional[float] = None
    trailingPercent: Optional[float] = None
    stopPrice: Optional[float] = None
    extremePrice: Optional[float] = None

    @model_validator(mode='after')
    def validate_trailing_params(self):
        """Validate exactly one of trailingDistance or trailingPercent is set."""
        if (self.trailingDistance is None and self.trailingPercent is None) or \
           (self.trailingDistance is not None and self.trailingPercent is not None):
            raise ValueError("Exactly one of trailingDistance or trailingPercent must be specified")
        return self


    def __init__(self, orderType: str, action: str, totalQuantity: float, trailingDistance: Optional[float] = None, trailingPercent: Optional[float] = None, **kwargs):
        super().__init__(
            action=action,
            totalQuantity=totalQuantity,
            stopPrice=0.0,
            orderType=orderType,
            trailingDistance=trailingDistance, # type: ignore
            trailingPercent=trailingPercent, # type: ignore
            **kwargs
        )

class TrailingStopMarket(TrailingOrder):
    """Trailing stop market order with mutable state tracking.

    Tracks the extreme price and adjusts stop price as market moves favorably.
    When stop is hit, executes as a market order.

    Supports two modes (exactly one must be specified):
    - trailingDistance: Absolute trailing amount (e.g., trail by $2.00)
    - trailingPercent: Percentage trailing (e.g., trail by 2%)

    Attributes:
        trailingDistance: Absolute distance from extreme to stop (optional)
        trailingPercent: Percentage distance from extreme to stop (optional)
        stopPrice: Current stop trigger price (mutable)
        extremePrice: Best price seen so far (mutable)
    """
    def __init__(self, action: str, totalQuantity: float, trailingDistance: Optional[float] = None, trailingPercent: Optional[float] = None, **kwargs):
        super().__init__(
            orderType='TRAIL',
            action=action,
            totalQuantity=totalQuantity,
            trailingDistance=trailingDistance,
            trailingPercent=trailingPercent,
            **kwargs
        )

class TrailingStopLimit(TrailingOrder):
    """Trailing stop limit order with mutable state tracking.

    Similar to TrailingStopMarket but evaluates as a limit order when triggered.

    Supports two modes (exactly one must be specified):
    - trailingDistance: Absolute trailing amount (e.g., trail by $2.00)
    - trailingPercent: Percentage trailing (e.g., trail by 2%)

    Attributes:
        trailingDistance: Absolute distance from extreme to stop (optional)
        trailingPercent: Percentage distance from extreme to stop (optional)
        limitOffset: Distance from stop to limit price (always positive)
        stopPrice: Current stop trigger price (mutable)
        extremePrice: Best price seen so far (mutable)
    """

    limitOffset: float = 0.0

    def __init__(self, action: str, totalQuantity: float,
                 limitOffset: float,
                 trailingDistance: Optional[float] = None,
                 trailingPercent: Optional[float] = None,
                 **kwargs):
        super().__init__(
            orderType='TRAIL LIMIT',
            action=action,
            totalQuantity=totalQuantity,
            trailingDistance=trailingDistance,
            trailingPercent=trailingPercent,
            limitOffset=limitOffset,
            **kwargs
        )
