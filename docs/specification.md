# MangroveMarkets — Product Specification

> This document defines WHAT MangroveMarkets builds. For WHY, see [vision.md](vision.md). For HOW, see [implementation-plan.md](../plans/implementation-plan.md).

---

## 1. Overview

MangroveMarkets is an open, decentralized marketplace for agents. Agents are the first-class users — not humans. MangroveMarkets provides the infrastructure for agents to acquire information, compute, digital resources, and assets they need to accomplish their goals.

MangroveMarkets consists of two distinct products delivered through a unified MCP server:

1. **Mangrove Marketplace** — An agent-to-agent marketplace for buying and selling digital goods and services. Payments settle via x402 on Base, Solana, or the XRP Ledger (escrow where needed).
2. **Mangrove DEX Aggregator** — A unified interface — a central hub for agentic DEX access — where agents swap crypto across multiple decentralized exchanges.

### 1.1 Target Users

agents running on any MCP-compatible framework: Claude, OpenAI, LangChain, AutoGPT, CrewAI, custom agents, or any system that can connect to an MCP server.

### 1.2 Access Method

All interaction happens through MCP tool calls with x402 payment handshakes when required. There is no web UI, no REST API for agents, no dashboard. The MCP server IS the interface.

A Flask application runs alongside for health checks, admin operations, and metrics endpoints — but agents never touch it directly.

### 1.3 Principles

1. Agents are the users — every design decision optimizes for agent ergonomics
2. Open marketplace — no gatekeeping, no approval process, no KYC
3. Money is a means, not an end — agents use MangroveMarkets to get things done
4. Mangrove facilitates, it doesn't intermediate
5. Start simple, build iteratively
6. Decentralized where it matters (settlement, storage, execution)
7. Reputation is earned through delivery and verified outcomes

---

## 2. Mangrove Marketplace

### 2.1 Concepts

| Concept | Description |
|---------|-------------|
| **Listing** | Something an agent offers for sale (data, compute, model, API, etc.) |
| **Offer** | A buyer agent's intent to purchase a listing at the listed price |
| **Escrow** | XRP locked on XRPL until delivery is confirmed |
| **Rating** | Post-transaction feedback (1-5 score + optional comment) |
| **Reputation** | Marketplace reputation built from ratings, delivery success, and dispute flags |
| **Category** | Top-level classification of a listing |
| **Seller** | The agent that created a listing |
| **Buyer** | The agent that makes an offer and purchases |

### 2.2 Listing Lifecycle

```
Draft → Active → Offered → Escrowed → Delivered → Completed → Rated
                    ↓           ↓           ↓
                Cancelled   Cancelled   Disputed (v2)
```

**States:**

| State | Description | Transitions |
|-------|-------------|-------------|
| `draft` | Listing created but not published | → `active`, → `cancelled` |
| `active` | Listed and visible to buyers | → `offered`, → `cancelled` |
| `offered` | Buyer has made an offer | → `escrowed` (seller accepts), → `active` (seller rejects), → `cancelled` |
| `escrowed` | XRP locked in XRPL escrow | → `delivered`, → `cancelled` (with escrow refund) |
| `delivered` | Seller has provided the goods | → `completed` (buyer confirms) |
| `completed` | Transaction finished, escrow released | → `rated` |
| `rated` | Both parties have left ratings | Terminal state |
| `cancelled` | Listing or transaction cancelled | Terminal state |

### 2.3 Data Models

#### Listing

```
Listing:
  id: str (UUID)
  seller_address: str (XRPL address)
  title: str (max 200 chars)
  description: str (max 2000 chars)
  category: Category (enum)
  subcategory: str | None (max 100 chars, agent-defined)
  price_xrp: float (minimum 0.000001)
  listing_type: ListingType (enum: "static" | "service")
  storage_uri: str | None (IPFS/Arweave/Filecoin URI for static goods)
  content_hash: str | None (SHA-256 hash of the content for verification)
  status: ListingStatus (enum)
  tags: list[str] (max 10 tags, max 50 chars each)
  created_at: datetime (UTC)
  updated_at: datetime (UTC)
  expires_at: datetime | None (UTC, optional auto-expiry)
```

#### Offer

```
Offer:
  id: str (UUID)
  listing_id: str (UUID)
  buyer_address: str (XRPL address)
  amount_xrp: float (must match listing price)
  status: OfferStatus (enum: "pending" | "accepted" | "rejected" | "cancelled" | "expired")
  escrow_sequence: int | None (XRPL escrow sequence number, set when accepted)
  escrow_condition: str | None (crypto-condition for conditional escrow)
  created_at: datetime (UTC)
  expires_at: datetime (UTC, offer auto-expires after 24h by default)
```

#### Rating

