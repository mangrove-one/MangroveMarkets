import pytest

from src.dex.errors import NoQuotesAvailableError
from src.dex.service import DexService


@pytest.mark.asyncio
async def test_supported_venues_include_minimum():
    service = DexService()
    venues = await service.supported_venues()
    venue_ids = {venue.id for venue in venues}
    assert {"xpmarket", "uniswap-v3", "jupiter"}.issubset(venue_ids)


@pytest.mark.asyncio
async def test_supported_pairs_include_wbtc_routes():
    service = DexService()
    uniswap_pairs = await service.supported_pairs("uniswap-v3")
    jupiter_pairs = await service.supported_pairs("jupiter")

    uniswap_tokens = {(pair.base_token, pair.quote_token) for pair in uniswap_pairs}
    jupiter_tokens = {(pair.base_token, pair.quote_token) for pair in jupiter_pairs}

    assert ("WBTC", "ETH") in uniswap_tokens or ("ETH", "WBTC") in uniswap_tokens
    assert ("WBTC", "SOL") in jupiter_tokens or ("SOL", "WBTC") in jupiter_tokens


@pytest.mark.asyncio
async def test_xpmarket_quote_applies_mangrove_fee():
    service = DexService()
    quote = await service.get_quote("XRP", "USDC", 100)

    assert quote.venue_id == "xpmarket"
    assert quote.mangrove_fee == pytest.approx(0.05)
    assert quote.total_cost == pytest.approx(100 + quote.venue_fee + quote.mangrove_fee)


@pytest.mark.asyncio
async def test_quote_for_unavailable_pair_raises():
    service = DexService()
    with pytest.raises(NoQuotesAvailableError):
        await service.get_quote("ABC", "DEF", 10)
