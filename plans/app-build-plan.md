# MangroveMarkets — App Build Plan (Draft)

## Objective
Build the first working Mangrove marketplace app now that CI/CD + deployment are ready.

## MVP Scope (must‑have)
1) **On‑chain identity** — wallet required to participate; agent profile keyed by wallet address.
2) **Marketplace listings** — create/read/update/expire offers + requests.
3) **Discovery** — browse + filter + search (category/tags/price/latency).
4) **Transaction + escrow** — initiate, fund, deliver, release, dispute (XRPL escrow flow).
5) **Delivery metadata** — proof‑of‑delivery or fulfillment link (hash/IPFS URL).
6) **Reputation signals** — basic rating + completed transaction count.
7) **Admin tooling** — review flags, resolve disputes, manage categories.

## Out of Scope (MVP)
- Advanced analytics, DEX aggregation, cross‑chain bridges, heavy social features.

## Phases & Milestones

### Phase 0 — Product + Architecture (1–2 weeks)
- Finalize MVP requirements + user stories
- Data model + API contract (MCP tooling + REST/GraphQL endpoints)
- Security model (wallet auth, escrow permissions)

### Phase 1 — Core Backend (2–3 weeks)
- Wallet auth + agent profiles
- Listings CRUD + discovery endpoints
- Escrow state machine + transaction lifecycle
- Audit logging + rate limits

### Phase 2 — Frontend (2–3 weeks)
- Landing → app entry
- Marketplace browse/search
- Listing create/edit
- Transaction flow + status UI

### Phase 3 — Trust + Ops (1–2 weeks)
- Dispute flow + admin tooling
- Basic reputation + reporting
- Monitoring + alerting

### Phase 4 — QA + Launch Readiness (1–2 weeks)
- End‑to‑end tests
- Security review + threat model
- Release checklist

## Key Decisions Needed
- Wallet auth method (XRPL signing flow, provider SDK)
- Escrow model details (time locks, dispute arbiter)
- Initial categories/tags taxonomy
- Pricing/fee model for marketplace

## Deliverables
- MVP app deployed with live escrow transactions
- Docs for agents + MCP tool usage
- Admin runbook + monitoring dashboards
