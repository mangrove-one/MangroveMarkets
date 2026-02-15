# Marketplace Agent

## Role
Implements the Mangrove Marketplace — agent-to-agent bulletin board for buying/selling digital goods and services, settled in XRP on the XRPL.

## Owned Files
- `src/marketplace/` — all marketplace source code
- `tests/marketplace/` — all marketplace tests

## Read-Only Dependencies
- `src/shared/` — config, database, auth, shared types
- `src/mcp/errors.py` — structured error helpers (tool_error, tool_success)

## Domain Knowledge

### Core Concepts
- **Listing** — something an agent offers for sale (data, compute, model, API, etc.)
- **Offer** — a buyer's intent to purchase at the listed price
- **Escrow** — XRP locked on XRPL until delivery is confirmed
- **Rating** — post-transaction feedback (1-5 score)
- **Categories** — Data, Compute, Intelligence, Models, APIs, Storage, Identity, Media, Code, Other

### Listing Lifecycle
`draft → active → offered → escrowed → delivered → completed → rated`

Cancellation is possible from: active, offered, escrowed (with refund).

### Two Listing Types
- **Static** (data, models, code) — delivered via decentralized storage (IPFS/Arweave/Filecoin). Seller uploads encrypted content, buyer gets decryption key on settlement.
- **Service** (compute, APIs) — delivered via access provisioning. Seller provides endpoint/credentials after escrow.

### Settlement Flow
1. Buyer makes offer → 2. Seller accepts → 3. XRPL escrow created → 4. Seller delivers → 5. Buyer confirms → 6. Escrow released → 7. Both rate

### XRPL Escrow
- Use `EscrowCreate` with `finish_after` (time-based) or `condition` (conditional)
- Use `EscrowFinish` when buyer confirms delivery
- Use `EscrowCancel` when escrow expires without confirmation
- Always validate `tesSUCCESS` on transaction results
- Use xrpl-py library for all XRPL operations

## Constraints
- **Never modify** `src/shared/` or `src/mcp/` — those belong to other agents
- **Never store wallet seeds** — accept as parameters, use for signing, discard immediately
- **Never hardcode XRPL mainnet credentials** — use testnet/devnet for development
- **Never set prices** — agents set their own prices
- **Never gate access** — open marketplace, no KYC
- **Never store actual data** — only store metadata; content lives on decentralized storage

## Exports
- **`src/marketplace/tools.py`** — `register(server)` function that adds `marketplace_*` tools to the main FastMCP server
- **`src/marketplace/models.py`** — Pydantic v2 models: Listing, Offer, Rating, Category, ListingType, ListingStatus, OfferStatus

## Patterns to Follow

### File Structure
```
src/marketplace/
  __init__.py
  tools.py           # MCP tool definitions (thin — delegates to service)
  models.py          # Pydantic models for all marketplace data
  service.py         # Business logic (create, search, offer, deliver, rate)
  escrow.py          # XRPL escrow operations (create, finish, cancel)
  storage.py         # Decentralized storage integration (IPFS, Arweave)
  repository.py      # Database operations (CRUD for listings, offers, ratings)
```

### Tool Design
- Tools are thin: validate input, call service, return result
- All tools return structured JSON via `mcp/errors.py` helpers
- Error messages include actionable context: "Insufficient XRP: have 5, need 10"
- Use Pydantic models for input validation

### Testing
- `tests/marketplace/test_tools.py` — tool input/output validation
- `tests/marketplace/test_service.py` — business logic
- `tests/marketplace/test_escrow.py` — XRPL escrow operations (mocked)
- Mock XRPL client and database in unit tests
