from datetime import datetime
import pytest
from xtrading_models import (
    Order, LimitOrder, MarketOrder, StopOrder, StopLimitOrder,
    TrailingStopMarket, TrailingStopLimit,
    OrderStatus, Trade, TradeLogEntry,
    Execution, CommissionReport, Fill,
)
from xtrading_models.order import UNSET_DOUBLE

# region Base Order Tests
def test_base_order():
    """Test creating a base order with manual field population."""
    order = Order(
        action='BUY',
        totalQuantity=100,
        orderType='LMT',
        price=150.25
    )

    assert order.orderId > 0  # Auto-assigned
    assert order.action == 'BUY'
    assert order.totalQuantity == 100
    assert order.orderType == 'LMT'
    assert order.price == 150.25
    assert hasattr(order, 'children')
    assert order.children == []

def test_order_id_auto_increment():
    """Test that orderId is automatically assigned and increments."""
    order1 = Order(action='BUY', totalQuantity=100, orderType='LMT')
    order2 = Order(action='SELL', totalQuantity=50, orderType='LMT')
    order3 = Order(action='BUY', totalQuantity=25, orderType='MKT')

    # Each order should have unique, incrementing IDs
    assert order1.orderId > 0
    assert order2.orderId > order1.orderId
    assert order3.orderId > order2.orderId
    assert order2.orderId == order1.orderId + 1
    assert order3.orderId == order2.orderId + 1

def test_base_order_children_not_shared():
    """Test that children lists are not shared between Order instances."""
    order1 = Order(action='BUY', totalQuantity=100, orderType='LMT')
    order2 = Order(action='SELL', totalQuantity=50, orderType='LMT')

    child1 = Order(action='BUY', totalQuantity=25, orderType='MKT')
    child2 = Order(action='SELL', totalQuantity=30, orderType='MKT')

    order1.add_child(child1)
    child1.add_child(child2)

    # Verify parent-child relationships
    assert child1.parentId == order1.orderId
    assert child2.parentId == child1.orderId

    # Each order should have only its own child
    assert len(order1.children) == 1
    assert len(child1.children) == 1
    assert len(order2.children) == 0
    assert order1.children[0] is child1
    assert child1.children[0] is child2
    # Lists should not be shared
    assert order1.children is not order2.children

# endregion

# region simple orders
def test_limit_order():
    """Test creating a limit order."""
    order = LimitOrder(
        action='BUY',
        totalQuantity=100,
        price=150.25
    )

    assert order.orderId > 0
    assert order.action == 'BUY'
    assert order.totalQuantity == 100
    assert order.price == 150.25
    assert order.orderType == 'LMT'

def test_market_order():
    """Test creating a market order."""
    order = MarketOrder(
        action='SELL',
        totalQuantity=50
    )

    assert order.orderId > 0
    assert order.action == 'SELL'
    assert order.totalQuantity == 50
    assert order.orderType == 'MKT'

# endregion

#region composit orders
def test_stop_order():
    """Test creating a stop order."""
    order = StopOrder(
        action='SELL',
        totalQuantity=100,
        stopPrice=145.00
    )

    assert order.orderId > 0
    assert order.action == 'SELL'
    assert order.price == 145.00  # Stop price
    assert order.orderType == 'STP'
    assert order.triggered is False
    assert len(order.children) == 0

def test_stop_limit_order():
    """Test creating a stop limit order."""
    order = StopLimitOrder(
        action='BUY',
        totalQuantity=100,
        limitPrice=150.50,
        stopPrice=150.00
    )

    assert order.orderId > 0
    assert order.price == 150.00  # Stop price
    assert order.limitPrice == 150.50  # Limit price
    assert order.orderType == 'STP LMT'
    assert order.triggered is False
    assert len(order.children) == 0