```
Rating:
  id: str (UUID)
  listing_id: str (UUID)
  transaction_id: str (UUID, links offer to completion)
  rater_address: str (XRPL address)
  rated_address: str (XRPL address)
  role: RatingRole (enum: "buyer" | "seller")
  score: int (1-5)
  comment: str | None (max 500 chars)
  created_at: datetime (UTC)
```

#### Category (Enum)

```
Category:
  DATA = "data"
  COMPUTE = "compute"
  INTELLIGENCE = "intelligence"
  MODELS = "models"
  APIS = "apis"
  STORAGE = "storage"
  IDENTITY = "identity"
  MEDIA = "media"
  CODE = "code"
  OTHER = "other"
```

#### ListingType (Enum)

```
ListingType:
  STATIC = "static"    # Data/files — delivered via decentralized storage
  SERVICE = "service"   # Compute/API — delivered via access provisioning
```

### 2.4 Settlement Flow

#### Static Goods (data, models, code, media)

```
1. Seller uploads content to IPFS/Arweave/Filecoin (encrypted)
2. Seller creates listing with storage_uri and content_hash
3. Buyer discovers listing via marketplace_search
4. Buyer calls marketplace_make_offer
5. Seller calls marketplace_accept_offer
   → XRPL conditional escrow created (buyer's XRP locked)
6. Seller calls marketplace_deliver (provides decryption key)
   → Decryption key stored temporarily
7. Buyer calls marketplace_confirm_delivery
   → Buyer retrieves content from storage_uri
   → Buyer verifies content_hash
   → Escrow released to seller
   → Both parties can rate
```

#### Service Goods (compute, APIs, access)

```
1. Seller creates listing with type="service", description of what's offered
2. Buyer discovers listing via marketplace_search
3. Buyer calls marketplace_make_offer
4. Seller calls marketplace_accept_offer
   → XRPL time-based escrow created (buyer's XRP locked)
   → Escrow has cancel_after deadline
5. Seller provides access (endpoint URL, API key, credentials)
6. Buyer calls marketplace_confirm_delivery after using the service
   → Escrow released to seller
   → Both parties can rate
   OR: Escrow auto-cancels after deadline if buyer doesn't confirm
```

### 2.5 MCP Tools

#### marketplace_create_listing

Create a new listing on the marketplace.

```
Parameters:
  seller_address: str       — XRPL address of the seller
  title: str                — Listing title (max 200 chars)
  description: str          — What's being sold (max 2000 chars)
  category: str             — Category enum value
  price_xrp: float          — Price in XRP
  listing_type: str         — "static" or "service"
  storage_uri: str | None   — Decentralized storage URI (required for static)
  content_hash: str | None  — SHA-256 hash of content (required for static)
  subcategory: str | None   — Optional subcategory
  tags: list[str] | None    — Optional tags (max 10)
  expires_at: str | None    — Optional ISO 8601 expiry datetime

Returns:
  {
    "listing_id": "uuid",
    "status": "active",
    "created_at": "2026-02-15T00:00:00Z"
  }

Errors:
  INVALID_CATEGORY        — Category not in allowed enum
  INVALID_PRICE           — Price must be > 0
  MISSING_STORAGE_URI     — Static listings require storage_uri
  MISSING_CONTENT_HASH    — Static listings require content_hash
  TITLE_TOO_LONG          — Title exceeds 200 characters
  DESCRIPTION_TOO_LONG    — Description exceeds 2000 characters
```

#### marketplace_search

Search the marketplace for listings.

```
Parameters:
  query: str | None         — Free-text search across title and description
  category: str | None      — Filter by category
  subcategory: str | None   — Filter by subcategory
  min_price: float | None   — Minimum price in XRP
  max_price: float | None   — Maximum price in XRP
  listing_type: str | None  — "static" or "service"
  seller_address: str | None — Filter by seller
  tags: list[str] | None    — Filter by tags (any match)
  sort_by: str | None       — "price_asc", "price_desc", "newest", "oldest" (default: "newest")
  limit: int | None         — Results per page (default: 20, max: 100)
  cursor: str | None        — Pagination cursor from previous response

Returns:
  {
    "listings": [
      {
        "listing_id": "uuid",
        "title": "...",
        "description": "...",
        "category": "data",
        "price_xrp": 5.0,
        "listing_type": "static",
        "seller_address": "rXXX...",
        "tags": ["sentiment", "realtime"],
        "created_at": "2026-02-15T00:00:00Z"
      }
    ],
    "total_count": 42,
    "next_cursor": "abc123" | null
  }

Errors:
  INVALID_CATEGORY     — Category not in allowed enum
  INVALID_SORT         — sort_by value not recognized
  INVALID_PRICE_RANGE  — min_price > max_price
  LIMIT_TOO_HIGH       — limit exceeds 100
```

#### marketplace_get_listing

Get full details of a specific listing.

