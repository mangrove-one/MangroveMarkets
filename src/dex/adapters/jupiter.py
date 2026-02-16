"""Jupiter adapter (Solana devnet) — stubbed for now."""
import os

from src.dex.adapters.base import BaseDexAdapter
from src.dex.errors import VenueNotSupportedError
from src.dex.models import Quote, Swap, SwapStatus, TradingPair


class JupiterAdapter(BaseDexAdapter):
    """Jupiter adapter with Solana devnet placeholders."""

    venue_id = "jupiter"
    name = "Jupiter"
    chain = "solana-devnet"
    fee_percent = 0.002  # illustrative

    def __init__(self) -> None:
        self._api_url = os.getenv("JUPITER_DEVNET_API_URL", "https://quote-api.jup.ag/v6")
        self._pairs = [
            TradingPair(venue_id=self.venue_id, base_token="SOL", quote_token="USDC"),
            TradingPair(venue_id=self.venue_id, base_token="WBTC", quote_token="SOL"),
            TradingPair(venue_id=self.venue_id, base_token="WBTC", quote_token="USDC"),
        ]

    async def get_pairs(self) -> list[TradingPair]:
        return list(self._pairs)

    async def get_quote(self, input_token: str, output_token: str, amount: float) -> Quote:
        raise VenueNotSupportedError("Jupiter devnet quoting is not yet supported")

    async def execute_swap(self, quote: Quote, wallet_seed: str) -> Swap:
        raise VenueNotSupportedError("Jupiter devnet swaps are not yet supported")

    async def get_swap_status(self, tx_hash: str) -> SwapStatus:
        return SwapStatus.PENDING

    async def health_check(self) -> bool:
        return bool(self._api_url)
