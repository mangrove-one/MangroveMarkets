# Integration Agent

## Role

Implements tools for agents to interact directly with external decentralized services — Akash, Bittensor, Fetch.ai, and Nodes.ai. Mangrove provides access, not intermediation.

## Owned Files

- `src/integrations/` — All integration tool implementations
- `tests/integrations/` — Integration tests for external service adapters

## Read-Only Dependencies

- `src/shared/config.py` — Configuration (API endpoints, network settings)
- `src/shared/types.py` — Base models, shared types
- `src/mcp/errors.py` — `tool_error()` and `tool_success()` helpers
- `src/mcp/server.py` — Tool registration pattern (for reference)
- `docs/specification.md` — Tool specifications and expected behavior
- `docs/vision.md` — Mangrove does NOT intermediate — tools give agents direct access

## Domain Knowledge

### Core Principle

Mangrove is **not a broker, proxy, or reseller**. Integration tools give agents the information and access they need to interact with external services directly. The agent makes the decisions and executes the transactions — Mangrove just provides the interface.

### Services

#### Akash Network (Decentralized Compute)
- **What it does**: Decentralized cloud compute marketplace. Agents can deploy containers, rent GPU/CPU.
- **Tool**: `integration_akash_deploy` — Deploy a workload to Akash
- **Key concepts**: SDL (Stack Definition Language), bids, leases, providers
- **SDK/API**: Akash CLI or REST API
- **Agent use case**: "I need 4 GPUs for 2 hours to fine-tune a model"

#### Bittensor (Decentralized AI)
- **What it does**: Decentralized AI network. Subnets provide specialized AI services (text, image, data).
- **Tool**: `integration_bittensor_query` — Query a Bittensor subnet
- **Key concepts**: Subnets, miners, validators, TAO token, subnet endpoints
- **SDK/API**: bittensor Python SDK
- **Agent use case**: "Query subnet 1 for text generation" or "Check miner performance on subnet 18"

#### Fetch.ai (Agent Framework)
- **What it does**: Agent-to-agent communication and service discovery framework.
- **Tool**: `integration_fetch_discover` — Discover Fetch.ai agents/services
- **Key concepts**: Agents, services, Almanac contract, uAgents framework
- **SDK/API**: fetchai Python SDK / REST APIs
- **Agent use case**: "Find agents offering weather data services"

#### Nodes.ai (Distributed Infrastructure)
- **What it does**: Distributed node infrastructure. Status monitoring and health checks.
- **Tool**: `integration_nodes_status` — Check infrastructure node status
- **Key concepts**: Nodes, clusters, health metrics, uptime
- **SDK/API**: REST API
- **Agent use case**: "Is my inference node healthy? What's the uptime?"

### Error Handling

External services are unreliable. Every integration tool must handle:
- **Timeouts**: Set reasonable timeouts (30s default), return clear timeout errors
- **Rate limiting**: Detect 429s, return `RATE_LIMITED` with retry-after info
- **Service unavailable**: Return `SERVICE_UNAVAILABLE` with which service and why
- **Auth failures**: Return `AUTH_FAILED` with what credential is needed
- **Network errors**: Return `NETWORK_ERROR` with actionable suggestion

### Response Format

All integration tools return structured responses via `tool_success()`:
```python
{
    "service": "akash",           # Which service
    "action": "deploy",           # What was attempted
    "status": "success",          # success | error | pending
    "data": { ... },              # Service-specific response data
    "metadata": {
        "latency_ms": 1200,       # How long the call took
        "endpoint": "...",        # Which endpoint was hit
        "timestamp": "..."        # When the call was made
    }
}
```

## Constraints

- **NEVER** proxy, broker, or resell external services — provide tools for direct access
- **NEVER** store external service credentials — agents provide their own
- **NEVER** make financial commitments on behalf of agents (e.g., don't auto-bid on Akash leases)
- **NEVER** modify files outside `src/integrations/` and `tests/integrations/`
- **NEVER** cache sensitive data from external services (API keys, session tokens)
- Each integration must work independently — failure in one service must not affect others
- All external API calls must have timeouts configured
- Mock all external services in tests — never make real API calls in test suite

## Exports

- `register(server: FastMCP)` function in `src/integrations/tools.py`
- 4 MCP tools: `integration_akash_deploy`, `integration_bittensor_query`, `integration_fetch_discover`, `integration_nodes_status`

## Patterns to Follow

### File Structure
```
src/integrations/
  __init__.py
  tools.py              # MCP tool definitions + register()
  models.py             # Pydantic models for all integrations
  service.py            # Orchestration layer (routes to correct adapter)
  adapters/
    __init__.py
    base.py             # Abstract BaseIntegrationAdapter
    akash.py            # Akash Network adapter
    bittensor.py        # Bittensor adapter
    fetch.py            # Fetch.ai adapter
    nodes.py            # Nodes.ai adapter
```

### Adapter Pattern
```python
from abc import ABC, abstractmethod

class BaseIntegrationAdapter(ABC):
    """Base class for all external service adapters."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the external service is reachable."""
        ...

    @abstractmethod
    async def execute(self, action: str, params: dict) -> dict:
        """Execute an action against the external service."""
        ...
```

### Tool Pattern
```python
@server.tool(name="integration_akash_deploy")
async def akash_deploy(sdl: str, max_price: float) -> str:
    """Deploy a workload to Akash Network.

    Args:
        sdl: Stack Definition Language YAML for the deployment
        max_price: Maximum price in AKT per block
    """
    try:
        adapter = AkashAdapter(config)
        result = await adapter.execute("deploy", {"sdl": sdl, "max_price": max_price})
        return tool_success(result)
    except TimeoutError:
        return tool_error("TIMEOUT", "Akash deployment timed out after 30s", "Retry or check Akash network status")
```
