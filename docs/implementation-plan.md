# MangroveMarkets — Implementation Plan

> This document defines HOW and WHEN to build MangroveMarkets. For WHAT to build, see [specification.md](specification.md). For WHY, see [vision.md](vision.md).

---

## Phases Overview

| Phase | Name | Focus | Depends On |
|-------|------|-------|------------|
| 0 | Project Setup | Structure, docs, conventions | — |
| 1 | Foundation | Shared utils, MCP skeleton, wallet | Phase 0 |
| 2 | Marketplace Core | Listings CRUD, search | Phase 1 |
| 3 | Marketplace Settlement | Escrow, delivery, ratings | Phase 2 |
| 4 | DEX Aggregator | Adapter interface, XPMarket | Phase 1 |
| 5 | Storage & Delivery | IPFS integration, encryption | Phase 3 |
| 6 | Metrics & Intelligence | Market data, usage metering | Phase 2 |
| 7 | Integration Tools | Akash, Bittensor, Fetch.ai, Nodes.ai | Phase 1 |
| 8 | Production Readiness | DB persistence, auth, deployment | Phases 3-7 |

Phases 4, 5, 6, and 7 can run in parallel after their dependencies are met.

---

## Phase 0: Project Setup

**Status**: Complete

### Deliverables
- Project directory structure (`src/`, `tests/`, `infra/`, `.github/`)
- Repo standards (`CONTRIBUTING.md`, `docs/conventions.md`, GitHub templates)
- Subagent definitions (`.claude/agents/*.md`)
- Specification document (`docs/specification.md`)
- This implementation plan (`docs/implementation-plan.md`)
- MCP server skeleton with tool stubs
- Shared utilities (config, DB, auth, health, types)
- `pyproject.toml`, `requirements.txt`
- `Dockerfile`, `docker-compose.yml`
- Updated `AGENTS.md`, `.gitignore`, `.claude/settings.json`

### Subagent Assignments
- Orchestrator handles all Phase 0 work

### Verification
- [x] All directories and `__init__.py` files exist
- [x] `pip install -r requirements.txt` succeeds
- [x] `python -c "from src.mcp.server import mcp"` imports without error
- [x] `docker compose build` succeeds
- [x] Each domain's `tools.py` and `models.py` imports independently
- [x] `docs/specification.md` covers all tools, models, flows
- [x] `.claude/agents/` has 11 agent definitions

---

## Phase 1: Foundation

**Goal**: Working MCP server with wallet tools on XRPL testnet.

### Deliverables

#### Shared Agent
- `src/shared/config.py` — finalize config with all required keys
- `src/shared/db.py` — PostgreSQL connection pool (not just single connections)
- `src/shared/types.py` — finalize shared types based on domain needs
- `tests/shared/test_config.py`, `tests/shared/test_db.py`

#### Wallet Agent
- `src/wallet/xrpl_client.py` — XRPL connection manager (testnet)
- `src/wallet/service.py` — wallet_create (faucet), wallet_balance, wallet_send, wallet_transactions
- `src/wallet/tools.py` — replace stubs with working implementations
- `tests/wallet/test_tools.py`, `tests/wallet/test_service.py`

#### MCP Agent
- `src/mcp/server.py` — verify all tool registrations work, server starts
- Health check returns meaningful dependency status

### Subagent Assignments
| Subagent | Task |
|----------|------|
| shared-agent | Config finalization, DB pooling, shared types |
| wallet-agent | XRPL client, wallet service, wallet tools |
| mcp-agent | Server verification, health check |

### Verification
- [ ] MCP server starts and responds to tool discovery
- [ ] `wallet_create` creates a funded wallet on testnet
- [ ] `wallet_balance` returns correct balance
- [ ] `wallet_send` transfers XRP between two testnet wallets
- [ ] `wallet_transactions` returns transaction history
- [ ] Health check reports database and XRPL status
- [ ] All tests pass

---

## Phase 2: Marketplace Core

**Goal**: Agents can create and search listings.

### Deliverables

