"""Pydantic models for the Mangrove DEX Aggregator."""
from datetime import datetime
from enum import Enum
from typing import Optional

from src.shared.types import MangroveBaseModel, utc_now


class VenueStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class SwapStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class Venue(MangroveBaseModel):
    id: str
    name: str
    chain: str
    status: VenueStatus = VenueStatus.ACTIVE
    supported_pairs_count: int = 0
    fee_percent: float = 0.0


class TradingPair(MangroveBaseModel):
    venue_id: str
    base_token: str
    quote_token: str
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    is_active: bool = True


class Quote(MangroveBaseModel):
    quote_id: str
    venue_id: str
    input_token: str
    output_token: str
    input_amount: float
    output_amount: float
    exchange_rate: float
    price_impact_percent: float = 0.0
    venue_fee: float = 0.0
    mangrove_fee: float = 0.0
    total_cost: float = 0.0
    expires_at: Optional[datetime] = None


class Swap(MangroveBaseModel):
    swap_id: str
    quote_id: str
    venue_id: str
    input_token: str
    output_token: str
    input_amount: float
    output_amount: float
    status: SwapStatus = SwapStatus.PENDING
    tx_hash: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    confirmed_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = utc_now()
        super().__init__(**data)
