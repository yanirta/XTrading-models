# CLAUDE.md — XTrading-models

Shared trading models for the XTrading ecosystem — Pydantic models, except `BarData`, which is a `slots` dataclass for memory and speed (see README). See `../CLAUDE.md` for workspace-wide conventions.

## Architecture

Models live in `src/xtrading_models/`. Orders are pure instructions (no status); parent-child via `add_child()` for bracket orders.

## Code Conventions

- File naming: singular nouns (`order.py` not `orders.py`)
