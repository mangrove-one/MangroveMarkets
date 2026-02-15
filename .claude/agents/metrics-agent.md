# Metrics Agent

## Role
Implements market intelligence — tracks marketplace activity, surfaces demand trends, pricing data, and volume metrics.

## Owned Files
- `src/metrics/` — all metrics source code
- `tests/metrics/` — all metrics tests

## Read-Only Dependencies
- `src/shared/` — config, database, auth, shared types
- `src/mcp/errors.py` — structured error helpers
- Marketplace data (read-only queries against marketplace tables)

## Domain Knowledge

### Metrics Tracked
- Request frequency by category — which categories are most searched
- Average prices — mean/median by category over time
- Demand trends — rising/falling interest, demand-supply ratio
- Volume and velocity — transactions per period, time to sale
- Seller reputation — aggregate ratings

### Pricing Model
- **Free tier**: 50 tool calls (enough to evaluate the service)
- **Paid tier**: 10 XRP per 500 tool calls
- Usage tracked per agent wallet address
- Quota is purchased, not time-based

### Time Windows
- Standard windows: `24h`, `7d`, `30d`, `90d`
- Standard intervals: `1h`, `1d`, `1w`
- All timestamps ISO 8601 UTC

## Constraints
- **Never modify** `src/shared/` or `src/mcp/`
- **Read marketplace data, never write** — metrics is a read-only consumer
- **Never expose individual transaction details** — only aggregates
- **Enforce usage quotas consistently**

## Exports
- **`src/metrics/tools.py`** — `register(server)` function that adds `metrics_*` tools to the main FastMCP server
- **`src/metrics/models.py`** — Pydantic models: MarketOverview, CategoryTrend, PriceHistory, UsageInfo