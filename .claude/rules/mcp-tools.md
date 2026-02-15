# MCP Tool Design Rules

## Naming Convention

All tools use a prefix that identifies the product area:

- `marketplace_*` — Marketplace operations (list, search, buy, sell, rate)
- `dex_*` — DEX aggregator operations (quote, swap, supported_pairs)
- `wallet_*` — Wallet management (create, balance, send, receive)
- `integration_*` — External service access (akash, fetch, bittensor, nodes)
- `metrics_*` — Market intelligence queries

## Tool Design Principles

- Each tool does one thing well
- Input parameters should be explicit — don't make the agent guess
- Return structured JSON that agents can parse programmatically
- Include clear descriptions so agent frameworks can understand when to use each tool
- Tools should be idempotent where possible

## Error Responses

Every tool error must include:
- `error`: boolean
- `code`: machine-readable error code
- `message`: human/agent-readable description
- `suggestion`: what the agent could do to fix it

## Tool Documentation

Every tool must have:
- A clear, one-line description
- Parameter descriptions with types and constraints
- Example input/output in the tool schema