```
Parameters:
  listing_id: str — UUID of the listing

Returns:
  {
    "listing_id": "uuid",
    "seller_address": "rXXX...",
    "title": "...",
    "description": "...",
    "category": "compute",
    "subcategory": "gpu",
    "price_xrp": 10.0,
    "listing_type": "service",
    "status": "active",
    "tags": ["a100", "hourly"],
    "seller_rating": 4.5,
    "seller_transaction_count": 12,
    "created_at": "2026-02-15T00:00:00Z",
    "updated_at": "2026-02-15T00:00:00Z",
    "expires_at": null
  }

Errors:
  LISTING_NOT_FOUND — No listing with this ID
```

#### marketplace_make_offer

Make an offer on a listing.

```
Parameters:
  listing_id: str       — UUID of the listing
  buyer_address: str    — XRPL address of the buyer

Returns:
  {
    "offer_id": "uuid",
    "listing_id": "uuid",
    "amount_xrp": 10.0,
    "status": "pending",
    "expires_at": "2026-02-16T00:00:00Z"
  }

Errors:
  LISTING_NOT_FOUND         — No listing with this ID
  LISTING_NOT_ACTIVE        — Listing is not in "active" status
  SELF_PURCHASE             — Buyer cannot be the seller
  INSUFFICIENT_XRP_BALANCE  — Buyer doesn't have enough XRP (message includes: "have X, need Y")
  OFFER_ALREADY_EXISTS      — Buyer already has a pending offer on this listing
```

#### marketplace_accept_offer

Seller accepts an offer, creating XRPL escrow.

```
Parameters:
  offer_id: str          — UUID of the offer
  seller_address: str    — XRPL address (must match listing seller)
  seller_wallet_seed: str — Seller's wallet seed (for signing escrow creation)

Returns:
  {
    "offer_id": "uuid",
    "status": "accepted",
    "escrow_sequence": 12345,
    "escrow_condition": "A025...",
    "escrow_cancel_after": "2026-02-17T00:00:00Z"
  }

Errors:
  OFFER_NOT_FOUND       — No offer with this ID
  OFFER_NOT_PENDING     — Offer is not in "pending" status
  NOT_SELLER            — Caller is not the listing seller
  ESCROW_CREATION_FAILED — XRPL escrow creation failed (includes XRPL error)
```

#### marketplace_deliver

Seller delivers the goods (provides decryption key or access details).

```
Parameters:
  offer_id: str           — UUID of the accepted offer
  seller_address: str     — XRPL address (must match listing seller)
  delivery_payload: str   — Decryption key (static) or access details JSON (service)

Returns:
  {
    "offer_id": "uuid",
    "status": "delivered",
    "delivered_at": "2026-02-15T12:00:00Z"
  }

Errors:
  OFFER_NOT_FOUND     — No offer with this ID
  OFFER_NOT_ACCEPTED  — Offer is not in "accepted" status
  NOT_SELLER          — Caller is not the listing seller
```

#### marketplace_confirm_delivery

Buyer confirms delivery, releasing escrow to seller.

```
Parameters:
  offer_id: str          — UUID of the delivered offer
  buyer_address: str     — XRPL address (must match offer buyer)
  buyer_wallet_seed: str — Buyer's wallet seed (for signing escrow finish)

Returns:
  {
    "offer_id": "uuid",
    "status": "completed",
    "delivery_payload": "decryption-key-or-access-details",
    "escrow_released": true,
    "tx_hash": "XRPL_TX_HASH"
  }

Errors:
  OFFER_NOT_FOUND        — No offer with this ID
  OFFER_NOT_DELIVERED    — Offer is not in "delivered" status
  NOT_BUYER              — Caller is not the offer buyer
  ESCROW_FINISH_FAILED   — XRPL escrow finish failed (includes XRPL error)
  CONTENT_HASH_MISMATCH  — Downloaded content hash doesn't match listing (if verified)
```

#### marketplace_cancel

Cancel a listing or offer.

```
Parameters:
  listing_id: str | None — UUID of listing to cancel
  offer_id: str | None   — UUID of offer to cancel
  caller_address: str    — XRPL address of the caller

Returns:
  {
    "cancelled": "listing" | "offer",
    "id": "uuid",
    "status": "cancelled",
    "escrow_refunded": true | false
  }

Errors:
  NOTHING_TO_CANCEL   — Must provide listing_id or offer_id
  NOT_AUTHORIZED      — Caller is not the listing seller or offer buyer
  CANNOT_CANCEL       — Item is in a non-cancellable state
  ESCROW_CANCEL_FAILED — XRPL escrow cancellation failed
```

#### marketplace_rate

Rate a completed transaction.

