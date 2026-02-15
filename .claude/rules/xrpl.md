# XRPL Rules

## Network Usage

- Development: Use XRPL Testnet or Devnet
- Never hardcode mainnet credentials or wallet seeds in source code
- Wallet seeds and secrets must come from environment variables or secure config

## Transactions

- Always validate transaction results — check for `tesSUCCESS`
- Use XRPL native escrow for marketplace settlements
- Use XRPL native DEX (order book) via XPMarket integration
- Respect reserve requirements when creating wallets (currently 10 XRP base reserve)

## Wallet Management

- Agents must have an XRP wallet to use the marketplace
- Mangrove provides tools to create wallets — the agent owns the keys
- Never store or log wallet secrets
- Use xrpl.js as the primary XRPL client library

## References

- XRPL docs: https://xrpl.org/docs
- xrpl.js: https://js.xrpl.org/
- XRPL testnet faucet: https://faucet.altnet.rippletest.net/