#### Marketplace Agent
- `src/marketplace/models.py` — finalize with validation
- `src/marketplace/repository.py` — in-memory store (DB in Phase 8)
- `src/marketplace/service.py` — create_listing, search, get_listing
- `src/marketplace/tools.py` — replace stubs for create_listing, search, get_listing
- `tests/marketplace/test_service.py`, `tests/marketplace/test_tools.py`

### Subagent Assignments
| Subagent | Task |
|----------|------|
| marketplace-agent | All Phase 2 deliverables |

### Verification
- [ ] `marketplace_create_listing` creates a listing and returns its ID
- [ ] `marketplace_search` finds listings by query, category, price range
- [ ] `marketplace_get_listing` returns full listing details
- [ ] Input validation works (bad category, negative price, etc.)
- [ ] Error responses follow structured format
- [ ] All tests pass

---

## Phase 3: Marketplace Settlement

**Goal**: Full buy/sell flow with XRPL escrow.

### Deliverables

#### Marketplace Agent
- `src/marketplace/escrow.py` — XRPL escrow create, finish, cancel
- `src/marketplace/service.py` — add make_offer, accept_offer, deliver, confirm_delivery, cancel, rate
- `src/marketplace/tools.py` — replace remaining stubs
- `tests/marketplace/test_escrow.py`

### Subagent Assignments
| Subagent | Task |
|----------|------|
| marketplace-agent | Escrow integration, offer/delivery flow |
| wallet-agent | Support escrow operations in XRPL client (if needed) |

### Verification
- [ ] Full flow on testnet: create listing → make offer → accept → deliver → confirm → rate
- [ ] XRPL escrow creates and releases correctly
- [ ] Cancellation refunds escrow
- [ ] Rating persists and is queryable
- [ ] Marketplace fee deducted correctly
- [ ] All tests pass

---

## Phase 4: DEX Aggregator

**Goal**: Agents can get quotes and swap tokens on XRPL native DEX.

### Deliverables

#### DEX Agent
- `src/dex/adapters/xpmarket.py` — XRPL native DEX adapter (full implementation)
- `src/dex/adapters/uniswap.py` — stub returning VENUE_NOT_SUPPORTED
- `src/dex/adapters/jupiter.py` — stub returning VENUE_NOT_SUPPORTED
- `src/dex/router.py` — best-route selection (simple: best price)
- `src/dex/service.py` — quote, swap, status
- `src/dex/tools.py` — replace stubs with working implementations
- `tests/dex/test_router.py`, `tests/dex/test_service.py`

### Subagent Assignments
| Subagent | Task |
|----------|------|
| dex-agent | All Phase 4 deliverables |

### Verification
- [ ] `dex_supported_venues` lists XPMarket as active
- [ ] `dex_supported_pairs` returns XRPL trading pairs
- [ ] `dex_get_quote` returns a valid quote from XPMarket
- [ ] `dex_swap` executes a swap on XRPL testnet
- [ ] `dex_swap_status` tracks swap confirmation
- [ ] Uniswap/Jupiter stubs return clear "not yet supported" errors
- [ ] Mangrove fee calculated correctly in quotes
- [ ] All tests pass

---

## Phase 5: Storage & Delivery

**Goal**: Decentralized storage integration for marketplace data delivery.

### Deliverables

#### Marketplace Agent
- `src/marketplace/storage.py` — IPFS upload/download integration
- Encryption/decryption key management for static goods
- `marketplace_deliver` tool implementation (key exchange)
- Content hash verification on buyer side

### Subagent Assignments
| Subagent | Task |
|----------|------|
| marketplace-agent | Storage integration, encryption, delivery flow |

### Verification
- [ ] Seller can upload encrypted content to IPFS
- [ ] Listing includes storage_uri and content_hash
- [ ] Buyer receives decryption key on settlement
- [ ] Content hash verification passes for valid content
- [ ] Full static goods flow works end-to-end

---

## Phase 6: Metrics & Intelligence

**Goal**: Market intelligence tools with usage metering.

### Deliverables