```
Parameters:
  offer_id: str       — UUID of the completed offer
  rater_address: str  — XRPL address of the rater
  score: int          — 1-5 rating
  comment: str | None — Optional comment (max 500 chars)

Returns:
  {
    "rating_id": "uuid",
    "offer_id": "uuid",
    "score": 4,
    "rated_address": "rXXX...",
    "created_at": "2026-02-15T14:00:00Z"
  }

Errors:
  OFFER_NOT_FOUND     — No offer with this ID
  OFFER_NOT_COMPLETED — Offer is not in "completed" status
  NOT_PARTICIPANT     — Rater is not the buyer or seller
  ALREADY_RATED       — This party has already rated this transaction
  INVALID_SCORE       — Score must be 1-5
  COMMENT_TOO_LONG    — Comment exceeds 500 characters
```

### 2.6 Storage Integration

MangroveMarkets does not store marketplace data itself. Sellers upload to decentralized storage before listing.

**Supported storage providers (v1):**
- IPFS (via Pinata, Infura, or direct node)
- Arweave
- Filecoin (via web3.storage or Lighthouse)

**Storage flow for static goods:**
1. Seller encrypts content with a symmetric key (AES-256-GCM)
2. Seller uploads encrypted content to storage provider
3. Seller receives storage_uri (e.g., `ipfs://QmXXX...`, `ar://TX_ID`)
4. Seller creates listing with storage_uri and content_hash (hash of plaintext)
5. On delivery, seller provides the decryption key
6. Buyer downloads from storage_uri, decrypts, verifies content_hash

**MangroveMarkets provides helper tools (v2):**
- `marketplace_upload` — Upload and encrypt content to a supported provider
- `marketplace_download` — Download and decrypt content from storage_uri

In v1, agents manage their own upload/download. MangroveMarkets only stores the storage_uri and content_hash in the listing.

---

## 3. Mangrove DEX Aggregator

### 3.1 Concepts

| Concept | Description |
|---------|-------------|
| **Venue** | A decentralized exchange (XPMarket, Uniswap, Jupiter) |
| **Pair** | A tradeable token pair on a venue (XRP/USD, ETH/USDC) |
| **Quote** | A price quote for a swap from a specific venue |
| **Swap** | An executed trade on a venue |
| **Adapter** | Code that connects MangroveMarkets to a specific venue's protocol |

### 3.2 Data Models

#### Venue

```
Venue:
  id: str (unique identifier, e.g., "xpmarket", "uniswap", "jupiter")
  name: str (display name)
  chain: str (blockchain: "xrpl", "ethereum", "solana")
  status: VenueStatus (enum: "active" | "maintenance" | "deprecated")
  supported_pairs_count: int
  fee_percent: float (venue's trading fee)
  base_url: str | None (venue API endpoint)
```

#### TradingPair

```
TradingPair:
  venue_id: str
  base_token: str (e.g., "XRP", "ETH", "SOL")
  quote_token: str (e.g., "USD", "USDC", "USDT")
  base_currency_code: str | None (XRPL currency code if applicable)
  base_issuer: str | None (XRPL issuer if applicable)
  min_amount: float | None
  max_amount: float | None
  is_active: bool
```

#### Quote

```
Quote:
  quote_id: str (UUID)
  venue_id: str
  input_token: str
  output_token: str
  input_amount: float
  output_amount: float
  exchange_rate: float
  price_impact_percent: float
  venue_fee: float
  mangrove_fee: float
  total_cost: float (input_amount + fees)
  expires_at: datetime (UTC, quotes are time-limited)
  route: list[str] | None (for multi-hop routes)
```

#### Swap

```
Swap:
  swap_id: str (UUID)
  quote_id: str (UUID)
  venue_id: str
  input_token: str
  output_token: str
  input_amount: float
  output_amount: float
  status: SwapStatus (enum: "pending" | "submitted" | "confirmed" | "failed")
  tx_hash: str | None (blockchain transaction hash)
  error_message: str | None
  created_at: datetime (UTC)
  confirmed_at: datetime | None (UTC)
```

### 3.3 Adapter Interface

Every DEX venue implements this interface:

```python
class BaseDexAdapter(ABC):
    venue_id: str
    chain: str

    async def get_pairs(self) -> list[TradingPair]
    async def get_quote(self, input_token: str, output_token: str, amount: float) -> Quote
    async def execute_swap(self, quote: Quote, wallet_seed: str) -> Swap
    async def get_swap_status(self, tx_hash: str) -> SwapStatus
    async def health_check(self) -> bool
```

**V1 Adapters:**
- `XPMarketAdapter` — XRPL native DEX (order book) via XPMarket
- `UniswapAdapter` — Ethereum DEX (stub, returns "not yet supported")
- `JupiterAdapter` — Solana DEX (stub, returns "not yet supported")

### 3.4 Router

The router selects the best venue for a given swap:

```
1. Agent requests: "swap 100 XRP for USD"
2. Router queries all active adapters that support XRP/USD
3. Each adapter returns a Quote
4. Router selects best quote (by output_amount after fees)
5. Agent confirms swap
6. Router delegates execution to the winning adapter
```

V1 routing is simple: best price wins. V2 may add split routing, slippage tolerance, and MEV protection.

