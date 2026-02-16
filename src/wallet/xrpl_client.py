"""XRPL client wrapper for wallet operations."""
from xrpl.clients import JsonRpcClient

from src.shared.config import app_config


class XRPLClient:
    """Lightweight XRPL client wrapper with network validation."""

    def __init__(self, network: str = "testnet") -> None:
        configured_network = str(getattr(app_config, "XRPL_NETWORK", "testnet")).lower()
        requested_network = str(network).lower()
        if requested_network != configured_network:
            raise ValueError(
                "Unsupported XRPL network: "
                f"{requested_network}. Configured network is {configured_network}."
            )
        self.network = requested_network
        self.url = app_config.XRPL_NODE_URL
        self.client = JsonRpcClient(self.url)
