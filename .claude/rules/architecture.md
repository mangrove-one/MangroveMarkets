# Architecture Rules

## Two Products, Separate Concerns

The Mangrove Marketplace and the Mangrove DEX Aggregator are distinct products with separate backends. Do not conflate them. Code, tools, and logic for each should be cleanly separated.

- Marketplace code: `src/marketplace/`
- DEX Aggregator code: `src/dex/`
- Shared utilities: `src/shared/`
- MCP server (unified entry): `src/mcp/`

## XRPL Is the Settlement Layer for the Marketplace

All marketplace transactions settle in XRP via XRPL. Use native XRPL features (escrow, trustlines, DEX) before building custom alternatives.

## DEX Aggregator Is Multi-Chain

The DEX aggregator supports multiple chains. Each chain has its own adapter. The agent-facing interface is chain-agnostic — the agent says what they want, Mangrove routes it.

## MCP Server Is the Interface

Everything an agent does goes through the MCP server. Tools are the API. Name them with clear prefixes: `marketplace_*`, `dex_*`, `wallet_*`, `integration_*`.

## Mangrove Does Not Intermediate Integrations

For Akash, Fetch.ai, Bittensor, Nodes.ai — Mangrove provides tools for the agent to interact directly. Mangrove does not proxy, broker, or resell.