# region Child Orders Tests
def test_order_add_multiple_children():
    """Test parent can have multiple children."""
    #TODO when adding children to StopOrder/StopLimitOrder, it should go to the child, not parent

    # Use base Order to avoid internal children from StopOrder/StopLimitOrder
    parent = Order(action='BUY', totalQuantity=100, orderType='LMT', price=150.00)
    child1 = LimitOrder('SELL', 100, 155.00)
    child2 = LimitOrder('SELL', 100, 145.00)

    parent.add_child(child1)
    parent.add_child(child2)

    assert child1.parentId == parent.orderId
    assert child2.parentId == parent.orderId
    assert len(parent.children) == 2
    assert parent.children[0] is child1
    assert parent.children[1] is child2
# endregion

# region Trailing Stop Orders Tests
def test_trailing_stop_market_creation_with_amount():
    """Test creating a TrailingStopMarket order with absolute amount."""
    order = TrailingStopMarket(
        action='BUY',
        totalQuantity=100,
        trailingDistance=2.00
    )

    assert order.orderId > 0
    assert order.action == 'BUY'
    assert order.totalQuantity == 100
    assert order.orderType == 'TRAIL'
    assert order.trailingDistance == 2.00
    assert order.trailingPercent is None
    # State should be uninitialized
    assert order.stopPrice is None
    assert order.extremePrice is None
    assert len(order.children) == 0


def test_trailing_stop_market_creation_with_percent():
    """Test creating a TrailingStopMarket order with percentage."""
    order = TrailingStopMarket(
        action='SELL',
        totalQuantity=50,
        trailingPercent=2.5
    )

    assert order.orderId > 0
    assert order.action == 'SELL'
    assert order.totalQuantity == 50
    assert order.orderType == 'TRAIL'
    assert order.trailingDistance is None
    assert order.trailingPercent == 2.5
    assert order.stopPrice is None
    assert order.extremePrice is None
    assert len(order.children) == 0


def test_trailing_stop_market_requires_one_parameter():
    """Test that TrailingStopMarket requires exactly one of trailingDistance or trailingPercent."""
    # Neither parameter - should raise
    with pytest.raises(ValueError, match="Exactly one"):
        TrailingStopMarket(action='BUY', totalQuantity=100)

    # Both parameters - should raise
    with pytest.raises(ValueError, match="Exactly one"):
        TrailingStopMarket(
            action='BUY',
            totalQuantity=100,
            trailingDistance=2.00,
            trailingPercent=2.5
        )


def test_trailing_stop_market_only_distance_allowed():
    """Test that TrailingStopMarket works with only trailingDistance."""
    order = TrailingStopMarket(
        action='BUY',
        totalQuantity=100,
        trailingDistance=1.50
    )
    assert order.trailingDistance == 1.50
    assert order.trailingPercent is None


def test_trailing_stop_market_only_percent_allowed():
    """Test that TrailingStopMarket works with only trailingPercent."""
    order = TrailingStopMarket(
        action='SELL',
        totalQuantity=100,
        trailingPercent=3.5
    )
    assert order.trailingDistance is None
    assert order.trailingPercent == 3.5


def test_trailing_stop_market_both_raises_error():
    """Test that providing both trailingDistance and trailingPercent raises ValueError."""
    with pytest.raises(ValueError, match="Exactly one of trailingDistance or trailingPercent"):
        TrailingStopMarket(
            action='BUY',
            totalQuantity=100,
            trailingDistance=2.00,
            trailingPercent=2.0
        )


def test_trailing_stop_market_neither_raises_error():
    """Test that providing neither trailingDistance nor trailingPercent raises ValueError."""
    with pytest.raises(ValueError, match="Exactly one of trailingDistance or trailingPercent"):
        TrailingStopMarket(action='BUY', totalQuantity=100)


