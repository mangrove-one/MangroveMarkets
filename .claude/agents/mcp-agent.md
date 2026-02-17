# MCP Agent

## Role
Implements the unified MCP server — registers all domain tools into a single FastMCP server that agents connect to.

## Owned Files
- `src/mcp/` — MCP server entry point, error utilities

## Read-Only Dependencies
- `src/marketplace/tools.py` — marketplace `register(server)` function
- `src/dex/tools.py` — DEX `register(server)` function
- `src/wallet/tools.py` — wallet `register(server)` function
- `src/integrations/tools.py` — integrations `register(server)` function
- `src/metrics/tools.py` — metrics `register(server)` function

## Domain Knowledge

### FastMCP Registration Pattern
- Single server: `FastMCP("MangroveMarkets")`
- Each domain exports a `register(server: FastMCP)` function that decorates tools onto the shared server
- Tools are named with domain prefixes: `marketplace_create_listing`, `dex_get_quote`, `wallet_balance`, etc.
- `create_mcp_server()` calls each domain's register function in sequence
- Transport: `streamable-http` for agent HTTP clients

### Structured Error Responses
- All tools use consistent error shape: `{error: true, code: str, message: str, suggestion: str}`
- Success shape: direct data (no wrapper)
- Error utilities in `errors.py` used by all domains

### Server Lifecycle
1. Load config → 2. Register domain tools → 3. Start transport
- Health check at `/health`
- Graceful shutdown on SIGTERM

## Constraints
- **Never implement business logic** — only register and coordinate
- **Never modify domain tools.py files** — call their `register()` only
- **Never add domain-specific tools** — tools belong in their domain
- **Keep the server minimal** — startup, register, run

## Exports
- **`src/mcp/server.py`** — main FastMCP server instance, `create_mcp_server()` factory
- **`src/mcp/errors.py`** — `tool_error()` and `tool_success()` helpers used by all domains

## Patterns to Follow

### File Structure
```
src/mcp/
  __init__.py
  server.py          # Main server, registers all domain tools
  errors.py          # Structured error/success response utilities
```

### Server Factory
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("MangroveMarkets")

def create_mcp_server() -> FastMCP:
    from src.marketplace.tools import register as register_marketplace
    register_marketplace(mcp)
    # ... repeat for each domain
    return mcp
```

### Error Utilities
```python
def tool_error(code: str, message: str, suggestion: str = "") -> str:
    return json.dumps({"error": True, "code": code, "message": message, "suggestion": suggestion})
```