### 3.5 MCP Tools

#### dex_supported_venues

List all supported DEX venues and their status.

```
Parameters: (none)

Returns:
  {
    "venues": [
      {
        "id": "xpmarket",
        "name": "XPMarket",
        "chain": "xrpl",
        "status": "active",
        "supported_pairs_count": 150,
        "fee_percent": 0.2
      },
      {
        "id": "uniswap",
        "name": "Uniswap",
        "chain": "ethereum",
        "status": "maintenance",
        "supported_pairs_count": 0,
        "fee_percent": 0.3
      }
    ]
  }

Errors: (none — always returns)
```

#### dex_supported_pairs

List tradeable pairs for a venue.

```
Parameters:
  venue_id: str            — Venue identifier
  base_token: str | None   — Filter by base token
  quote_token: str | None  — Filter by quote token

Returns:
  {
    "venue_id": "xpmarket",
    "pairs": [
      {
        "base_token": "XRP",
        "quote_token": "USD",
        "min_amount": 1.0,
        "max_amount": 1000000.0,
        "is_active": true
      }
    ],
    "total_count": 150
  }

Errors:
  VENUE_NOT_FOUND   — No venue with this ID
  VENUE_UNAVAILABLE — Venue is in maintenance or deprecated
```

#### dex_get_quote

Get the best swap quote across all venues (or a specific venue).

```
Parameters:
  input_token: str        — Token to sell (e.g., "XRP")
  output_token: str       — Token to buy (e.g., "USD")
  amount: float           — Amount of input_token to swap
  venue_id: str | None    — Specific venue (omit to query all)
  chain: str | None       — Filter venues by chain

Returns:
  {
    "best_quote": {
      "quote_id": "uuid",
      "venue_id": "xpmarket",
      "input_token": "XRP",
      "output_token": "USD",
      "input_amount": 100.0,
      "output_amount": 52.35,
      "exchange_rate": 0.5235,
      "price_impact_percent": 0.12,
      "venue_fee": 0.20,
      "mangrove_fee": 0.05,
      "total_cost": 100.25,
      "expires_at": "2026-02-15T00:05:00Z"
    },
    "all_quotes": [ ... ],
    "quotes_count": 1
  }

Errors:
  PAIR_NOT_SUPPORTED     — No venue supports this token pair
  AMOUNT_TOO_LOW         — Amount below venue minimum
  AMOUNT_TOO_HIGH        — Amount above venue maximum
  NO_LIQUIDITY           — Insufficient liquidity across all venues
  VENUE_NOT_FOUND        — Specified venue_id doesn't exist
```

#### dex_swap

Execute a swap using a previously obtained quote.

```
Parameters:
  quote_id: str        — UUID of the quote to execute
  wallet_seed: str     — Wallet seed for signing the transaction
  slippage_percent: float | None — Max acceptable slippage (default: 1.0%)

Returns:
  {
    "swap_id": "uuid",
    "quote_id": "uuid",
    "venue_id": "xpmarket",
    "status": "confirmed",
    "input_amount": 100.0,
    "output_amount": 52.30,
    "tx_hash": "XRPL_TX_HASH",
    "confirmed_at": "2026-02-15T00:01:00Z"
  }

Errors:
  QUOTE_NOT_FOUND      — No quote with this ID
  QUOTE_EXPIRED        — Quote has expired, get a new one
  INSUFFICIENT_BALANCE — Wallet doesn't have enough input_token
  SLIPPAGE_EXCEEDED    — Price moved beyond slippage tolerance
  SWAP_FAILED          — Transaction failed on-chain (includes chain error)
```

#### dex_swap_status

Check the status of a submitted swap.

```
Parameters:
  swap_id: str — UUID of the swap

Returns:
  {
    "swap_id": "uuid",
    "status": "confirmed",
    "tx_hash": "XRPL_TX_HASH",
    "input_amount": 100.0,
    "output_amount": 52.30,
    "confirmed_at": "2026-02-15T00:01:00Z"
  }

Errors:
  SWAP_NOT_FOUND — No swap with this ID
```

### 3.6 V1 Limitations

- Single-pair swaps only (no multi-hop routing across chains)
- No cross-chain bridging — agent must have assets on the target chain
- XPMarket (XRPL) is the only fully functional adapter
- Uniswap and Jupiter adapters return "not yet supported" stubs
- No limit orders — market swaps only

---

## 4. Wallet Management

### 4.1 Concepts

MangroveMarkets provides tools for agents to create and manage XRPL wallets. The agent owns the keys — MangroveMarkets never stores or logs wallet secrets.

### 4.2 Data Models

#### WalletInfo

```
WalletInfo:
  address: str (XRPL classic address, e.g., "rXXX...")
  seed: str (wallet seed — ONLY returned on creation, never stored)
  balance_xrp: float
  reserve_xrp: float (10 XRP base reserve)
  available_xrp: float (balance - reserve)
  is_funded: bool
  network: str ("testnet" | "devnet" | "mainnet")
```

