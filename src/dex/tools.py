"""DEX aggregator tools — registered on the main MCP server with dex_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.mcp.errors import tool_error


def register(server: FastMCP) -> None:
    """Register all DEX tools on the given MCP server."""

    @server.tool(name="dex_supported_venues")
    async def supported_venues() -> str:
        """List all supported DEX venues and their status."""
        return tool_error("NOT_IMPLEMENTED", "dex_supported_venues not yet implemented", "Coming in Phase 4")

    @server.tool(name="dex_supported_pairs")
    async def supported_pairs(venue_id: str) -> str:
        """List tradeable pairs for a specific DEX venue."""
        return tool_error("NOT_IMPLEMENTED", "dex_supported_pairs not yet implemented", "Coming in Phase 4")

    @server.tool(name="dex_get_quote")
    async def get_quote(
        input_token: str,
        output_token: str,
        amount: float,
        venue_id: str | None = None,
    ) -> str:
        """Get the best swap quote across all venues."""
        return tool_error("NOT_IMPLEMENTED", "dex_get_quote not yet implemented", "Coming in Phase 4")

    @server.tool(name="dex_swap")
    async def swap(
        quote_id: str,
        wallet_seed: str,
        slippage_percent: float = 1.0,
    ) -> str:
        """Execute a swap using a previously obtained quote."""
        return tool_error("NOT_IMPLEMENTED", "dex_swap not yet implemented", "Coming in Phase 4")

    @server.tool(name="dex_swap_status")
    async def swap_status(swap_id: str) -> str:
        """Check the status of a submitted swap."""
        return tool_error("NOT_IMPLEMENTED", "dex_swap_status not yet implemented", "Coming in Phase 4")
