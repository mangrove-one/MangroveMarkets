"""Pydantic models for market intelligence."""
from typing import Optional

from src.shared.types import MangroveBaseModel


class UsageInfo(MangroveBaseModel):
    calls_used: int = 0
    calls_remaining: int = 50
    tier: str = "free"


class CategorySummary(MangroveBaseModel):
    category: str
    listing_count: int = 0
    volume_xrp: float = 0.0


class MarketOverview(MangroveBaseModel):
    time_window: str
    total_listings: int = 0
    active_listings: int = 0
    total_transactions: int = 0
    total_volume_xrp: float = 0.0
    average_price_xrp: float = 0.0
    top_categories: list[CategorySummary] = []
    usage: Optional[UsageInfo] = None
