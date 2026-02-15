---
name: testnet
description: Set up or verify XRPL testnet configuration for development
disable-model-invocation: true
---

Check and verify the XRPL testnet development setup:

1. Confirm xrpl.js is installed (check package.json)
2. Verify testnet/devnet configuration exists (not mainnet)
3. Check if there's a funded testnet wallet available for development
4. If no testnet wallet exists, offer to create one using the XRPL testnet faucet

Follow all rules in `.claude/rules/xrpl.md` — never touch mainnet, never log secrets.

Report the current state and any actions needed.
