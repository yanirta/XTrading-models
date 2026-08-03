# CLAUDE.md — XTrading-models

Shared Pydantic-based trading models for the XTrading ecosystem. See `../CLAUDE.md` for workspace-wide conventions.

## Architecture

Models live in `src/xtrading_models/`. Orders are pure instructions (no status); parent-child via `add_child()` for bracket orders.

## Code Conventions

- File naming: singular nouns (`order.py` not `orders.py`)
