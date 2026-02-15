"""MangroveMarkets MCP Server — unified entry point for all agent tools."""
from mcp.server.fastmcp import FastMCP

# Create the main server instance — all domains register tools directly on this
mcp = FastMCP("MangroveMarkets")


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all domain tools registered.

    Each domain's tools.py exports a register(server) function that adds
    its tools to the main server with the appropriate namespace prefix
    (marketplace_, dex_, wallet_, integration_, metrics_).
    """
    from src.marketplace.tools import register as register_marketplace
    from src.dex.tools import register as register_dex
    from src.wallet.tools import register as register_wallet
    from src.integrations.tools import register as register_integrations
    from src.metrics.tools import register as register_metrics

    register_marketplace(mcp)
    register_dex(mcp)
    register_wallet(mcp)
    register_integrations(mcp)
    register_metrics(mcp)

    return mcp
