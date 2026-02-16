"""DEX aggregator tools — registered on the main MCP server with dex_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.dex.errors import DexError
from src.dex.service import DexService
from src.mcp.errors import tool_error, tool_success


def register(server: FastMCP) -> None:
    """Register all DEX tools on the given MCP server."""
    service = DexService()

    @server.tool(name="dex_supported_venues")
    async def supported_venues() -> str:
        """List all supported DEX venues and their status."""
        try:
            venues = await service.supported_venues()
            return tool_success({"venues": [venue.model_dump() for venue in venues]})
        except DexError as exc:
            return tool_error(exc.code, exc.message, exc.suggestion)

    @server.tool(name="dex_supported_pairs")
    async def supported_pairs(venue_id: str) -> str:
        """List tradeable pairs for a specific DEX venue."""
        try:
            pairs = await service.supported_pairs(venue_id)
            return tool_success({"pairs": [pair.model_dump() for pair in pairs]})
        except DexError as exc:
            return tool_error(exc.code, exc.message, exc.suggestion)

    @server.tool(name="dex_get_quote")
    async def get_quote(
        input_token: str,
        output_token: str,
        amount: float,
        venue_id: str | None = None,
    ) -> str:
        """Get the best swap quote across all venues."""
        try:
            quote = await service.get_quote(input_token, output_token, amount, venue_id=venue_id)
            return tool_success(quote)
        except DexError as exc:
            return tool_error(exc.code, exc.message, exc.suggestion)

    @server.tool(name="dex_swap")
    async def swap(
        quote_id: str,
        wallet_seed: str,
        slippage_percent: float = 1.0,
    ) -> str:
        """Execute a swap using a previously obtained quote."""
        try:
            return tool_success({"swap_id": await service.swap(quote_id, wallet_seed)})
        except DexError as exc:
            return tool_error(exc.code, exc.message, exc.suggestion)

    @server.tool(name="dex_swap_status")
    async def swap_status(swap_id: str) -> str:
        """Check the status of a submitted swap."""
        try:
            return tool_success({"status": await service.swap_status(swap_id)})
        except DexError as exc:
            return tool_error(exc.code, exc.message, exc.suggestion)