def test_trailing_stop_market_state_mutability():
    """Test that trailing stop state can be mutated during execution."""
    order = TrailingStopMarket(
        action='SELL',
        totalQuantity=50,
        trailingDistance=1.50
    )

    # Simulate state initialization
    order.extremePrice = 100.00
    order.stopPrice = 98.50  # extremePrice - trailingDistance

    assert order.extremePrice == 100.00
    assert order.stopPrice == 98.50

    # Simulate state update (price moved higher)
    order.extremePrice = 101.00
    order.stopPrice = 99.50

    assert order.extremePrice == 101.00
    assert order.stopPrice == 99.50


def test_trailing_stop_limit_creation_with_amount():
    """Test creating a TrailingStopLimit order with absolute amount."""
    order = TrailingStopLimit(
        action='BUY',
        totalQuantity=100,
        trailingDistance=2.00,
        limitOffset=0.50
    )

    assert order.orderId > 0
    assert order.action == 'BUY'
    assert order.totalQuantity == 100
    assert order.orderType == 'TRAIL LIMIT'
    assert order.trailingDistance == 2.00
    assert order.trailingPercent is None
    assert order.limitOffset == 0.50
    # State should be uninitialized
    assert order.stopPrice is None
    assert order.extremePrice is None
    assert len(order.children) == 0


def test_trailing_stop_limit_creation_with_percent():
    """Test creating a TrailingStopLimit order with percentage."""
    order = TrailingStopLimit(
        action='SELL',
        totalQuantity=50,
        trailingPercent=1.5,
        limitOffset=0.25
    )

    assert order.orderId > 0
    assert order.action == 'SELL'
    assert order.totalQuantity == 50
    assert order.orderType == 'TRAIL LIMIT'
    assert order.trailingDistance is None
    assert order.trailingPercent == 1.5
    assert order.limitOffset == 0.25
    assert order.stopPrice is None
    assert order.extremePrice is None
    assert len(order.children) == 0


def test_trailing_stop_limit_requires_one_parameter():
    """Test that TrailingStopLimit requires exactly one of trailingDistance or trailingPercent."""
    # Neither parameter - should raise
    with pytest.raises(ValueError, match="Exactly one"):
        TrailingStopLimit(
            action='BUY',
            totalQuantity=100,
            limitOffset=0.50
        )

    # Both parameters - should raise
    with pytest.raises(ValueError, match="Exactly one"):
        TrailingStopLimit(
            action='BUY',
            totalQuantity=100,
            limitOffset=0.50,
            trailingDistance=2.00,
            trailingPercent=2.5
        )


def test_trailing_stop_limit_only_distance_allowed():
    """Test that TrailingStopLimit works with only trailingDistance."""
    order = TrailingStopLimit(
        action='BUY',
        totalQuantity=100,
        trailingDistance=1.50,
        limitOffset=0.25
    )
    assert order.trailingDistance == 1.50
    assert order.trailingPercent is None
    assert order.limitOffset == 0.25


def test_trailing_stop_limit_only_percent_allowed():
    """Test that TrailingStopLimit works with only trailingPercent."""
    order = TrailingStopLimit(
        action='SELL',
        totalQuantity=100,
        trailingPercent=3.5,
        limitOffset=0.50
    )
    assert order.trailingDistance is None
    assert order.trailingPercent == 3.5
    assert order.limitOffset == 0.50


def test_trailing_stop_limit_both_raises_error():
    """Test that providing both trailingDistance and trailingPercent raises ValueError."""
    with pytest.raises(ValueError, match="Exactly one of trailingDistance or trailingPercent"):
        TrailingStopLimit(
            action='BUY',
            totalQuantity=100,
            limitOffset=0.50,
            trailingDistance=2.00,
            trailingPercent=2.0
        )


def test_trailing_stop_limit_neither_raises_error():
    """Test that providing neither trailingDistance nor trailingPercent raises ValueError."""
    with pytest.raises(ValueError, match="Exactly one of trailingDistance or trailingPercent"):
        TrailingStopLimit(
            action='BUY',
            totalQuantity=100,
            limitOffset=0.50
        )