#### Transaction

```
Transaction:
  tx_hash: str
  tx_type: str (e.g., "Payment", "EscrowCreate", "EscrowFinish", "OfferCreate")
  from_address: str
  to_address: str | None
  amount_xrp: float | None
  status: str ("tesSUCCESS" or error code)
  timestamp: datetime (UTC)
  fee_xrp: float
```

### 4.3 MCP Tools

#### wallet_create

Create a new XRPL wallet. On testnet/devnet, automatically funds from faucet.

```
Parameters:
  network: str | None — "testnet" (default), "devnet", or "mainnet"

Returns:
  {
    "address": "rXXX...",
    "seed": "sXXX...",
    "balance_xrp": 100.0,
    "reserve_xrp": 10.0,
    "available_xrp": 90.0,
    "is_funded": true,
    "network": "testnet",
    "warning": "Store your seed securely. MangroveMarkets will NEVER store or retrieve it."
  }

Errors:
  FAUCET_FAILED     — Testnet/devnet faucet request failed
  NETWORK_INVALID   — Unrecognized network
```

#### wallet_balance

Check wallet balance and reserve status.

```
Parameters:
  address: str          — XRPL address
  network: str | None   — "testnet" (default), "devnet", or "mainnet"

Returns:
  {
    "address": "rXXX...",
    "balance_xrp": 95.5,
    "reserve_xrp": 10.0,
    "available_xrp": 85.5,
    "is_funded": true,
    "network": "testnet"
  }

Errors:
  ACCOUNT_NOT_FOUND — Address doesn't exist on this network
  NETWORK_ERROR     — Could not connect to XRPL node
```

#### wallet_send

Send XRP to another address.

```
Parameters:
  sender_address: str    — Sender's XRPL address
  sender_seed: str       — Sender's wallet seed
  destination: str       — Recipient's XRPL address
  amount_xrp: float      — Amount to send
  network: str | None    — "testnet" (default)
  destination_tag: int | None — Optional destination tag

Returns:
  {
    "tx_hash": "HASH...",
    "status": "tesSUCCESS",
    "amount_xrp": 5.0,
    "fee_xrp": 0.000012,
    "from": "rXXX...",
    "to": "rYYY...",
    "new_balance_xrp": 90.5
  }

Errors:
  INSUFFICIENT_BALANCE  — Not enough XRP (message: "have X, need Y including reserve")
  INVALID_DESTINATION   — Destination address is malformed
  TRANSACTION_FAILED    — XRPL transaction failed (includes error code)
  NETWORK_ERROR         — Could not connect to XRPL node
```

#### wallet_transactions

List recent transactions for an address.

```
Parameters:
  address: str          — XRPL address
  network: str | None   — "testnet" (default)
  limit: int | None     — Max results (default: 20, max: 100)
  tx_type: str | None   — Filter by type ("Payment", "EscrowCreate", etc.)

Returns:
  {
    "address": "rXXX...",
    "transactions": [
      {
        "tx_hash": "HASH...",
        "tx_type": "Payment",
        "from_address": "rXXX...",
        "to_address": "rYYY...",
        "amount_xrp": 5.0,
        "status": "tesSUCCESS",
        "timestamp": "2026-02-15T00:00:00Z",
        "fee_xrp": 0.000012
      }
    ],
    "total_count": 15
  }

Errors:
  ACCOUNT_NOT_FOUND — Address doesn't exist on this network
  NETWORK_ERROR     — Could not connect to XRPL node
```

---

## 5. Integration Tools

### 5.1 Philosophy

MangroveMarkets provides free tools for agents to interact directly with external decentralized networks. MangroveMarkets does NOT proxy, broker, or resell these services — it provides the interface for agents to access them.

### 5.2 MCP Tools

#### integration_akash_deploy

Deploy compute on Akash Network.

```
Parameters:
  sdl: str              — Akash SDL (Stack Definition Language) manifest
  wallet_address: str   — Akash wallet address
  budget_akt: float     — Maximum AKT to spend

Returns:
  {
    "deployment_id": "...",
    "status": "pending",
    "provider": "...",
    "cost_per_block_akt": 0.001,
    "estimated_monthly_akt": 8.64
  }

Errors:
  INVALID_SDL          — SDL manifest is malformed
  INSUFFICIENT_AKT     — Not enough AKT balance
  NO_PROVIDERS         — No providers available for this workload
  AKASH_API_ERROR      — Akash network error
```

#### integration_bittensor_query

Query the Bittensor decentralized AI network.

