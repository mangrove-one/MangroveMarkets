"""Pydantic models for the Mangrove Marketplace."""
from datetime import datetime
from enum import Enum
from typing import Optional

from src.shared.types import Category, MangroveBaseModel, utc_now


class ListingType(str, Enum):
    STATIC = "static"
    SERVICE = "service"


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    OFFERED = "offered"
    ESCROWED = "escrowed"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    RATED = "rated"
    CANCELLED = "cancelled"


class OfferStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Listing(MangroveBaseModel):
    id: str
    seller_address: str
    title: str
    description: str
    category: Category
    subcategory: Optional[str] = None
    price_xrp: float
    listing_type: ListingType
    storage_uri: Optional[str] = None
    content_hash: Optional[str] = None
    status: ListingStatus = ListingStatus.ACTIVE
    tags: list[str] = []
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = utc_now()
        if data.get("updated_at") is None:
            data["updated_at"] = utc_now()
        super().__init__(**data)


class Offer(MangroveBaseModel):
    id: str
    listing_id: str
    buyer_address: str
    amount_xrp: float
    status: OfferStatus = OfferStatus.PENDING
    escrow_sequence: Optional[int] = None
    escrow_condition: Optional[str] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = utc_now()
        super().__init__(**data)


class Rating(MangroveBaseModel):
    id: str
    listing_id: str
    rater_address: str
    rated_address: str
    role: str  # "buyer" or "seller"
    score: int  # 1-5
    comment: Optional[str] = None
    created_at: datetime = None

    def __init__(self, **data):
        if data.get("created_at") is None:
            data["created_at"] = utc_now()
        super().__init__(**data)
