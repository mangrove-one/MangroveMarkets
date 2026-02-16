"""DEX routing logic to select best venue quotes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.dex.adapters import BaseDexAdapter, JupiterAdapter, UniswapV3Adapter, XPMarketAdapter
from src.dex.errors import DexError, NoQuotesAvailableError, VenueNotFoundError
from src.dex.models import Quote, TradingPair, Venue, VenueStatus


MANGROVE_FEE_PERCENT = 0.0005


@dataclass
class DexRouter:
    adapters: list[BaseDexAdapter]

    async def list_venues(self) -> list[Venue]:
        venues: list[Venue] = []
        for adapter in self.adapters:
            pairs = await adapter.get_pairs()
            venues.append(
                Venue(
                    id=adapter.venue_id,
                    name=getattr(adapter, "name", adapter.venue_id),
                    chain=adapter.chain,
                    status=VenueStatus.ACTIVE,
                    supported_pairs_count=len(pairs),
                    fee_percent=getattr(adapter, "fee_percent", 0.0),
                )
            )
        return venues

    async def list_pairs(self, venue_id: str) -> list[TradingPair]:
        adapter = self._get_adapter(venue_id)
        return await adapter.get_pairs()

    async def get_best_quote(
        self,
        input_token: str,
        output_token: str,
        amount: float,
        venue_id: str | None = None,
    ) -> Quote:
        if venue_id:
            adapter = self._get_adapter(venue_id)
            quote = await adapter.get_quote(input_token, output_token, amount)
            return self._apply_mangrove_fee(quote)

        quotes: list[Quote] = []
        for adapter in self.adapters:
            try:
                quote = await adapter.get_quote(input_token, output_token, amount)
            except DexError:
                continue
            quotes.append(self._apply_mangrove_fee(quote))

        if not quotes:
            raise NoQuotesAvailableError(input_token, output_token)

        return max(quotes, key=lambda q: q.output_amount)

    def _get_adapter(self, venue_id: str) -> BaseDexAdapter:
        for adapter in self.adapters:
            if adapter.venue_id == venue_id:
                return adapter
        raise VenueNotFoundError(venue_id)

    @staticmethod
    def _apply_mangrove_fee(quote: Quote) -> Quote:
        mangrove_fee = quote.input_amount * MANGROVE_FEE_PERCENT
        quote.mangrove_fee = mangrove_fee
        quote.total_cost = quote.input_amount + quote.venue_fee + mangrove_fee
        return quote


def get_default_router(adapters: Iterable[BaseDexAdapter] | None = None) -> DexRouter:
    if adapters is None:
        adapters = [XPMarketAdapter(), UniswapV3Adapter(), JupiterAdapter()]
    return DexRouter(list(adapters))