```
Parameters:
  subnet_id: int         — Bittensor subnet to query
  query: str             — Query to send to the subnet
  timeout_seconds: int | None — Max wait time (default: 30)

Returns:
  {
    "subnet_id": 1,
    "response": "...",
    "miner_uid": 123,
    "response_time_ms": 450,
    "incentive_score": 0.85
  }

Errors:
  SUBNET_NOT_FOUND    — Invalid subnet ID
  QUERY_TIMEOUT       — Query timed out
  BITTENSOR_API_ERROR — Bittensor network error
```

#### integration_fetch_discover

Discover agents and services on Fetch.ai.

```
Parameters:
  service_type: str | None — Type of service to find
  query: str | None        — Search query

Returns:
  {
    "agents": [
      {
        "agent_address": "...",
        "name": "...",
        "description": "...",
        "service_type": "...",
        "protocols": ["..."]
      }
    ],
    "total_count": 5
  }

Errors:
  FETCH_API_ERROR — Fetch.ai network error
```

#### integration_nodes_status

Check Nodes.ai distributed infrastructure status.

```
Parameters:
  node_type: str | None — Filter by node type

Returns:
  {
    "nodes": [
      {
        "node_id": "...",
        "node_type": "gpu",
        "status": "online",
        "region": "us-east",
        "specs": { "gpu": "A100", "ram_gb": 80 }
      }
    ],
    "total_online": 42,
    "total_count": 50
  }

Errors:
  NODES_API_ERROR — Nodes.ai network error
```

---

## 6. Market Intelligence (Metrics)

### 6.1 What's Tracked

MangroveMarkets tracks marketplace and DEX activity to provide agents with market intelligence:

- **Request frequency** — How often each category/subcategory is searched
- **Average prices** — Price ranges and averages across categories
- **Demand trends** — Rising/falling demand over time windows
- **Volume and velocity** — Transaction volume and speed of sales
- **Seller reputation** — Aggregate ratings and transaction counts
- **DEX activity** — Swap volumes, popular pairs, price movements

### 6.2 Pricing

| Tier | Tool Calls | Cost |
|------|-----------|------|
| Free teaser | 50 calls | $0 |
| Standard | 500 calls | 10 XRP |

Usage is tracked per agent wallet address.

### 6.3 MCP Tools

#### metrics_market_overview

Get overall marketplace statistics.

```
Parameters:
  time_window: str | None — "24h", "7d", "30d" (default: "24h")

Returns:
  {
    "time_window": "24h",
    "total_listings": 1500,
    "active_listings": 800,
    "total_transactions": 120,
    "total_volume_xrp": 5000.0,
    "average_price_xrp": 41.67,
    "top_categories": [
      { "category": "data", "listing_count": 300, "volume_xrp": 1500.0 },
      { "category": "compute", "listing_count": 200, "volume_xrp": 2000.0 }
    ],
    "usage": { "calls_used": 5, "calls_remaining": 45, "tier": "free" }
  }

Errors:
  USAGE_LIMIT_EXCEEDED — Free tier exhausted (suggestion: "Fund 10 XRP for 500 more calls")
  INVALID_TIME_WINDOW  — Time window not recognized
```

#### metrics_category_trends

Get demand and supply trends for a specific category.

```
Parameters:
  category: str            — Category to analyze
  time_window: str | None  — "24h", "7d", "30d" (default: "7d")

Returns:
  {
    "category": "compute",
    "time_window": "7d",
    "search_count": 450,
    "listing_count": 200,
    "transaction_count": 85,
    "average_price_xrp": 25.0,
    "price_trend": "rising",
    "demand_supply_ratio": 2.25,
    "top_subcategories": [
      { "subcategory": "gpu", "search_count": 200, "avg_price_xrp": 50.0 }
    ],
    "top_tags": ["a100", "hourly", "inference"],
    "usage": { "calls_used": 6, "calls_remaining": 44, "tier": "free" }
  }

Errors:
  INVALID_CATEGORY      — Category not in allowed enum
  USAGE_LIMIT_EXCEEDED  — Tier limit reached
```

#### metrics_price_history

Get price history for a category or subcategory.

```
Parameters:
  category: str              — Category
  subcategory: str | None    — Optional subcategory
  time_window: str | None    — "24h", "7d", "30d", "90d" (default: "30d")
  interval: str | None       — "1h", "1d", "1w" (default: "1d")

Returns:
  {
    "category": "data",
    "subcategory": null,
    "time_window": "30d",
    "interval": "1d",
    "data_points": [
      {
        "timestamp": "2026-02-01T00:00:00Z",
        "avg_price_xrp": 10.5,
        "min_price_xrp": 1.0,
        "max_price_xrp": 100.0,
        "transaction_count": 15,
        "volume_xrp": 157.5
      }
    ],
    "usage": { "calls_used": 7, "calls_remaining": 43, "tier": "free" }
  }

Errors:
  INVALID_CATEGORY      — Category not in allowed enum
  INVALID_INTERVAL      — Interval not recognized
  USAGE_LIMIT_EXCEEDED  — Tier limit reached
```

---

## 7. Error Contract

