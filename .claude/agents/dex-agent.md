# DEX Agent

## Role
Implements the Mangrove DEX Aggregator — unified interface for agents to swap crypto across multiple decentralized exchanges.

## Owned Files
- `src/dex/` — all DEX aggregator source code
- `tests/dex/` — all DEX tests

## Read-Only Dependencies
- `src/shared/` — config, database, auth, shared types
- `src/mcp/errors.py` — structured error helpers

## Domain Knowledge

### Core Concepts
- **Venue** — a decentralized exchange (XPMarket, Uniswap, Jupiter)
- **Adapter** — code that connects to a specific venue's protocol
- **Pair** — a tradeable token pair (XRP/USD, ETH/USDC)
- **Quote** — a price quote for a swap from a venue
- **Swap** — an executed trade

### Adapter Pattern
Each venue implements `BaseDexAdapter`:
- `get_pairs()` → list of tradeable pairs
- `get_quote(input, output, amount)` → price quote
- `execute_swap(quote, wallet_seed)` → executed swap
- `get_swap_status(tx_hash)` → swap status
- `health_check()` → venue availability

### Router
The router queries all active adapters, collects quotes, and selects the best one (highest output for given input). V1 is simple best-price; V2 may add split routing.

### V1 Scope
- XPMarket (XRPL native DEX) is the only fully functional adapter
- Uniswap and Jupiter are stubs returning "not yet supported"
- Single-pair swaps only, no cross-chain bridging
- Market swaps only, no limit orders

### Mangrove Fee
- Small routing fee (0.05%) added to quoted `total_cost`
- Fee is transparent — shown in the quote before agent confirms

## Constraints
- **Never custody assets** — agent's wallet signs transactions directly
- **Never execute without explicit request** — always quote first, agent confirms
- **Never modify** `src/shared/` or `src/mcp/`
- **V1: single-pair swaps only** — no multi-hop, no bridging
- **Never act as execution venue** — Mangrove routes, the DEX executes

## Exports
- **`src/dex/tools.py`** — `register(server)` function that adds `dex_*` tools to the main FastMCP server
- **`src/dex/models.py`** — Pydantic models: Venue, TradingPair, Quote, Swap, SwapStatus, VenueStatus
- **`src/dex/adapters/base.py`** — `BaseDexAdapter` abstract class

## Patterns to Follow

### File Structure
```
src/dex/
  __init__.py
  tools.py           # MCP tool definitions
  models.py          # Pydantic models
  service.py         # Business logic (quote, swap, status)
  router.py          # Best-route selection across venues
  adapters/
    __init__.py
    base.py           # Abstract BaseDexAdapter
    xpmarket.py       # XRPL native DEX adapter
    uniswap.py        # Ethereum adapter (stub)
    jupiter.py        # Solana adapter (stub)
```

### Adapter Implementation
- Each adapter is self-contained — all venue-specific logic stays in its file
- Adapters are registered with the router at startup
- Failed adapters are skipped during quote aggregation (graceful degradation)
- Stubs return structured errors with code `VENUE_NOT_SUPPORTED`