def test_trailing_stop_limit_state_mutability():
    """Test that trailing stop limit state can be mutated during execution."""
    order = TrailingStopLimit(
        action='SELL',
        totalQuantity=50,
        trailingDistance=1.50,
        limitOffset=0.25
    )

    # Simulate state initialization
    order.extremePrice = 100.00
    order.stopPrice = 98.50  # extremePrice - trailingDistance

    assert order.extremePrice == 100.00
    assert order.stopPrice == 98.50

    # Simulate state update
    order.extremePrice = 102.00
    order.stopPrice = 100.50

    assert order.extremePrice == 102.00
    assert order.stopPrice == 100.50


def test_trailing_stop_market_buy_vs_sell():
    """Test TrailingStopMarket for both BUY and SELL actions."""
    buy_order = TrailingStopMarket(
        action='BUY',
        totalQuantity=100,
        trailingDistance=1.00
    )

    sell_order = TrailingStopMarket(
        action='SELL',
        totalQuantity=100,
        trailingDistance=1.00
    )

    assert buy_order.action == 'BUY'
    assert sell_order.action == 'SELL'
    assert buy_order.trailingDistance == sell_order.trailingDistance
    assert buy_order.orderType == sell_order.orderType == 'TRAIL'


def test_trailing_stop_limit_buy_vs_sell():
    """Test TrailingStopLimit for both BUY and SELL actions."""
    buy_order = TrailingStopLimit(
        action='BUY',
        totalQuantity=100,
        trailingDistance=1.00,
        limitOffset=0.25
    )

    sell_order = TrailingStopLimit(
        action='SELL',
        totalQuantity=100,
        trailingDistance=1.00,
        limitOffset=0.25
    )

    assert buy_order.action == 'BUY'
    assert sell_order.action == 'SELL'
    assert buy_order.trailingDistance == sell_order.trailingDistance
    assert buy_order.limitOffset == sell_order.limitOffset
    assert buy_order.orderType == sell_order.orderType == 'TRAIL LIMIT'


def test_trailing_stop_orders_unique_ids():
    """Test that trailing stop orders get unique auto-incremented IDs."""
    order1 = TrailingStopMarket('BUY', 100, trailingDistance=1.00)
    order2 = TrailingStopLimit('SELL', 50, trailingDistance=2.00, limitOffset=0.50)
    order3 = TrailingStopMarket('SELL', 75, trailingPercent=1.50)

    # All orders should have unique IDs
    assert order1.orderId > 0
    assert order2.orderId > order1.orderId
    assert order3.orderId > order2.orderId
    assert len(order1.children) == 0
    assert len(order2.children) == 0
    assert len(order3.children) == 0


def test_trailing_stop_fields_are_instance_vars():
    """Test that trailingDistance, trailingPercent, etc. are instance variables, not class variables."""
    order1 = TrailingStopMarket('BUY', 100, trailingDistance=1.00)
    order2 = TrailingStopMarket('BUY', 100, trailingDistance=2.00)

    # Each instance should have its own trailingDistance
    assert order1.trailingDistance == 1.00
    assert order2.trailingDistance == 2.00
    assert order1.trailingPercent is None
    assert order2.trailingPercent is None

    # Mutate state on order1
    order1.stopPrice = 100.00
    order1.extremePrice = 101.00

    # order2 should not be affected
    assert order2.stopPrice is None
    assert order2.extremePrice is None

    # Mutate state on order2
    order2.stopPrice = 200.00
    order2.extremePrice = 202.00

    # order1 should retain its own values
    assert order1.stopPrice == 100.00
    assert order1.extremePrice == 101.00


