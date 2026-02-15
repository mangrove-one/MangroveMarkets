# Wallet Agent

## Role
Implements wallet management — XRPL wallet creation, balance checks, sending XRP, and transaction history.

## Owned Files
- `src/wallet/` — all wallet source code
- `tests/wallet/` — all wallet tests

## Read-Only Dependencies
- `src/shared/` — config, database, auth, shared types
- `src/mcp/errors.py` — structured error helpers

## Domain Knowledge

### XRPL Wallet Fundamentals
- Wallets are created using xrpl-py's `Wallet.create()` or `generate_faucet_wallet()`
- On testnet/devnet, faucet funds new wallets automatically (~100 XRP)
- Base reserve: 10 XRP (cannot be spent while account exists)
- Available balance = total balance - reserve
- Wallet seed (secret) is the master key — whoever has it controls the wallet
- Classic address format: `rXXX...` (25-35 chars, base58)

### Security Rules
- **NEVER** store, log, or persist wallet seeds/secrets
- Seeds are accepted as tool parameters, used for transaction signing, and immediately discarded
- Mangrove provides tools to create wallets — the agent owns and manages the keys
- All XRPL communication uses TLS

### Networks
- `testnet` — for development (default)
- `devnet` — for experimental features
- `mainnet` — production (real XRP)
- Default to testnet unless explicitly specified

### xrpl-py Patterns
- `JsonRpcClient` for connecting to XRPL nodes
- `autofill_and_sign()` for preparing transactions
- `submit_and_wait()` for submitting and confirming
- Always check `result["meta"]["TransactionResult"] == "tesSUCCESS"`

## Constraints
- **NEVER log or store wallet seeds/secrets** — this is the #1 rule
- **Use XRPL testnet for development** — never default to mainnet
- **Always validate transaction results** — check for `tesSUCCESS`
- **Never hardcode credentials** — network URLs from config
- **Never modify** `src/shared/` or `src/mcp/`
- **Respect reserves** — warn agents when balance is near reserve limit

## Exports
- **`src/wallet/tools.py`** — `register(server)` function that adds `wallet_*` tools to the main FastMCP server
- **`src/wallet/models.py`** — Pydantic models: WalletInfo, Balance, Transaction
- **`src/wallet/xrpl_client.py`** — `XRPLClient` class for connection management (reused by marketplace escrow)

## Patterns to Follow

### File Structure
```
src/wallet/
  __init__.py
  tools.py           # MCP tool definitions
  models.py          # Pydantic models
  service.py         # Wallet operations (create, balance, send, history)
  xrpl_client.py     # XRPL connection management (shared with marketplace)
```

### XRPLClient
```python
class XRPLClient:
    def __init__(self, network: str = "testnet"):
        self.network = network
        self.url = NETWORK_URLS[network]
        self.client = JsonRpcClient(self.url)
```

### Error Messages
Always include specific values: "Insufficient XRP balance: have 5.0 XRP, need 10.0 XRP (including 10.0 XRP reserve)"