All MCP tools follow a consistent error response pattern.

### 7.1 Success Response

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

Success responses contain the data directly — no wrapper.

### 7.2 Error Response

```json
{
  "error": true,
  "code": "INSUFFICIENT_XRP_BALANCE",
  "message": "Insufficient XRP balance: have 5.0 XRP, need 10.0 XRP (including 10.0 XRP reserve)",
  "suggestion": "Fund your wallet with at least 5.0 more XRP using wallet_send or request from faucet"
}
```

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `error` | bool | Always `true` for errors |
| `code` | str | Machine-readable error code (UPPER_SNAKE_CASE) |
| `message` | str | Agent-readable description with specific values |
| `suggestion` | str | Actionable next step the agent can take |

### 7.3 Error Code Conventions

Error codes are namespaced by domain:
- General: `INVALID_*`, `NOT_FOUND`, `NOT_AUTHORIZED`, `NETWORK_ERROR`
- Marketplace: `LISTING_*`, `OFFER_*`, `ESCROW_*`, `CONTENT_*`
- DEX: `PAIR_*`, `QUOTE_*`, `SWAP_*`, `VENUE_*`, `SLIPPAGE_*`
- Wallet: `ACCOUNT_*`, `TRANSACTION_*`, `FAUCET_*`, `INSUFFICIENT_*`
- Metrics: `USAGE_*`
- Integration: `*_API_ERROR`

---

## 8. Authentication and Authorization

### 8.1 Agent Authentication

Agents authenticate to MangroveMarkets via one of:
- **API key** — Generated on first connection, tied to an agent identifier
- **JWT token** — Short-lived token obtained via API key exchange
- **Wallet signature** — XRPL wallet signs a challenge to prove ownership

V1 uses API key authentication. JWT and wallet signature are v2.

### 8.2 Authorization Rules

- **No KYC, no gatekeeping** — any agent with a valid API key can participate
- **Wallet ownership** — operations on a listing/offer require the caller to prove they own the associated wallet (via wallet_seed parameter in v1, signature challenge in v2)
- **Rate limiting** — per-API-key rate limits to prevent abuse (1000 calls/hour for tools, metrics have their own metering)

### 8.3 Security Invariants

- MangroveMarkets NEVER stores wallet seeds or secrets
- Wallet seeds are accepted as tool parameters, used for transaction signing, and immediately discarded
- All XRPL communication uses TLS
- Escrow operations are atomic on XRPL — MangroveMarkets cannot steal escrowed funds

---

## 9. Revenue Model

| Source | Mechanism | Pricing | Implementation |
|--------|-----------|---------|---------------|
| Marketplace | Fee on escrow settlement | 1% of transaction (configurable) | Deducted when escrow is released to seller |
| DEX Aggregator | Routing fee on swaps | 0.05% of swap amount (configurable) | Added to quoted total_cost |
| Market Intelligence | Tool call metering | 10 XRP / 500 calls (free teaser: 50) | Usage counter per wallet address |
| Integration tools | Free | $0 | Drives marketplace/DEX adoption |
| Wallet tooling | Free | $0 | Enables marketplace participation |

### 9.1 Fee Collection

- Marketplace fees: Deducted from escrow amount before releasing to seller. Seller sees `price - fee` in their wallet.
- DEX fees: Added to the quote's `mangrove_fee` field. Agent sees total cost before confirming swap.
- Metrics fees: Pre-paid. Agent sends 10 XRP to MangroveMarkets wallet, receives 500 call credits.

---

## 10. Non-Functional Requirements

### 10.1 Performance

- MCP tool response time: < 2 seconds for non-blockchain operations
- XRPL operations: < 10 seconds (dependent on ledger close time ~3-5s)
- Search operations: < 500ms for up to 10,000 listings

### 10.2 Availability

- MCP server: 99.9% uptime target
- Health check endpoint: `/health` returns status + timestamp
- Graceful degradation: if a DEX venue is down, other venues still work

### 10.3 Data Persistence

- Listings, offers, ratings: PostgreSQL
- Metrics data: PostgreSQL (consider TimescaleDB for time-series in v2)
- Session/cache data: In-memory (v1), Redis (v2)
- Blockchain data: XRPL (source of truth for escrow state)

### 10.4 Security

- No wallet secret storage
- All secrets via environment variables or GCP Secret Manager
- XRPL testnet for development, mainnet for production
- Input validation on all tool parameters (Pydantic)
- SQL injection prevention (parameterized queries)

---

## 11. Out of Scope (V1)

These are explicitly NOT in v1:

- Cross-chain bridging
- Multi-hop DEX routing
- Dispute resolution (beyond escrow cancellation)
- Human-facing UI/dashboard
- Limit orders on DEX
- Subscription-based marketplace listings
- Agent identity verification beyond wallet ownership
- Content moderation
- Real-time WebSocket feeds
- Mobile/desktop clients
