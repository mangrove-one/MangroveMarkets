"""Uniswap v3 adapter (Sepolia) — stubbed for now."""
import os

from src.dex.adapters.base import BaseDexAdapter
from src.dex.errors import VenueNotSupportedError
from src.dex.models import Quote, Swap, SwapStatus, TradingPair


class UniswapV3Adapter(BaseDexAdapter):
    """Uniswap v3 adapter with Sepolia configuration placeholders."""

    venue_id = "uniswap-v3"
    name = "Uniswap v3"
    chain = "ethereum-sepolia"
    fee_percent = 0.003  # 0.30% typical v3 pool fee

    def __init__(self) -> None:
        self._rpc_url = os.getenv("SEPOLIA_RPC_URL", "")
        self._pairs = [
            TradingPair(venue_id=self.venue_id, base_token="ETH", quote_token="USDC"),
            TradingPair(venue_id=self.venue_id, base_token="WBTC", quote_token="ETH"),
            TradingPair(venue_id=self.venue_id, base_token="WBTC", quote_token="USDC"),
        ]

    async def get_pairs(self) -> list[TradingPair]:
        return list(self._pairs)

    async def get_quote(self, input_token: str, output_token: str, amount: float) -> Quote:
        raise VenueNotSupportedError("Uniswap v3 Sepolia quoting is not yet supported")

    async def execute_swap(self, quote: Quote, wallet_seed: str) -> Swap:
        raise VenueNotSupportedError("Uniswap v3 Sepolia swaps are not yet supported")

    async def get_swap_status(self, tx_hash: str) -> SwapStatus:
        return SwapStatus.PENDING

    async def health_check(self) -> bool:
        return bool(self._rpc_url) if self._rpc_url else True
