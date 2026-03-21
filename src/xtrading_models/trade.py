from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .order import Order
from .fill import Fill


class TradeStatus(str, Enum):
    PendingSubmit = 'PendingSubmit'
    PreSubmitted = 'PreSubmitted'
    Submitted = 'Submitted'
    Filled = 'Filled'
    Cancelled = 'Cancelled'
    Inactive = 'Inactive'


@dataclass
class OrderStatus:
    orderId: int = 0
    status: TradeStatus = TradeStatus.PendingSubmit
    filled: float = 0.0
    remaining: float = 0.0
    avgFillPrice: float = 0.0
    lastFillPrice: float = 0.0
    parentId: int = 0

    DoneStates = {TradeStatus.Filled, TradeStatus.Cancelled}
    ActiveStates = {TradeStatus.PendingSubmit, TradeStatus.Submitted}


@dataclass
class TradeLogEntry:
    time: datetime
    status: TradeStatus
    message: str = ''


@dataclass
class Trade:
    order: Order
    orderStatus: OrderStatus
    fills: list[Fill] = field(default_factory=list)
    log: list[TradeLogEntry] = field(default_factory=list)

    @property
    def is_done(self) -> bool:
        return self.orderStatus.status in OrderStatus.DoneStates

    @property
    def is_active(self) -> bool:
        return self.orderStatus.status in OrderStatus.ActiveStates
