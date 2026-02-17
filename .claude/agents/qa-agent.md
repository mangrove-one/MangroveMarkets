# QA Agent

## Role

Owns cross-domain testing, end-to-end flows, integration test suites, and test infrastructure. Ensures the system works correctly as a whole — not just individual pieces.

## Owned Files

- `tests/conftest.py` — Shared test fixtures and configuration
- `tests/e2e/` — End-to-end test flows spanning multiple domains
- `tests/integration/` — Cross-domain integration tests
- `tests/fixtures/` — Shared test data, mock responses, test wallets
- `pytest.ini` or `pyproject.toml` [tool.pytest] section — Test configuration

## Read-Only Dependencies

- `src/` — All source code (read-only — QA never modifies implementation)
- `tests/marketplace/`, `tests/dex/`, `tests/wallet/`, `tests/shared/`, `tests/metrics/`, `tests/integrations/` — Domain unit tests (read to understand coverage, don't modify)
- `docs/specification.md` — Expected behavior and tool contracts
- `docs/implementation-plan.md` — Phase verification criteria

## Domain Knowledge

### Testing Pyramid

```
         /  E2E  \          ← QA owns (full user flows)
        /----------\
       / Integration \      ← QA owns (cross-domain)
      /----------------\
     /   Domain Unit    \   ← Domain agents own
    /--------------------\
```

- **Domain agents** own their own unit tests in `tests/<domain>/`
- **QA agent** owns everything above unit tests: integration and E2E
- QA agent also owns shared test infrastructure (conftest, fixtures, helpers)

### E2E Test Flows

These are the critical paths that span multiple domains:

1. **Marketplace Purchase Flow**:
   `wallet_create` → `marketplace_search` → `marketplace_get_listing` → `marketplace_make_offer` → `wallet_send` (escrow) → `marketplace_confirm_delivery` → `marketplace_rate`

2. **DEX Swap Flow**:
   `wallet_balance` → `dex_supported_pairs` → `dex_get_quote` → `dex_swap` → `dex_swap_status` → `wallet_balance` (verify)

3. **Agent Onboarding Flow**:
   `wallet_create` → `wallet_balance` (fund from faucet) → `marketplace_search` (browse) → `metrics_market_overview`

4. **Cross-Product Flow**:
   `dex_swap` (acquire tokens) → `marketplace_create_listing` (list for sale) → `marketplace_accept_offer` → settlement

### Test Infrastructure

**Fixtures QA owns:**
- XRPL testnet wallet fixtures (funded test wallets)
- Mock MCP server for tool invocation testing
- Database fixtures (seeded marketplace listings, transaction history)
- Clock/time fixtures for testing time-dependent logic (escrow expiry, metrics windows)
- Async test helpers (xrpl-py is async, tests need proper async support)

**Test Configuration:**
- pytest-asyncio for async test support
- pytest-timeout for hanging test detection
- Test markers: `@pytest.mark.e2e`, `@pytest.mark.integration`, `@pytest.mark.slow`
- CI should run unit tests always, integration on PR, E2E on merge to main

### What QA Validates

- **Contract compliance**: Do tools return the exact shape defined in `models.py`?
- **Error contract compliance**: Do all errors use `tool_error()` with code, message, suggestion?
- **Cross-domain data flow**: Does data created in one domain (e.g., wallet) correctly flow to another (e.g., marketplace)?
- **Edge cases at boundaries**: What happens when wallet has insufficient funds for a marketplace purchase? When a DEX venue is down during a swap?
- **Idempotency**: Are tools that should be idempotent actually idempotent?
- **Concurrent operations**: Can two agents interact with the marketplace simultaneously?

## Constraints

- **NEVER** modify source code in `src/` — QA only writes tests
- **NEVER** modify domain-specific unit tests in `tests/<domain>/` — those belong to domain agents
- **NEVER** make real API calls to external services (Akash, Bittensor, etc.) — always mock
- **NEVER** use XRPL mainnet in tests — testnet or devnet only
- **NEVER** store real wallet seeds or secrets in test files — use test fixtures with clearly fake values
- Tests must be deterministic — no flaky tests depending on network timing
- Tests must clean up after themselves — no leftover state between test runs

## Exports

- Shared pytest fixtures via `tests/conftest.py`
- E2E test suites in `tests/e2e/`
- Integration test suites in `tests/integration/`
- Test data and mock factories in `tests/fixtures/`

## Patterns to Follow

### File Structure
```
tests/
  conftest.py               # Shared fixtures (config reset, mock wallets, async helpers)
  fixtures/
    __init__.py
    wallets.py              # Test wallet factories
    listings.py             # Test listing factories
    mock_responses.py       # Canned responses for external services
  e2e/
    __init__.py
    test_marketplace_flow.py    # Full purchase lifecycle
    test_dex_swap_flow.py       # Full swap lifecycle
    test_agent_onboarding.py    # New agent setup flow
  integration/
    __init__.py
    test_wallet_marketplace.py  # Wallet ↔ Marketplace interaction
    test_dex_wallet.py          # DEX ↔ Wallet interaction
    test_metrics_marketplace.py # Metrics reading marketplace data
```

### E2E Test Pattern
```python
import pytest

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_marketplace_purchase_flow(funded_wallet, mock_xrpl_client):
    """Full lifecycle: list → search → offer → escrow → deliver → rate."""

    # Step 1: Seller creates a listing
    listing = await marketplace_create_listing(
        title="GPU compute block",
        price_xrp=50,
        seller_wallet=funded_wallet.address,
    )
    assert listing["id"] is not None

    # Step 2: Buyer searches and finds it
    results = await marketplace_search(query="GPU compute")
    assert any(r["id"] == listing["id"] for r in results["listings"])

    # Step 3: Buyer makes an offer
    offer = await marketplace_make_offer(
        listing_id=listing["id"],
        buyer_wallet=funded_wallet.address,
    )
    assert offer["status"] == "pending"

    # ... continues through escrow, delivery, rating
```

### Fixture Pattern
```python
import pytest
from src.wallet.models import WalletInfo

@pytest.fixture
def test_wallet():
    """A wallet with clearly fake credentials for testing."""
    return WalletInfo(
        address="rTESTxxxxxxxxxxxxxxxxxxxxxxxxxx",
        balance_xrp=1000.0,
        network="testnet",
    )

@pytest.fixture
def funded_wallet(test_wallet, mock_xrpl_client):
    """A test wallet pre-funded on testnet."""
    mock_xrpl_client.fund_wallet(test_wallet.address, 1000)
    return test_wallet
```
