"""Market intelligence tools — registered on the main MCP server with metrics_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.mcp.errors import tool_error


def register(server: FastMCP) -> None:
    """Register all metrics tools on the given MCP server."""

    @server.tool(name="metrics_market_overview")
    async def market_overview(time_window: str = "24h") -> str:
        """Get overall marketplace statistics."""
        return tool_error("NOT_IMPLEMENTED", "metrics_market_overview not yet implemented", "Coming in Phase 6")

    @server.tool(name="metrics_category_trends")
    async def category_trends(category: str, time_window: str = "7d") -> str:
        """Get demand and supply trends for a specific category."""
        return tool_error("NOT_IMPLEMENTED", "metrics_category_trends not yet implemented", "Coming in Phase 6")

    @server.tool(name="metrics_price_history")
    async def price_history(category: str, time_window: str = "30d", interval: str = "1d") -> str:
        """Get price history for a category or subcategory."""
        return tool_error("NOT_IMPLEMENTED", "metrics_price_history not yet implemented", "Coming in Phase 6")
