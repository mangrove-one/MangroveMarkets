"""Wallet operations for XRPL."""
from __future__ import annotations

from typing import Any

from xrpl.wallet import Wallet, generate_faucet_wallet

from src.wallet.xrpl_client import XRPLClient


def create_wallet(network: str = "testnet") -> dict[str, Any]:
    """Create a new XRPL wallet, funded on testnet/devnet via faucet."""
    xrpl_client = XRPLClient(network=network)
    normalized_network = xrpl_client.network

    if normalized_network in {"testnet", "devnet"}:
        wallet = generate_faucet_wallet(xrpl_client.client, debug=False)
        is_funded = True
    else:
        wallet = Wallet.create()
        is_funded = False

    secret = wallet.seed
    seed_phrase = getattr(wallet, "seed_phrase", None)

    warnings = [
        "IMPORTANT: Save your wallet secret now. It will not be stored by Mangrove.",
        "Anyone with this secret can access your funds. Do not share it.",
        "Store secrets offline in a secure password manager or hardware wallet.",
    ]

    return {
        "address": wallet.classic_address,
        "secret": secret,
        "seed_phrase": seed_phrase,
        "network": normalized_network,
        "is_funded": is_funded,
        "warnings": warnings,
    }
