"""Shared Pydantic base types used across all domains."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class MangroveBaseModel(BaseModel):
    """Base model for all MangroveMarkets Pydantic models."""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class Category(str, Enum):
    """Top-level marketplace listing categories."""
    DATA = "data"
    COMPUTE = "compute"
    INTELLIGENCE = "intelligence"
    MODELS = "models"
    APIS = "apis"
    STORAGE = "storage"
    IDENTITY = "identity"
    MEDIA = "media"
    CODE = "code"
    OTHER = "other"


class PaginatedResponse(MangroveBaseModel):
    """Standard paginated response shape."""
    items: list[Any]
    total_count: int
    next_cursor: Optional[str] = None


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)