#### Metrics Agent
- `src/metrics/service.py` — aggregation queries, trend calculation
- `src/metrics/tools.py` — replace stubs with working implementations
- Usage metering (per-wallet call counting, tier enforcement)
- `tests/metrics/test_service.py`

### Subagent Assignments
| Subagent | Task |
|----------|------|
| metrics-agent | All Phase 6 deliverables |

### Verification
- [ ] `metrics_market_overview` returns marketplace stats
- [ ] `metrics_category_trends` shows demand/supply data
- [ ] `metrics_price_history` returns time-series price data
- [ ] Free tier limits at 50 calls
- [ ] Usage info included in every response
- [ ] Quota exhaustion returns clear error with purchase instructions
- [ ] All tests pass

---

## Phase 7: Integration Tools

**Goal**: At least one external integration fully functional.

### Deliverables
- `src/integrations/tools.py` — replace stubs with real implementations
- Start with one integration (likely Akash or Bittensor) as proof of concept
- Others can remain as stubs with clear "coming soon" errors

### Subagent Assignments
| Subagent | Task |
|----------|------|
| integration-agent | Integration implementations |

### Verification
- [ ] At least one `integration_*` tool works end-to-end
- [ ] Other integrations return clear "not yet implemented" errors
- [ ] No proxying or intermediation — agent interacts directly

---

## Phase 8: Production Readiness

**Goal**: Deployed, secure, and persistent.

### Deliverables

#### Shared Agent
- PostgreSQL persistence — replace in-memory stores with DB queries
- Database migrations (schema creation scripts)
- Auth hardening — real JWT validation, wallet signature verification

#### Infra Agent
- Terraform deployment to GCP Cloud Run (dev environment)
- CI/CD pipeline (GitHub Actions)
- Secret Manager configuration
- Cloud SQL setup

#### All Agents
- Error handling audit — verify all tools follow structured error convention
- Input validation audit — verify all parameters are validated
- Security audit — no secret logging, no hardcoded credentials

### Subagent Assignments
| Subagent | Task |
|----------|------|
| shared-agent | DB persistence, migrations, auth hardening |
| infra-agent | Terraform, CI/CD, Cloud SQL |
| All agents | Error and security audits |

### Verification
- [ ] Application deploys to GCP Cloud Run
- [ ] All data persists in PostgreSQL (survives restart)
- [ ] Auth works with real JWT tokens
- [ ] CI/CD pipeline builds, tests, and deploys on merge
- [ ] Health check verifies all dependencies
- [ ] No secrets in logs or code
- [ ] All tools return structured errors
- [ ] All tests pass in CI

---

## Dependency Graph

```
Phase 0 (Setup)
    │
    v
Phase 1 (Foundation: shared + wallet + MCP)
    │
    ├──────────────┬──────────────┐
    v              v              v
Phase 2         Phase 4        Phase 7
(Marketplace    (DEX           (Integration
 Core)          Aggregator)     Tools)
    │              │
    v              │
Phase 3            │
(Settlement)       │
    │              │
    v              │
Phase 5            │
(Storage)          │
    │              │
    ├──────────────┘
    v
Phase 6 (Metrics — needs marketplace data)
    │
    v
Phase 8 (Production Readiness)
```

---

## Parallelization Opportunities

After Phase 1 completes:
- **Marketplace Agent** can work on Phases 2→3→5 independently
- **DEX Agent** can work on Phase 4 independently
- **Metrics Agent** can start Phase 6 once Phase 2 data exists
- **Integration work** (Phase 7) can happen anytime after Phase 1
- **Infra Agent** can prepare Terraform and CI/CD at any point

Maximum parallelism: 5 subagents working simultaneously (marketplace, dex, metrics, integrations, infra).

### Cross-Cutting Agents (Available at Any Phase)

| Agent | Role |
|-------|------|
| ui-agent | Frontend work — landing pages, dashboards, agent-facing UIs |
| qa-agent | E2E testing, integration testing, cross-domain test flows |
| code-review-agent | Convention compliance, code quality, cross-agent consistency checks |

These agents can be invoked at any phase and are not tied to a specific phase's deliverables.
