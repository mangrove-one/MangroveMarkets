# DEX Aggregator Configuration

This project ships a minimal DEX aggregator with the following venues:

- **XPMarket (XRPL testnet)** — functional quotes for XRP pairs (testnet-only).
- **Uniswap v3 (Sepolia)** — stubbed adapter; venue + pairs exposed.
- **Jupiter (Solana devnet)** — stubbed adapter; venue + pairs exposed.

## Required / Optional Environment Variables

The current implementation is testnet-focused and uses placeholders for future on-chain integrations.

| Variable | Purpose | Default |
| --- | --- | --- |
| `XRPL_TESTNET_RPC_URL` | XRPL testnet JSON-RPC endpoint for XPMarket | `https://s.altnet.rippletest.net:51234` |
| `SEPOLIA_RPC_URL` | Ethereum Sepolia RPC endpoint for Uniswap v3 | _(empty)_ |
| `JUPITER_DEVNET_API_URL` | Jupiter devnet quote API base URL | `https://quote-api.jup.ag/v6` |

## Wrapped BTC (Testnet Routes)

The minimum venue coverage includes wrapped BTC routes on Ethereum and Solana testnets:

- **Uniswap v3 (Sepolia):** `WBTC/ETH`, `WBTC/USDC`
- **Jupiter (Solana devnet):** `WBTC/SOL`, `WBTC/USDC`

These pairs are surfaced via `dex_supported_pairs`, even though quoting/swapping is stubbed for now.
