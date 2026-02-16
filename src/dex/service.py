"""Business logic for DEX operations."""
from __future__ import annotations

from src.dex.errors import DexError
from src.dex.models import Quote, TradingPair, Venue
from src.dex.router import DexRouter, get_default_router


class DexService:
    """High-level DEX service wrapper used by MCP tools."""

    def __init__(self, router: DexRouter | None = None) -> None:
        self.router = router or get_default_router()

    async def supported_venues(self) -> list[Venue]:
        return await self.router.list_venues()

    async def supported_pairs(self, venue_id: str) -> list[TradingPair]:
        return await self.router.list_pairs(venue_id)

    async def get_quote(
        self,
        input_token: str,
        output_token: str,
        amount: float,
        venue_id: str | None = None,
    ) -> Quote:
        return await self.router.get_best_quote(input_token, output_token, amount, venue_id=venue_id)

    async def swap(self, quote_id: str, wallet_seed: str) -> str:
        raise DexError("NOT_IMPLEMENTED", "Swap execution not yet available", "Coming soon")

    async def swap_status(self, swap_id: str) -> str:
        raise DexError("NOT_IMPLEMENTED", "Swap status not yet available", "Coming soon")
