"""Pydantic models for wallet management."""
from datetime import datetime
from typing import Optional

from src.shared.types import MangroveBaseModel


class WalletInfo(MangroveBaseModel):
    address: str
    secret: Optional[str] = None  # Only returned on creation
    seed_phrase: Optional[str] = None
    balance_xrp: float = 0.0
    reserve_xrp: float = 10.0
    available_xrp: float = 0.0
    is_funded: bool = False
    network: str = "testnet"


class Transaction(MangroveBaseModel):
    tx_hash: str
    tx_type: str
    from_address: str
    to_address: Optional[str] = None
    amount_xrp: Optional[float] = None
    status: str = ""
    timestamp: Optional[datetime] = None
    fee_xrp: float = 0.0
