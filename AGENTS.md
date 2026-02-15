# AGENTS.md

> This file defines the conventions, guidelines, and context for any AI agent working on the MangroveMarkets project.

## Project Overview

MangroveMarkets is an open, decentralized marketplace built for AI agents — not humans. Agents are the first-class participants. They buy, sell, and trade information, compute, digital resources, and crypto assets through MangroveMarkets.

## File Conventions

- No all-caps markdown filenames except `README.md` and this file (`AGENTS.md`)
- There is only ever one `AGENTS.md`, and it lives in the project root
- Documentation lives in `docs/`
- Python modules use `snake_case.py`; non-Python files use `lowercase-hyphens`
- See `docs/conventions.md` for full coding conventions

## Architecture — Two Distinct Products

### 1. The Mangrove Marketplace
An agent-to-agent bulletin board (like eBay for agents) where agents list, discover, and transact digital goods and services. Settlement is in XRP on the XRPL. Mangrove facilitates discovery, escrow, and delivery — not execution.

### 2. The Mangrove DEX Aggregator
A unified interface for agents to trade crypto across multiple decentralized exchanges (XPMarket, Uniswap, Jupiter, etc.). Mangrove is not the execution venue — it routes to the right DEX and provides a single clean interface.

## Delivery Mechanism

MangroveMarkets is delivered to agents as:
- An **MCP server** (the protocol interface)
- **Skills and tools** (actionable capabilities agents invoke via MCP tool calls)

## Key Principles

- Agents are the users, not humans
- Open marketplace — no gatekeeping
- Money (XRP, crypto) is a means to an end, not the end itself
- Mangrove does not sit in the middle of external integrations (Akash, Fetch.ai, etc.) — it provides tools for agents to access those services directly
- Start simple, build iteratively

## Tech Stack

- **Language**: Python 3.11+
- **MCP server**: FastMCP (Python SDK)
- **Web framework**: Flask (health checks, admin)
- **XRPL client**: xrpl-py
- **Data models**: Pydantic v2
- **Settlement layer**: XRPL (XRP Ledger)
- **Decentralized storage**: IPFS / Arweave / Filecoin
- **Database**: PostgreSQL
- **Deployment**: GCP Cloud Run, Terraform

## Revenue Model

- Thin transaction fee on marketplace escrow settlements
- Routing fee on DEX aggregator swaps
- Market intelligence: 10 XRP per 500 tool calls (with a free teaser tier)
- Integration tools (Akash, Fetch.ai, Bittensor, Nodes.ai): Free — drives adoption

## Project Structure

```
src/
  app.py              # Flask + MCP entrypoint
  marketplace/         # Product 1: Marketplace
  dex/                 # Product 2: DEX Aggregator
  wallet/              # Wallet management
  integrations/        # External service tools
  metrics/             # Market intelligence
  mcp/                 # Unified MCP server
  shared/              # Shared utilities (config, db, auth, types)
tests/                 # Mirrors src/ structure
docs/                  # Vision, specification, implementation plan, conventions
infra/                 # Terraform IaC
.claude/agents/        # Subagent definitions
```

## Development with Subagents

MangroveMarkets is designed for parallel development using Claude Code subagents. Each domain has a specialist agent defined in `.claude/agents/`.

### Domain Ownership

| Agent | Domain | Owned Files | Can Read (not modify) |
|-------|--------|-------------|----------------------|
| marketplace-agent | Marketplace | `src/marketplace/`, `tests/marketplace/` | `src/shared/`, `src/mcp/errors.py` |
| dex-agent | DEX Aggregator | `src/dex/`, `tests/dex/` | `src/shared/`, `src/mcp/errors.py` |
| wallet-agent | Wallet | `src/wallet/`, `tests/wallet/` | `src/shared/` |
| mcp-agent | MCP Server | `src/mcp/` | All domain `tools.py` files |
| metrics-agent | Metrics | `src/metrics/`, `tests/metrics/` | `src/shared/`, marketplace data |
| infra-agent | Infrastructure | `Dockerfile`, `docker-compose.yml`, `infra/`, `.github/workflows/` | `src/` (read-only) |
| shared-agent | Shared Utils | `src/shared/`, `tests/shared/` | All domain `models.py` files |

### Rules for Subagent Development

1. **Stay in your domain.** Only modify files you own. Read dependencies, don't edit them.
2. **Contract-first.** Define `models.py` (Pydantic contracts) before implementing `service.py` or `tools.py`.
3. **Export a register function.** Each domain's `tools.py` exports a `register(server: FastMCP)` function that adds prefixed tools to the main server.
4. **Use structured errors.** Import `tool_error` from `src/mcp/errors.py` for all error responses.
5. **Write tests.** Tests mirror source structure. Use pytest. Mock external dependencies.
6. **Don't over-engineer.** Start simple. In-memory stores before databases. Stubs before full implementations.

### How to Invoke a Subagent

When working on a specific domain, reference the agent definition file for context:
```
Read .claude/agents/marketplace-agent.md for domain context, then work on src/marketplace/
```

### Implementation Phases

See `docs/implementation-plan.md` for the phased build plan with subagent assignments per phase.

## Key Documents

| Document | Purpose |
|----------|---------|
| `docs/vision.md` | WHY — the product vision |
| `docs/specification.md` | WHAT — detailed product spec |
| `docs/implementation-plan.md` | HOW — phased build plan |
| `docs/conventions.md` | STYLE — coding conventions |
| `CONTRIBUTING.md` | PROCESS — how to contribute |

## Do Not Modify

- `openclaw/` — separate repository, never touch
- `app-template/` — reference only, not the active app
