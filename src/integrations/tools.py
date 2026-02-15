"""External integration tools — registered on the main MCP server with integration_ prefix."""
from mcp.server.fastmcp import FastMCP

from src.mcp.errors import tool_error


def register(server: FastMCP) -> None:
    """Register all integration tools on the given MCP server."""

    @server.tool(name="integration_akash_deploy")
    async def akash_deploy(sdl: str, wallet_address: str, budget_akt: float) -> str:
        """Deploy compute on Akash Network."""
        return tool_error("NOT_IMPLEMENTED", "integration_akash_deploy not yet implemented", "Coming in Phase 7")

    @server.tool(name="integration_bittensor_query")
    async def bittensor_query(subnet_id: int, query: str, timeout_seconds: int = 30) -> str:
        """Query the Bittensor decentralized AI network."""
        return tool_error("NOT_IMPLEMENTED", "integration_bittensor_query not yet implemented", "Coming in Phase 7")

    @server.tool(name="integration_fetch_discover")
    async def fetch_discover(service_type: str | None = None, query: str | None = None) -> str:
        """Discover agents and services on Fetch.ai."""
        return tool_error("NOT_IMPLEMENTED", "integration_fetch_discover not yet implemented", "Coming in Phase 7")

    @server.tool(name="integration_nodes_status")
    async def nodes_status(node_type: str | None = None) -> str:
        """Check Nodes.ai distributed infrastructure status."""
        return tool_error("NOT_IMPLEMENTED", "integration_nodes_status not yet implemented", "Coming in Phase 7")
