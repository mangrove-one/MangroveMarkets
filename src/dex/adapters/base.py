"""Abstract base class for DEX venue adapters."""
from abc import ABC, abstractmethod

from src.dex.models import Quote, Swap, SwapStatus, TradingPair


class BaseDexAdapter(ABC):
    """Interface that every DEX venue adapter must implement."""

    venue_id: str
    chain: str

    @abstractmethod
    async def get_pairs(self) -> list[TradingPair]:
        """Return all tradeable pairs on this venue."""
        ...

    @abstractmethod
    async def get_quote(self, input_token: str, output_token: str, amount: float) -> Quote:
        """Get a price quote for a swap."""
        ...

    @abstractmethod
    async def execute_swap(self, quote: Quote, wallet_seed: str) -> Swap:
        """Execute a swap using a quote."""
        ...

    @abstractmethod
    async def get_swap_status(self, tx_hash: str) -> SwapStatus:
        """Check the status of a submitted swap."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the venue is reachable and operational."""
        ...
