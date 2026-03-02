# CLAUDE.md — XTrading-models

Shared Pydantic-based trading models for the XTrading ecosystem. See `../CLAUDE.md` for workspace-wide conventions.

## Commands

```bash
pip install -e .
pip install -e ".[dev]"    # With dev dependencies (pytest)
pytest tests/ -v
```

## Architecture

All models are in `src/xtrading_models/`:

- **`order.py`**: Order hierarchy — base `Order` with `MarketOrder`, `LimitOrder`, `StopOrder`, `StopLimitOrder`, `TrailingStopMarket`, `TrailingStopLimit`. Orders are pure instructions (no status). Parent-child via `add_child()` for bracket orders. Stop types have `triggered: bool` for internal state tracking.
- **`trade.py`**: `Trade` (lifecycle wrapper: order + orderStatus + fills + log), `OrderStatus`, `TradeLogEntry`
- **`bar.py`**: `BarData` — OHLCV candlestick representation
- **`fill.py`**: `Fill`, `Execution`, `CommissionReport` — execution result models

## Code Conventions

- File naming: singular nouns (`order.py` not `orders.py`)
