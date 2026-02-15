# Coding conventions

This document defines the coding standards for the MangroveMarkets project. All contributors -- human and agent -- should follow these conventions.

## Python style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Maximum line length: 100 characters.
- Use 4 spaces for indentation. No tabs.
- Type hints are **required** on all function signatures (parameters and return types).
- Use [Pydantic v2](https://docs.pydantic.dev/latest/) for data models, especially at API and MCP tool boundaries.

## Naming conventions

| Element                  | Convention           | Example                      |
|--------------------------|----------------------|------------------------------|
| Functions and variables  | `snake_case`         | `get_listing`, `total_price` |
| Classes                  | `PascalCase`         | `ListingService`, `DexQuote` |
| Constants                | `UPPER_SNAKE_CASE`   | `MAX_RETRIES`, `BASE_RESERVE_XRP` |
| Python modules (files)   | `snake_case`         | `listing_service.py`, `dex_adapter.py` |
| Non-Python files         | `lowercase-hyphens`  | `pull-request-template.md`, `docker-compose.yml` |

## Imports

Order imports in three groups, separated by a blank line:

1. Standard library
2. Third-party packages
3. Local project modules

Rules:
- No wildcard imports (`from module import *`).
- Use absolute imports from `src` (e.g., `from src.marketplace.listing_service import ListingService`).
- Sort imports alphabetically within each group.

```python
import asyncio
import os
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel
import xrpl

from src.marketplace.listing_service import ListingService
from src.shared.errors import ToolError
```

## Error handling

All MCP tool errors must return a structured error dictionary:

```python
{
    "error": True,
    "code": "INSUFFICIENT_BALANCE",
    "message": "Insufficient XRP balance: have 5.0, need 10.0",
    "suggestion": "Fund the wallet with at least 5.0 additional XRP before retrying."
}
```

Fields:
- `error` (bool): Always `True` for errors.
- `code` (str): Machine-readable error code in `UPPER_SNAKE_CASE`.
- `message` (str): Descriptive message with specific values. Agents read these.
- `suggestion` (str): Actionable next step the caller can take.

Rules:
- No silent failures. If something goes wrong, return an error.
- Include concrete values in messages ("have 5, need 10" not "insufficient balance").
- Use exceptions internally but convert to structured errors at the MCP tool boundary.

## Testing

- Framework: [pytest](https://docs.pytest.org/).
- Test directory structure mirrors source: `src/marketplace/listing_service.py` maps to `tests/marketplace/test_listing_service.py`.
- Test files are named `test_*.py`.
- Shared fixtures go in `conftest.py` at the appropriate directory level.
- Tests should be independent and not rely on execution order.
- Use `pytest-asyncio` for async test functions.

```
src/
  marketplace/
    listing_service.py
  dex/
    adapter.py
tests/
  marketplace/
    test_listing_service.py
  dex/
    test_adapter.py
  conftest.py
```

## Type hints

Type hints are required, not optional.

- Use lowercase generic types: `list[str]`, `dict[str, int]`, `tuple[int, ...]`.
- Use `Optional[X]` (from `typing`) or `X | None` for nullable types.
- Use Pydantic models for structured data at API and tool boundaries.
- Use `TypeAlias` for complex type expressions that appear more than once.

```python
from typing import Optional

from pydantic import BaseModel


class Listing(BaseModel):
    listing_id: str
    title: str
    category: str
    price_xrp: float
    seller_address: str
    description: Optional[str] = None


async def search_listings(
    category: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
) -> list[Listing]:
    ...
```

## Docstrings

Use [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) docstrings.

- Required for all public functions and classes.
- Not required for obvious helper functions, test functions, or single-line lambdas.
- Include `Args`, `Returns`, and `Raises` sections where applicable.

```python
async def create_escrow(
    sender: str,
    receiver: str,
    amount_xrp: float,
    condition: str,
) -> dict:
    """Create an XRPL escrow for a marketplace transaction.

    Locks the specified amount of XRP in escrow until the fulfillment
    condition is met or the escrow expires.

    Args:
        sender: XRPL address of the buyer.
        receiver: XRPL address of the seller.
        amount_xrp: Amount of XRP to lock in escrow.
        condition: Crypto-condition for escrow release.

    Returns:
        Transaction result dict with escrow sequence number and status.

    Raises:
        InsufficientBalanceError: If sender lacks sufficient XRP.
        XRPLConnectionError: If the XRPL node is unreachable.
    """
    ...
```

## Dependencies

- Pin all dependency versions in `requirements.txt` (e.g., `xrpl-py==3.0.0`, not `xrpl-py>=3`).
- Minimize external dependencies. Prefer standard library where reasonable.
- Vet new dependencies for maintenance status, security, and license compatibility before adding.

## MCP tool conventions

Tools are the interface agents use to interact with MangroveMarkets. Design them carefully.

### Naming

All tools use a domain prefix:

| Prefix          | Domain                                  |
|-----------------|------------------------------------------|
| `marketplace_*` | Marketplace operations                   |
| `dex_*`         | DEX aggregator operations                |
| `wallet_*`      | Wallet management                        |
| `integration_*` | External service access (Akash, etc.)    |
| `metrics_*`     | Market intelligence queries              |

### Design rules

- One tool does one thing. `marketplace_search` searches. `marketplace_buy` buys. Do not combine.
- Input parameters must be explicit with clear names, types, and descriptions.
- Return structured JSON that agents can parse programmatically.
- Every tool must include a clear, one-line description in its schema.
- Tools should be idempotent where possible.
- Errors follow the structured error format defined above.

## Async

- Use `async`/`await` for all I/O operations: XRPL transactions, HTTP requests, database queries, file reads from decentralized storage.
- FastMCP tools are async by default. Define tool handlers as `async def`.
- Use `asyncio.gather` for concurrent independent operations.
- Do not mix blocking I/O with async code. Use `asyncio.to_thread` if you must call a blocking function from async context.

```python
@mcp.tool()
async def marketplace_search(category: str, limit: int = 20) -> list[dict]:
    """Search marketplace listings by category."""
    results = await listing_service.search(category=category, limit=limit)
    return [r.model_dump() for r in results]
```