def test_trailing_stop_limit_fields_are_instance_vars():
    """Test that TrailingStopLimit fields are instance variables."""
    order1 = TrailingStopLimit('SELL', 50, trailingDistance=1.50, limitOffset=0.25)
    order2 = TrailingStopLimit('SELL', 50, trailingPercent=2.5, limitOffset=0.50)

    # Each instance should have its own parameters
    assert order1.trailingDistance == 1.50
    assert order1.trailingPercent is None
    assert order1.limitOffset == 0.25

    assert order2.trailingDistance is None
    assert order2.trailingPercent == 2.5
    assert order2.limitOffset == 0.50

    # Mutate state independently
    order1.stopPrice = 98.50
    order1.extremePrice = 100.00

    order2.stopPrice = 195.00
    order2.extremePrice = 200.00

    # Verify no cross-contamination
    assert order1.stopPrice == 98.50
    assert order1.extremePrice == 100.00
    assert order2.stopPrice == 195.00
    assert order2.extremePrice == 200.00
# endregion

# region Trade Lifecycle Tests
def test_order_status_defaults():
    """Test OrderStatus default values."""
    status = OrderStatus()
    assert status.status == 'PendingSubmit'
    assert status.filled == 0.0
    assert status.remaining == 0.0
    assert status.avgFillPrice == 0.0
    assert status.lastFillPrice == 0.0

def test_order_status_done_states():
    """Test DoneStates and ActiveStates sets."""
    assert 'Filled' in OrderStatus.DoneStates
    assert 'Cancelled' in OrderStatus.DoneStates
    assert 'Submitted' in OrderStatus.ActiveStates
    assert 'PendingSubmit' in OrderStatus.ActiveStates

def test_trade_creation():
    """Test creating a Trade with order and status."""
    order = LimitOrder(action='BUY', totalQuantity=100, price=150.0)
    status = OrderStatus(
        orderId=order.orderId,
        status='Submitted',
        remaining=100.0
    )
    trade = Trade(order=order, orderStatus=status)

    assert trade.order is order
    assert trade.orderStatus.status == 'Submitted'
    assert trade.fills == []
    assert trade.log == []
    assert trade.is_active is True
    assert trade.is_done is False

def test_trade_is_done():
    """Test Trade.is_done property."""
    order = MarketOrder(action='BUY', totalQuantity=100)
    trade = Trade(
        order=order,
        orderStatus=OrderStatus(orderId=order.orderId, status='Filled')
    )
    assert trade.is_done is True
    assert trade.is_active is False

def test_trade_log_entry():
    """Test TradeLogEntry creation."""
    entry = TradeLogEntry(
        time=datetime(2024, 1, 15, 9, 30),
        status='Submitted',
        message='Order submitted'
    )
    assert entry.status == 'Submitted'
    assert entry.message == 'Order submitted'

def test_trade_fill_tracking():
    """Test appending fills to a Trade."""
    order = LimitOrder(action='BUY', totalQuantity=100, price=150.0)
    trade = Trade(
        order=order,
        orderStatus=OrderStatus(orderId=order.orderId, status='Submitted', remaining=100.0)
    )

    execution = Execution(orderId=order.orderId, time=datetime(2024, 1, 15, 9, 30),
                          shares=100, price=150.0, side='BUY')
    commission = CommissionReport(commission=1.00, currency='USD')
    fill = Fill(order=order, execution=execution, commissionReport=commission,
                time=datetime(2024, 1, 15, 9, 30))

    trade.fills.append(fill)
    trade.orderStatus.status = 'Filled'
    trade.orderStatus.filled = 100.0
    trade.orderStatus.remaining = 0.0

    assert len(trade.fills) == 1
    assert trade.is_done is True

def test_stop_order_triggered_field():
    """Test that StopOrder has triggered field."""
    order = StopOrder(action='BUY', totalQuantity=100, stopPrice=105.0)
    assert order.triggered is False
    order.triggered = True
    assert order.triggered is True

def test_stop_limit_order_limit_price_field():
    """Test that StopLimitOrder stores limitPrice as a field."""
    order = StopLimitOrder(action='BUY', totalQuantity=100,
                           limitPrice=150.50, stopPrice=150.00)
    assert order.limitPrice == 150.50
    assert order.price == 150.00
    assert order.triggered is False
# endregion
