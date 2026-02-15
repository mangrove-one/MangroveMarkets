"""Marketplace tools — registered on the main MCP server with marketplace_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.mcp.errors import tool_error


def register(server: FastMCP) -> None:
    """Register all marketplace tools on the given MCP server."""

    @server.tool(name="marketplace_create_listing")
    async def create_listing(
        seller_address: str,
        title: str,
        description: str,
        category: str,
        price_xrp: float,
        listing_type: str = "static",
        storage_uri: str | None = None,
        content_hash: str | None = None,
        subcategory: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a new listing on the Mangrove Marketplace."""
        # TODO: implement in Phase 2
        return tool_error("NOT_IMPLEMENTED", "marketplace_create_listing not yet implemented", "Coming in Phase 2")

    @server.tool(name="marketplace_search")
    async def search(
        query: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        listing_type: str | None = None,
        limit: int = 20,
    ) -> str:
        """Search the Mangrove Marketplace for listings."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_search not yet implemented", "Coming in Phase 2")

    @server.tool(name="marketplace_get_listing")
    async def get_listing(listing_id: str) -> str:
        """Get full details of a specific listing."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_get_listing not yet implemented", "Coming in Phase 2")

    @server.tool(name="marketplace_make_offer")
    async def make_offer(listing_id: str, buyer_address: str) -> str:
        """Make an offer on a marketplace listing."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_make_offer not yet implemented", "Coming in Phase 3")

    @server.tool(name="marketplace_accept_offer")
    async def accept_offer(offer_id: str, seller_address: str) -> str:
        """Accept an offer, creating XRPL escrow."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_accept_offer not yet implemented", "Coming in Phase 3")

    @server.tool(name="marketplace_confirm_delivery")
    async def confirm_delivery(offer_id: str, buyer_address: str) -> str:
        """Confirm delivery and release escrow to seller."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_confirm_delivery not yet implemented", "Coming in Phase 3")

    @server.tool(name="marketplace_rate")
    async def rate(offer_id: str, rater_address: str, score: int, comment: str | None = None) -> str:
        """Rate a completed marketplace transaction."""
        return tool_error("NOT_IMPLEMENTED", "marketplace_rate not yet implemented", "Coming in Phase 3")
