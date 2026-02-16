# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xtrading-models is a shared library of Pydantic-based trading models for the XTrading ecosystem. It provides order types, execution results, and market data structures compatible with Interactive Brokers conventions.

## Commands

```bash
pip install -e .           # Install in development mode
pip install -e ".[dev]"    # Install with dev dependencies (pytest)

# Tests
pytest tests/ -v                              # Run all tests
pytest tests/test_models.py -v                # Single test file
pytest tests/test_models.py::test_function -v # Single test
```

## Architecture

All models are in `src/xtrading_models/`:

- **`order.py`**: Order hierarchy - base `Order` class with `MarketOrder`, `LimitOrder`, `StopOrder`, `StopLimitOrder`, `TrailingStopMarket`, `TrailingStopLimit`. Orders are pure instructions (no status). Parent-child via `add_child()` reserved for bracket orders. Stop types have `triggered: bool` field for internal state tracking.
- **`trade.py`**: `Trade` (lifecycle wrapper: order + orderStatus + fills + log), `OrderStatus` (fill progress tracking), `TradeLogEntry` (timestamped status entries)
- **`bar.py`**: `BarData` - OHLCV candlestick representation
- **`fill.py`**: `Fill`, `Execution`, `CommissionReport` - execution result models

### Sentinels

Use `UNSET_DOUBLE` (Decimal infinity) and `UNSET_INTEGER` (2^31-1) for optional numeric fields rather than None.

## Code Conventions

### Financial Values
Use `decimal.Decimal` or `int` for all financial values. Never use `float` for prices.

### IB Compatibility
Models follow Interactive Brokers naming conventions with camelCase fields: `orderId`, `totalQuantity`, `lmtPrice`, `auxPrice`, `clientId`, `parentId`.

### File Naming
Singular nouns (`order.py` not `orders.py`).
