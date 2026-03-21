from importlib.metadata import version
__version__ = version("xtrading-models")

from .order import (
    Order, LimitOrder, MarketOrder, MarketOnCloseOrder, StopOrder, StopLimitOrder,
    TrailingOrder, TrailingStopMarket, TrailingStopLimit,
    UNSET_DOUBLE, UNSET_INTEGER
)
from .bar import BarData
from .fill import Execution, CommissionReport, Fill
from .trade import OrderStatus, Trade, TradeLogEntry, TradeStatus
from .time_provider import TimeProvider

__all__ = [
    # Orders
    'Order', 'LimitOrder', 'MarketOrder', 'MarketOnCloseOrder', 'StopOrder', 'StopLimitOrder',
    'TrailingOrder', 'TrailingStopMarket', 'TrailingStopLimit',
    # Sentinels
    'UNSET_DOUBLE', 'UNSET_INTEGER',
    # Bar
    'BarData',
    # Fill
    'Execution', 'CommissionReport', 'Fill',
    # Trade lifecycle
    'OrderStatus', 'Trade', 'TradeLogEntry', 'TradeStatus',
    # Time
    'TimeProvider',
]
