"""Wallet management tools — registered on the main MCP server with wallet_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.mcp.errors import tool_error, tool_success
from src.wallet.service import create_wallet


def register(server: FastMCP) -> None:
    """Register all wallet tools on the given MCP server."""

    @server.tool(name="wallet_create")
    async def create(network: str = "testnet") -> str:
        """Create a new XRPL wallet. On testnet/devnet, auto-funds from faucet."""
        try:
            return tool_success(create_wallet(network=network))
        except ValueError as exc:
            return tool_error("INVALID_NETWORK", str(exc), "Use the configured XRPL network.")
        except Exception as exc:  # pragma: no cover - defensive
            return tool_error("WALLET_CREATE_FAILED", "Failed to create wallet", str(exc))

    @server.tool(name="wallet_balance")
    async def balance(address: str, network: str = "testnet") -> str:
        """Check wallet balance and reserve status."""
        return tool_error("NOT_IMPLEMENTED", "wallet_balance not yet implemented", "Coming in Phase 1")

    @server.tool(name="wallet_send")
    async def send(
        sender_address: str,
        sender_seed: str,
        destination: str,
        amount_xrp: float,
        network: str = "testnet",
    ) -> str:
        """Send XRP to another address."""
        return tool_error("NOT_IMPLEMENTED", "wallet_send not yet implemented", "Coming in Phase 1")

    @server.tool(name="wallet_transactions")
    async def transactions(
        address: str,
        network: str = "testnet",
        limit: int = 20,
    ) -> str:
        """List recent transactions for an address."""
        return tool_error("NOT_IMPLEMENTED", "wallet_transactions not yet implemented", "Coming in Phase 1")
