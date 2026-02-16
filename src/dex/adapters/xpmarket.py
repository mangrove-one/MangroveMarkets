"""XPMarket adapter (XRPL testnet)."""
from __future__ import annotations

import os
from uuid import uuid4

from src.dex.adapters.base import BaseDexAdapter
from src.dex.errors import VenueNotSupportedError
from src.dex.models import Quote, Swap, SwapStatus, TradingPair


class XPMarketAdapter(BaseDexAdapter):
    """XRPL XPMarket adapter using testnet-only configuration.

    This adapter currently returns deterministic quotes and pairs for testnet
    until on-ledger integration is completed.
    """

    venue_id = "xpmarket"
    name = "XPMarket"
    chain = "xrpl-testnet"
    fee_percent = 0.001  # 0.10% venue fee (illustrative)

    def __init__(self) -> None:
        self._xrpl_testnet_rpc = os.getenv("XRPL_TESTNET_RPC_URL", "https://s.altnet.rippletest.net:51234")
        self._pairs = [
            TradingPair(
                venue_id=self.venue_id,
                base_token="XRP",
                quote_token="USDC",
                min_amount=1.0,
                max_amount=1_000_000.0,
            ),
            TradingPair(
                venue_id=self.venue_id,
                base_token="XRP",
                quote_token="USD",
                min_amount=1.0,
                max_amount=1_000_000.0,
            ),
        ]
        self._rates = {
            ("XRP", "USDC"): 0.50,
            ("XRP", "USD"): 0.50,
        }

    async def get_pairs(self) -> list[TradingPair]:
        return list(self._pairs)

    async def get_quote(self, input_token: str, output_token: str, amount: float) -> Quote:
        rate = self._rates.get((input_token, output_token))
        if rate is None:
            reverse_rate = self._rates.get((output_token, input_token))
            if reverse_rate is None:
                raise VenueNotSupportedError(
                    f"XPMarket does not support pair {input_token}/{output_token} on testnet",
                )
            rate = 1 / reverse_rate

        venue_fee = amount * self.fee_percent
        effective_input = amount - venue_fee
        output_amount = effective_input * rate
        exchange_rate = output_amount / amount if amount else 0.0

        return Quote(
            quote_id=f"xpmarket-{uuid4().hex}",
            venue_id=self.venue_id,
            input_token=input_token,
            output_token=output_token,
            input_amount=amount,
            output_amount=output_amount,
            exchange_rate=exchange_rate,
            venue_fee=venue_fee,
        )

    async def execute_swap(self, quote: Quote, wallet_seed: str) -> Swap:
        raise VenueNotSupportedError("XPMarket swap execution is not yet wired for testnet")

    async def get_swap_status(self, tx_hash: str) -> SwapStatus:
        return SwapStatus.PENDING

    async def health_check(self) -> bool:
        return bool(self._xrpl_testnet_rpc)
